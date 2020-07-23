from typing import Dict
from pyroaring import FrozenBitMap
from .Graph import Graph
from ..models.Namespace import Namespace


class CacheGraph(Graph):
    """
    A graph implementation that caches ancestors and descendants
    as BitMaps using pyroaring
    (previously done with sets of ints)
    """

    def __init__(
            self,
            root: str,
            id_map: Dict[str, int],
            ancestors: Dict[str, FrozenBitMap],
            descendants: Dict[str, FrozenBitMap],
            namespace_map: Dict[Namespace, FrozenBitMap] = None,
            is_ordered: bool = False
    ):
        """

        :param root: Root of the ontology (UPHENO:0001001, HP:0000118)
        :param id_map: dictionary of curie id (key) to integer encoded id (value)
        :param ancestors: dictionary of curie id (key) and frozen bitmap,
                          created from an array of integers for its ancestors
                          self included (reflexive closure)
        :param descendants: dictionary of curie id (key) and frozen bitmap,
                            created from an array of integers for its descendants
                            (self included)
        :param namespaces: dictionary of namespace (key) and frozen bitmap,
                           created from an array of integers of all ids in
                           the namespace
        :param is_ordered: {default=False} True if integers are sorted in ascending
                           order
        """
        self.root = root
        self.id_map = id_map
        self.ancestors = ancestors
        self.descendants = descendants
        self.is_ordered = is_ordered
        self.ic_map = {}

    def get_ancestors(self, node: str) -> FrozenBitMap:
        try:
            nodes = self.ancestors[node]
        except KeyError:
            # TODO handle
            nodes = FrozenBitMap()
        return nodes

    def get_descendants(self, node: str) -> FrozenBitMap:
        try:
            nodes = self.descendants[node]
        except KeyError:
            # TODO handle
            nodes = FrozenBitMap()
        return nodes
