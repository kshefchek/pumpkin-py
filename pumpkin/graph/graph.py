from abc import ABCMeta, abstractmethod
from typing import Optional, Iterable, Dict
from pyroaring import FrozenBitMap, BitMap
from bidict import bidict
from ..models.namespace import Namespace


class Graph(metaclass=ABCMeta):
    """
    Interface for an graph object where classes are integer encoded
    and contains methods for traversing ancestors, descendants, and storing
    information content about classes
    """
    root: str
    id_map: bidict  # Dict[str, int]
    namespace_map: Dict[Namespace, FrozenBitMap]

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

    def get_profile_closure(
            self,
            profile: Iterable[str],
            negative: Optional[bool] = False
    ) -> BitMap:
        """
        Given a list of phenotypes, get the reflexive closure for each phenotype
        stored in a single set.  This can be used for jaccard similarity or
        simGIC

        This should probably be moved elsewhere as the loan fx here
        """
        return BitMap.union(
            *[self.get_closure(node, negative=negative)
              for node in profile]
        )
