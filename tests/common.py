
import pathlib
from tempfile import TemporaryDirectory
import unittest
import logging

LOG = logging.getLogger("test.common")

class TestBase(unittest.TestCase):

    def tearDown(self):
        self.TMPDIR_OBJ.cleanup()

    def setUp(self):
        LOG.info("====================================================")
        LOG.info("=== Starting test: %s ", self._testMethodName)
        LOG.info("====================================================")

        self.TMPDIR_OBJ = TemporaryDirectory()
        self.TMPDIR = pathlib.Path( self.TMPDIR_OBJ.name )

