#!/usr/bin/python3
"""Creates a text-searchable PDF from a regular PDF.

This is intended to be used with document scanners that output PDFs. A PDF
written into --in_dir will be automatically processed through an OCR engine,
then a searchable file of the same name will be written into --out_dir.

This tool relies on:
  (1) Tesseract (open-source OCR)
  (2) ImageMagick (to convert PDF into TIFF for Tesseract input)

This code also relies on Linux's inotify API in order to automatically detect
incoming files.
"""

import argparse
import concurrent.futures
import functools
import logging
import os
import subprocess
import sys
import tempfile
import time

from typing import List, Tuple

import inotify.adapters     # type: ignore[import]


def file_size_changing(f: str, wait_time_secs=15, sleep_fn=time.sleep) -> bool:
  """Returns True if a file's size has changed in wait_time_secs."""
  try:
    st = os.stat(f)
    sleep_fn(wait_time_secs)
    return st.st_size != os.stat(f).st_size
  except FileNotFoundError:
    # In case the file moved in between.
    return True


class TesseractRunner:
  def __init__(self, convert_bin: str, tesseract_bin: str, in_dir: str,
               out_dir: str):
    self._convert_bin = convert_bin
    self._tesseract_bin = tesseract_bin
    self._in_dir = in_dir
    self._out_dir = out_dir

  def MissingFiles(self) -> List[str]:
    """Files present in in_dir that have no corresponding match in out_dir."""
    i = set(os.listdir(self._in_dir))
    o = set(os.listdir(self._out_dir))
    return list(i-o)

  def CanHandle(self, filename) -> bool:
    return filename.endswith('.pdf')

  def RunOne(self, filename: str) -> bool:
    in_file = os.path.join(self._in_dir, filename)
    out_file = os.path.join(self._out_dir, filename)

    logging.info('Processing: %s', in_file)
    success, output = self._Run(in_file, out_file)

    if success:
      logging.info('Successfully completed: %s', in_file)
    else:
      logging.error('Errors processing %s: %s', in_file, output)

    return success

  def RunMissed(self, filename: str) -> bool:
    if file_size_changing(os.path.join(self._in_dir, filename)):
      logging.info('File %s still getting written to, ignoring until complete')
      return False
    else:
      return self.RunOne(filename)

  def _Run(self, in_pdf: str, out_pdf: str) -> Tuple[bool, str]:
    with tempfile.NamedTemporaryFile(prefix="autotess", suffix=".tiff") as tf:
      convert_args = [self._convert_bin,
        '-density', '300',
        in_pdf,
        '-depth', '8',
        '-strip',
        '-background', 'white',
        '-alpha', 'off',
        tf.name]

      tesseract_args = [self._tesseract_bin, tf.name, out_pdf[0:-4], 'pdf']

      try:
        logging.info('Running: %s', convert_args)
        out = subprocess.run(convert_args, check=True, capture_output=True)

        logging.info('Running: %s', tesseract_args)
        out = subprocess.run(tesseract_args, check=True, capture_output=True)
      except subprocess.CalledProcessError as e:
        logging.error('Run failed: code=%d output=%s', e.returncode, e.output)
        return False, str(e.output)

      return True, ''


def main(argv):
  parser = argparse.ArgumentParser(prog=argv[0])
  parser.add_argument('--in_dir', type=str, help='Input directory', default='output')
  parser.add_argument('--out_dir', type=str, help='Output directory', default='output/ocr')
  parser.add_argument('--convert_bin', type=str, help='Path to convert tool', default='/usr/bin/convert')
  parser.add_argument('--tesseract_bin', type=str, help='Path to Tesseract tool', default='/usr/bin/tesseract')
  args = parser.parse_args()

  logging.basicConfig(
      format='%(asctime)s [%(threadName)10s] %(levelname)8s %(message)s',
      datefmt='%Y/%m/%d %H:%M:%S',
      level=logging.INFO)

  logging.info('Starting autotess..')
  logging.info('  in_dir        = %s', args.in_dir)
  logging.info('  out_dir       = %s', args.out_dir)
  logging.info('  convert_bin   = %s', args.convert_bin)
  logging.info('  tesseract_bin = %s', args.tesseract_bin)

  i = inotify.adapters.Inotify()
  i.add_watch(args.in_dir)

  runner = TesseractRunner(
    args.convert_bin, args.tesseract_bin, args.in_dir, args.out_dir)

  with concurrent.futures.ThreadPoolExecutor(
    max_workers=2, thread_name_prefix='worker') as executor:

    for filename in runner.MissingFiles():
      if runner.CanHandle(filename):
        logging.info('Submitting missing file for processing: %s', filename)
        executor.submit(runner.RunMissed, filename)

    for event in i.event_gen(yield_nones=False):
      (_, type_names, path, filename) = event

      if set(type_names) & set(['IN_CLOSE_WRITE', 'IN_MOVED_TO']):
        if runner.CanHandle(filename):
          logging.info('New file detected: %s', filename)
          executor.submit(runner.RunOne, filename)


if __name__ == '__main__':
  main(sys.argv)
