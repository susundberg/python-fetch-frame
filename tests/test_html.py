
from tempfile import NamedTemporaryFile
import unittest
import logging

from src.html import HtmlItem, HtmlOutput

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger("test.html")

class TestItem( HtmlItem ):
    FORMATS = { "desc": lambda x: "CALLED %s" % x }

    @staticmethod
    def sorted_key( obj ) -> str:
        return str(obj.data["nid"])

def make_item( x : int ):
    return TestItem( {"nid" : x , "desc" : "Foo bar %03d" % x })

class Test(unittest.TestCase):

#    def tearDown(self):
#        self.TMP.cleanup()

    def setUp(self):
        self.TMP = NamedTemporaryFile()
        self.html = HtmlOutput( self.TMP.name, header=["desc","nid"] )

    def test_0_basic(self):
        self.html.prepare()
        self.html.make_table( "New items", [ make_item( x ) for x in range(5 )])
        self.html.finish()
        with open( self.TMP.name ) as fid:
            LOG.info( fid.read() )


if __name__ == '__main__':
    unittest.main()
