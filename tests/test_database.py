
from tempfile import TemporaryDirectory
import unittest
import logging

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger("test")

from src.database import Database, DatabaseItem, DatabaseStatus

def get_item_id ( nid : int ):
    return "ID%04d" % nid
def make_item( nid : int , desc=""):
    return DatabaseItem.from_new_data( get_item_id(nid), {"nid":nid, "desc": desc})


class Test(unittest.TestCase):

    def tearDown(self):
        self.TMPDIR_OBJ.cleanup()

    def setUp(self):
        LOG.info("====================================================")
        LOG.info("=== Starting test: %s ", self._testMethodName)
        LOG.info("====================================================")

        self.TMPDIR_OBJ = TemporaryDirectory()
        self.TMPDIR = self.TMPDIR_OBJ.name
        self.db = Database(basepath=self.TMPDIR)
        self.make_structure()

    def _make_old_stuff(self):
        return [make_item(101 + loop, "Very old stuff %d" % loop) for loop in range(5)]
    def make_structure(self):
        # Ok first make old items

        items =  self._make_old_stuff()
        items += [make_item(501 + loop, "Old filtered %d" % loop) for loop in range(5)]
        
        self.db.items_classify(items)

        for item in items:
            print(item)
            if item.data["nid"] >= 500 and item.data["nid"] < 600:
                item.status = DatabaseStatus.FILTERED
        self.db.items_save(items)

        # allright, then new items appear
        items = [make_item(201 + loop, "Existing stuff %d" % loop) for loop in range(5)]
        self.db.items_classify(items)
        self.db.items_save(items)

    def test_0_basic(self):
        # Ok, now lets see that classification works.
        items = [make_item(201 + loop, "Existing stuff %d" % loop) for loop in range(2)]
        items += [make_item(301 + loop, "New stuff %d" % loop) for loop in range(5)]
        items += [make_item(501, "Should be filtered")]
        items += [make_item(551 + loop, "New filteted %d" % loop) for loop in range(5)]
        self.db.items_classify(items)
        #print(items)

        for item in items:
            if item.data["nid"] > 200 and item.data["nid"] < 203:
                # These should be existing
                self.assertEqual(item.status, DatabaseStatus.EXISTING)
            elif item.data["nid"] < 300:
                self.assertEqual(item.status, DatabaseStatus.GONE)
            elif item.data["nid"] > 300 and item.data["nid"] < 400:
                self.assertEqual(item.status, DatabaseStatus.NEW)
            elif item.data["nid"] > 500 and item.data["nid"] < 550:
                self.assertEqual(item.status, DatabaseStatus.FILTERED)
            elif item.data["nid"] > 550 and item.data["nid"] < 600:
                self.assertEqual(item.status, DatabaseStatus.NEW)
                item.filter()
        self.db.items_save( items )
        LOG.info("OK, check that double filtered")

        items = [make_item(551 + loop, "Should be filteted %d" % loop) for loop in range(5)]
        self.db.items_classify(items)
        #print(items)
        for item in items:
            if item.data["nid"] > 550 and item.data["nid"] < 600:
                self.assertEqual(item.status, DatabaseStatus.FILTERED)
            else:
                self.assertEqual(item.status, DatabaseStatus.GONE)   

    def test_1_re_appear(self):
        items = []
        self.db.items_classify(items)
        self.db.items_save( items )
        print(items)

        items =  self._make_old_stuff()
        self.db.items_classify(items)
        self.db.items_save( items )
        print(items)

        items = []
        self.db.items_classify(items)
        self.db.items_save( items )
        print(items)

if __name__ == '__main__':
    unittest.main()
