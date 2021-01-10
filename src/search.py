import typing
import abc
import logging


LOG = logging.getLogger("frame.search")


class Search(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def list_items(self) -> typing.List[ typing.Any ]:
        pass

    @abc.abstractmethod
    def details( self, items: typing.List[ typing.Any ] ):
        pass


