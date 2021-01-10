import abc
import typing
import logging

LOG = logging.getLogger("frame.html")


class HtmlItem:

    FORMATS = {}

    def __init__(self, data: typing.Dict[str, typing.Any]):
        self.data = data
        self.id = ""

    # @abc.abstractstaticmethod
    @staticmethod
    def sorted_key(_obj) -> str:
        return ""

    def get_value(self, key: str):
        try:
            data_value = self.data[key]
        except KeyError:
            LOG.error("Item %s is missing value for '%s'", self, key)
            return ""

        if key not in self.FORMATS:
            return str(data_value)

        return str(self.FORMATS[key](data_value))


class HtmlOutput(abc.ABC):

    def __init__(self, fn, header: typing.List[str]):
        self.filename = fn
        self.header = header
        self.fid = None

    def prepare(self):
        self.fid = open(self.filename, 'wb')
        LOG.info("Open html output to '%s'", self.filename)
        self.print("<html> <meta charset='UTF-8'> <head></head><body>")

    def make_table(self, title, items: typing.List[HtmlItem]):
        self.print('<h3> %s </h3>' % title)

        if len(items) == 0:
            self.print("<p> No items, srry :/ </p>")
            return

        self.print('<table border="1|0" id="table_%s">' % title.lower() )
        self.print("<tr><th>" + "</th><th>".join(self.header) + "</th></tr>")
        for item in sorted(items, key=items[0].sorted_key):
            self._output_item(item)
        self.print("</table>")

    def _output_item(self, item: HtmlItem):
        values = [ item.get_value(x) for x in self.header]
        self.print("<tr id=\"%s\"><td>" % item.id + "</td><td>".join(values) + "</td></tr>")

    def finish(self):
        self.print("</body></html>")
        self.fid.close()

    def print(self, item):
        self.fid.write(item.encode("utf-8") + b"\n")
