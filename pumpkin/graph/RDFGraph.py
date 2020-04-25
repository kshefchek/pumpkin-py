from rdflib import URIRef, BNode, Literal, RDFS, util
from rdflib import Graph as RDFLibGraph
from typing import Optional, Set
from prefixcommons import contract_uri, expand_uri
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
            iri: str,
            edge: Optional[URIRef]=RDFS['subClassOf']
    ):
        self.graph = RDFLibGraph()
        self.root = root
        self.edge = edge
        self.ic_map = {}
        self.graph.load(iri, format=util.guess_format(iri))

    def get_ancestors(self, node: str) -> Set[str]:
        """
        Reflexive get_ancestors
        :param node:
        :return:
        """
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
            nodes.add(self.root)

        return nodes

    def get_descendants(self, node: str) -> Set[str]:
        nodes = set()
        node = URIRef(expand_uri(node, strict=True))
        for sub in self.graph.transitive_subjects(self.edge, node):
            if isinstance(sub, Literal):
                continue
            nodes.add(contract_uri(str(sub), strict=True)[0])
        return nodes
