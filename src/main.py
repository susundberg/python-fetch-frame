

import logging

from src.database import Database, DatabaseStatus
from src.search import Search
from src.html import HtmlOutput

LOG = logging.getLogger("frame.main")


def main(db: Database, search: Search, html: HtmlOutput):

    # First do generic serach
    html.prepare()
    LOG.info("Search for items..")
    items = search.list_items()
    LOG.info("Update status..")
    # Then update status of all items
    db.items_classify(items)
    # Then query details on new items
    LOG.info("Search for details ..")
    search.details([item for item in items if item.status == DatabaseStatus.NEW])
    LOG.info("Saving ..")
    db.items_save(items)
    # All done. prepare output

    def make_table_of_status(title, status):
        html.make_table(title, list(filter(lambda x: x.status == status, items)))

    make_table_of_status("New", DatabaseStatus.NEW)
    make_table_of_status("Gone", DatabaseStatus.GONE)
    make_table_of_status("Existing", DatabaseStatus.EXISTING)
    html.finish()

