import main

import shutil
import os
import subprocess
import tempfile
import unittest
import unittest.mock


TEST_PDF = 'testdata/thisisasamplepdf.pdf'


class TestMain(unittest.TestCase):
  def setUp(self):
    self.in_dir = tempfile.TemporaryDirectory()
    self.out_dir = tempfile.TemporaryDirectory()
    self.runner = main.TesseractRunner(
      '/convert', '/tesseract', self.in_dir.name, self.out_dir.name)

  def tearDown(self):
    self.in_dir.cleanup()
    self.out_dir.cleanup()

  def testCanHandle(self):
    self.assertTrue(self.runner.CanHandle('foo.pdf'))
    self.assertFalse(self.runner.CanHandle('foo.doc'))

  def testMissingFiles(self):
    self.assertEqual(0, len(self.runner.MissingFiles()))

    shutil.copy(TEST_PDF, self.in_dir.name)
    missing = self.runner.MissingFiles()
    self.assertEqual(1, len(missing))
    self.assertEqual(os.path.basename(TEST_PDF), missing[0])

    shutil.copy(TEST_PDF, self.out_dir.name)
    self.assertEqual(0, len(self.runner.MissingFiles()))

  def testFileSizeChanging(self):
    sleep_fn = lambda x: True

    self.assertEqual(False,
      main.file_size_changing(TEST_PDF, sleep_fn=sleep_fn))

    with unittest.mock.patch('os.stat') as mock_stat:
      base_stat_result = os.stat(TEST_PDF)
      changed = os.stat_result(
        (0, 0, 0, 0, 0, 0, base_stat_result.st_size + 100, 0, 0, 0))

      mock_stat.side_effect = [base_stat_result, changed]
      self.assertEqual(True,
        main.file_size_changing(TEST_PDF, sleep_fn=sleep_fn))

  def testRunOne(self):
    shutil.copy(TEST_PDF, self.in_dir.name)
    with unittest.mock.patch('subprocess.run') as mock_run:
      result = self.runner.RunOne(os.path.basename(TEST_PDF))

      calls = mock_run.mock_calls
      self.assertEqual(calls[0].args[0][0], '/convert')
      self.assertEqual(calls[1].args[0][0], '/tesseract')
      self.assertTrue(result)

    with unittest.mock.patch('subprocess.run') as mock_run:
      mock_run.side_effect = subprocess.CalledProcessError(1, 'foo')

      result = self.runner.RunOne(os.path.basename(TEST_PDF))
      mock_run.assert_called_once()
      self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
