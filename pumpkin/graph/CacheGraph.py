from typing import Set, Dict
from pyroaring import BitMap
from .Graph import Graph


class CacheGraph(Graph):
    """
    adsf
    """

    def __init__(
            self,
            root: str,
            id_map: Dict[str, int],
            ancestors: Dict[str, BitMap],
            descendants: Dict[str, BitMap]
    ):
        self.root = root
        self.id_map = id_map
        self.ancestors = ancestors
        self.descendants = descendants
        self.ic_map = {}

    def get_ancestors(self, node: str) -> BitMap:
        try:
            nodes = self.ancestors[node]
        except KeyError:
            # TODO handle
            nodes = BitMap()
        return nodes

    def get_descendants(self, node: str) -> BitMap:
        try:
            nodes = self.descendants[node]
        except KeyError:
            # TODO handle
            nodes = set()
        return nodes
