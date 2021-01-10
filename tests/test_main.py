

import logging
import time
import typing
import unittest
import bs4

from src.main import main
from src.database import Database, DatabaseItem
from src.search import Search
from src.html import HtmlOutput, HtmlItem

from tests.common import TestBase
LOG = logging.getLogger("test")


class DataItem(DatabaseItem, HtmlItem):

    @staticmethod
    def sorted_key(obj) -> str:
        return obj.id

    @classmethod
    def create_from_new_data( cls, data ):
        ret = DataItem()
        ret.from_new_data( data ) 
        return ret

    @classmethod
    def create_from_load_data( cls, data  ):
        ret = DataItem()
        ret.from_load_data( data ) 
        return ret

        


class SearchSim(Search):
    LOOP_START = 1
    LOOP_END = 10

    FORMATS = {"detail": lambda x: int(x) % 64}

    def list_items(self) -> typing.List[typing.Any]:

        to_ret = [DataItem.create_from_new_data( {"_id":"ID%04d" % loop, "secret": "Fresh", "number": loop})
                  for loop in range(SearchSim.LOOP_START, SearchSim.LOOP_END)]
        LOG.info("Search from %d -> %d", SearchSim.LOOP_START, SearchSim.LOOP_END)
        SearchSim.LOOP_START += 4
        SearchSim.LOOP_END += 4
        return to_ret

    def details(self, items: typing.List[typing.Any]):
        for item in items:
            LOG.info("Search for detail %s", item )
            if item.data["number"] % 2 == 0:
                item.filter()
            item.data["detail"] = time.time()


def cat_file(fn):
    with open(fn) as fid:
        LOG.info("%s", fid.read())



class Test(TestBase):
    def check_file( self, fn, items_to_check ):
        with open(fn) as fid:
            html = bs4.BeautifulSoup( fid.read(), "lxml" )

        for to_check_table, to_check_ids in items_to_check.items():
            LOG.info("Check that table '%s' contains %s", to_check_table, to_check_ids )
            print(html)
            table = html.find( id=to_check_table )
            self.assertIsNotNone( table )
            for ids in to_check_ids:
                tr = table.find( id = ids )
                self.assertIsNotNone( tr  )
                LOG.info("Found: %s", tr)

    def test_0(self):
        db = Database(self.TMPDIR, DataItem)
        html = HtmlOutput(self.TMPDIR / "out.html", ["secret", "_id", "detail"])
        search = SearchSim()
        
        for loop in range(4):
            LOG.info("-------- LOOP %d -------", loop)
            main(db, search, html)
            cat_file(html.filename)
        
        to_check = { 
            "table_new"  : ["ID0019","ID0021"],
            "table_gone" : ["ID0009","ID0011"],
            "table_existing" : ["ID0013","ID0015", "ID0017"],
        }

        self.check_file( html.filename, to_check )
        


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
