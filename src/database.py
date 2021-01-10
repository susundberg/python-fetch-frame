

from pathlib import Path
import json
import gzip
import shutil
import typing
import abc
import logging
import enum

LOG = logging.getLogger("frame.db")


class DatabaseStatus(enum.Enum):
    NONE = "none"
    FILTERED = "filtered"
    NEW = "new"
    EXISTING = "existing"
    GONE = "gone"
    ARCHIVED = "archived"


DatabaseItemData = typing.Dict[str, typing.Any]

class DatabaseItem:
    def __init__(self, iid: str, status : DatabaseStatus, data: DatabaseItemData ):
        self.id = iid
        self.status = status
        self.modified = False
        self.data = data
    def __repr__(self):
        return "<DBItem %s %s -- %s>" % (self.id, self.status.value, self.data )

    def update_data( self ):
        self.data["_id"] = self.id
        self.data["_status"] = self.status.value
    
    def filter(self):
        self.modified = True
        self.status = DatabaseStatus.FILTERED


    @classmethod
    def from_new_data( cls, iid : str, data : DatabaseItemData ):
        return cls( iid=iid, status=DatabaseStatus.NONE, data=data ) 

    @classmethod
    def from_load_data( cls, data : DatabaseItemData ):
        return cls( iid=data["_id"], status=DatabaseStatus(data["_status"]), data=data ) 


class Database(abc.ABC):

    def __init__(self, basepath: str):
        self.path_act = Path(basepath) / Path("active")
        self.path_old = Path(basepath) / Path("old")
        self.path_filt = Path(basepath) / Path("filtered")

        for pat in [self.path_act, self.path_old, self.path_filt]:
            pat.mkdir(parents=True, exist_ok=True)
            LOG.info("Check database path %s", pat)

    def _itemset_from_path(self, pat):
        result = set()
        for fileitem in pat.iterdir():
            if fileitem.suffix == ".gzip":
                fn = fileitem.name.replace(".json.gzip", "")
                result.add(fn)
        return result

    def items_classify(self, items: typing.List[DatabaseItem]):
        # We need to classify all items -- for that
        #items_old = get_set_from_path(self.path_act)

        items_active_now = set([x.id for x in items])
        items_active_last = self._itemset_from_path(self.path_act)
        items_filtered = self._itemset_from_path(self.path_filt)

        LOG.debug("Active now: %s", items_active_now)
        LOG.debug("Active last: %s", items_active_last)
        LOG.debug("Filted:  %s", items_filtered)

        for item in items:

            if item.id in items_filtered:
                item.status = DatabaseStatus.FILTERED
                continue

            if item.id in items_active_last:
                item.status = DatabaseStatus.EXISTING
                continue

            item.status = DatabaseStatus.NEW
            item.modified = True

        for item_id in items_active_last - items_active_now:
            LOG.debug("Noticed item '%s' is gone", item_id)
            item = self._item_load(item_id, self.path_act)
            item.status = DatabaseStatus.GONE
            item.modified = True
            items.append(item)

        LOG.info("Item classification done!")

    def items_save(self, items: typing.List[DatabaseItem]):

        store_path = {DatabaseStatus.FILTERED: self.path_filt, DatabaseStatus.NEW: self.path_act}
        for item in items:
            if item.modified == False:
                continue

            if item.status == DatabaseStatus.FILTERED or item.status == DatabaseStatus.NEW:
                # Filtered that have have modified == new filtered -> save
                self._item_save(item, store_path[item.status])
            elif item.status == DatabaseStatus.GONE:
                # Gone items have disapeared from search results
                # -> move to archive
                self._item_move(item, self.path_act, self.path_old)
            else:
                LOG.error("Item: %s invalid modified + status %s", item.id, item.status)

    def _item_get_fn(self, item_id: str):
        return Path(str(item_id) + ".json.gzip")

    def _item_load(self, item_id: str, path: Path) -> DatabaseItem:
        fn = path / self._item_get_fn(item_id)
        LOG.debug("Load %s from '%s'", item_id, fn)
        with open(str(fn), 'rb') as fid:
            data = json.loads(gzip.decompress(fid.read()).decode("utf-8"))
            return DatabaseItem.from_load_data( data )

    def _item_save( self, item: DatabaseItem, path : Path ):
        fn = path / self._item_get_fn( item.id )
        item.update_data()
        json_content = json.dumps(item.data).encode("utf-8")
        LOG.debug("Save %s to '%s'", item.id, fn)
        with open(str(fn), 'wb') as fid:
            fid.write(gzip.compress(json_content))

    def _item_move(self, item, path_from : Path, path_to : Path ):
        fn = self._item_get_fn( item.id )
        fn_from = path_from / fn
        fn_to = path_to / fn
        LOG.debug("Move %s from '%s' to '%s'", item.id, fn_from, fn_to )
        shutil.move( str(fn_from), str(fn_to))
