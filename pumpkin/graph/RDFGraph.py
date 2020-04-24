from rdflib import URIRef, BNode, Literal, RDFS, util
from rdflib import Graph as RDFLibGraph
from typing import Optional, Set
from prefixcommons import contract_uri, expand_uri
from . import Graph


class RDFGraph(Graph):
    """
    RDFLib based graph implementation

    Easier for testing small ontologies and datasets, but slower
    than CacheGraph due to needing to traverse the graph for each
    query
    """

    def __init__(
            self,
            iri: str,
            root: Optional[str] = None,
            edge: Optional[URIRef]=RDFS['subClassOf']
    ):
        self.graph = RDFLibGraph.load(iri, format=util.guess_format(iri))
        self.root = root
        self.edge = edge
        self.ic_map = {}

    def get_closure(
            self,
            node: str,
            negative: Optional[bool] = False
    ) -> Set[str]:
        nodes = set()
        if negative:
            nodes = self.get_descendants(node)
        else:
            nodes = self.get_ancestors(node)
        return nodes

    def get_ancestors(self, node: str) -> Set[str]:
        nodes = set()
        root_seen = {}
        node = URIRef(expand_uri(node, strict=True))

        if self.root is not None:
            root = URIRef(expand_uri(self.root, strict=True))
            root_seen = {root: 1}
        for obj in self.graph.transitive_objects(node, self.edge, root_seen):
            if isinstance(obj, Literal) or isinstance(obj, BNode):
                continue
            nodes.add(contract_uri(str(obj), strict=True)[0])

        # Add root to graph
        if self.root is not None:
            nodes.add(contract_uri(str(self.root), strict=True)[0])

        return nodes

    def get_descendants(self, node: str) -> Set[str]:
        nodes = set()
        node = URIRef(expand_uri(node, strict=True))
        for sub in self.graph.transitive_subjects(self.edge, node):
            if isinstance(sub, Literal):
                continue
            nodes.add(contract_uri(str(sub), strict=True)[0])
        return nodes
