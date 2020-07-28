from abc import ABCMeta, abstractmethod
from typing import Optional, Set, Dict
from pyroaring import FrozenBitMap
from bidict import bidict
from ..models.Namespace import Namespace


class Graph(metaclass=ABCMeta):
    """
    Interface for an graph object where classes are integer encoded
    and contains methods for traversing ancestors, descendants, and storing
    information content about classes
    """
    root: str
    id_map: bidict  # Dict[str, int]
    namespace_map: Dict[Namespace, FrozenBitMap]
    is_ordered: bool

    @abstractmethod
    def get_descendants(self, node: str) -> FrozenBitMap:
        pass

    @abstractmethod
    def get_ancestors(self,  node: str) -> FrozenBitMap:
        pass

    def get_closure(self, node: str, negative: Optional[bool] = False) -> FrozenBitMap:
        if negative:
            nodes = self.get_descendants(node)
        else:
            nodes = self.get_ancestors(node)
        return nodes
