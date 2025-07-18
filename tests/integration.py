import auto_tesseract as main

import shutil
import os
import tempfile
import unittest


TEST_PDF = 'testdata/thisisasamplepdf.pdf'
TESSERACT_BIN = '/usr/bin/tesseract'
CONVERT_BIN = '/usr/bin/convert'


def _binaries_present() -> bool:
  mode = os.R_OK | os.X_OK
  return os.access(TESSERACT_BIN, mode) and os.access(CONVERT_BIN, mode)


class TestMain(unittest.TestCase):
  def setUp(self):
    self.in_dir = tempfile.TemporaryDirectory()
    self.out_dir = tempfile.TemporaryDirectory()
    self.runner = main.TesseractRunner(
      CONVERT_BIN, TESSERACT_BIN, self.in_dir.name, self.out_dir.name)

  def tearDown(self):
    self.in_dir.cleanup()
    self.out_dir.cleanup()

  @unittest.skipUnless(_binaries_present(),
    'tesseract and/or convert binaries not found')
  def testRun(self):
    shutil.copy(TEST_PDF, self.in_dir.name)
    filename = os.path.basename(TEST_PDF)

    result = self.runner.RunOne(filename)
    self.assertTrue(result)
    self.assertTrue(os.access(
      os.path.join(self.out_dir.name, filename), os.R_OK))


if __name__ == '__main__':
    unittest.main()
