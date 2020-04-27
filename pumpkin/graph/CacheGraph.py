from typing import Dict
from pyroaring import FrozenBitMap
from .Graph import Graph


class CacheGraph(Graph):
    """
    A graph implementation that caches ancestors and descendants
    as BitMaps using pyroaring
    (previously done with sets of strings)
    """

    def __init__(
            self,
            root: str,
            id_map: Dict[str, int],
            ancestors: Dict[str, FrozenBitMap],
            descendants: Dict[str, FrozenBitMap],
            is_ordered: bool = False
    ):
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
