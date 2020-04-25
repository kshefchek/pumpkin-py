from typing import Set, Dict
from .Graph import Graph


class RDFGraph(Graph):
    """
    RDFLib based graph implementation

    Easier for testing small ontologies and datasets, but slower
    than CacheGraph due to needing to traverse the graph for each
    query
    """

    def __init__(
            self,
            root: str,
            ancestors: Dict[str, Set[str]],
            descendants: Dict[str, Set[str]]
    ):
        self.ancestors = ancestors
        self.descendants = descendants
        self.ic_map = {}

    def get_ancestors(self, node: str) -> Set[str]:
        try:
            nodes = self.ancestors[node]
        except KeyError:
            # TODO handle
            nodes = set()
        return nodes

    def get_descendants(self, node: str) -> Set[str]:
        try:
            nodes = self.descendants[node]
        except KeyError:
            # TODO handle
            nodes = set()
        return nodes

    def load_ic_map(self):
        """
        Initializes ic_map
        """
        raise NotImplementedError
