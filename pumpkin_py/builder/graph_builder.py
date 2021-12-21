import csv
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional, Set, TextIO, Tuple

from bidict import bidict
from pyroaring import FrozenBitMap
from rdflib import OWL, RDFS, BNode
from rdflib import Graph as RDFLibGraph
from rdflib import Literal, URIRef, util

from ..graph.graph import Graph
from ..graph.ic_graph import ICGraph
from ..models.namespace import Namespace
from ..store.ic_store import ICStore
from ..utils.ic_utils import make_ic_map


@dataclass
class FamilyTree:
    ancestors: Dict[str, Set[str]]
    descendants: Dict[str, Set[str]]
    id_map: bidict  # Dict[str, int]


def get_family_from_rdflib(iri: str, root: str) -> FamilyTree:
    ancestors = {}
    descendants = {}
    graph = RDFLibGraph()
    graph.load(iri, format=util.guess_format(iri))
    id_map = bidict()
    id = 0
    descendants[root] = get_descendants(root, graph)
    for node in descendants[root]:
        id_map[node] = id
        id += 1
        ancestors[node] = get_ancestors(node, graph, root)
        descendants[node] = get_descendants(node, graph)

    return FamilyTree(ancestors, descendants, id_map)


def build_graph_from_rdflib(iri: str, root: str):
    """
    Build graph using RDFLib

    Easier for testing small ontologies and datasets without robot
    :param iri: URL or local file path to iri, local files should be
                prefixed with file:///, see the utility function
                https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.as_uri
    :param root: root ontology term for semantic sim, eg HP:0000118 for HPO
    :return: Graph object
    """
    family_graph = get_family_from_rdflib(iri, root)
    ancestors, descendants, namespaces = _make_bitmaps(family_graph)

    return Graph(root, family_graph.id_map, ancestors, descendants, namespaces)


def build_graph_from_closures(
    ancestors: Dict[str, Set[str]], descendants: Dict[str, Set[str]], root: str
) -> Graph:
    id_map = bidict()
    id = 0
    for node in descendants[root]:
        id_map[node] = id
        id += 1

    ancestors, descendants, namespaces = _make_bitmaps(FamilyTree(ancestors, descendants, id_map))

    return Graph(root, id_map, ancestors, descendants, namespaces)


def build_graph_from_closure_file(closure_file: TextIO, root: str) -> Graph:
    ancestors, descendants = _get_closures(closure_file, root)
    return build_graph_from_closures(ancestors, descendants, root)


def build_ic_graph_from_closures(
    closure_file: TextIO, root: str, annotations: Optional[Dict[str, Set[str]]] = None
) -> ICGraph:
    """
    There's an awkward two-way dependency on an ic graph
    and an ic store.  An ic store requires a graph object, and
    an ic graph requires an ic store to initialize its descendent and ancestor bitmaps
    and sort them in ascending order for faster mica calcs - intersection().max()

    :param closure_file:
      text I/O stream such as returned by open(), containing a two column file with
      parent-child class relationships with transitive relationships enumerated
    :param root: root class as  curie formatted string
    :param annotations: Annotation map, eg output from builder.annotation_builder.flat_to_annotations

    :return: CacheGraph object with is_ordered=True
    """
    ancestors, descendants = _get_closures(closure_file, root)
    tmp_graph = build_graph_from_closures(ancestors, descendants, root)
    unsorted_ic = make_ic_map(tmp_graph, annotations)

    sorted_ic_twotuple = sorted([(cls, ic) for cls, ic in unsorted_ic.items()], key=lambda x: x[1])
    # Int encode in ascending order
    id = 0
    ic_map = {}
    id_map = bidict()
    for node, ic in sorted_ic_twotuple:
        id_map[tmp_graph.id_map.inverse[node]] = id
        ic_map[id] = ic
        id += 1

    ancestors, descendants, namespaces = _make_bitmaps(FamilyTree(ancestors, descendants, id_map))
    ic_store = ICStore(ic_map=ic_map, id_map=id_map)

    return ICGraph(root, id_map, ancestors, descendants, ic_store, namespaces)


def build_ic_graph_from_iri(
    iri: str, root: str, annotations: Optional[Dict[str, Set[str]]] = None
) -> ICGraph:
    """
    There's an awkward two-way dependency on an ic graph
    and an ic store.  An ic store requires a graph object, and
    an ic graph requires an ic store to initialize its descendent and ancestor bitmaps
    and sort them in ascending order for faster mica calcs - intersection().max()

    :param closure_file:
      text I/O stream such as returned by open(), containing a two column file with
      parent-child class relationships with transitive relationships enumerated
    :param root: root class as  curie formatted string
    :param annotations: Annotation map, eg output from builder.annotation_builder.flat_to_annotations

    :return: CacheGraph object with is_ordered=True
    """
    family_tree = get_family_from_rdflib(iri, root)
    bit_ancestors, bit_descendants, namespaces = _make_bitmaps(family_tree)
    tmp_graph = Graph(root, family_tree.id_map, bit_ancestors, bit_descendants, namespaces)
    unsorted_ic = make_ic_map(tmp_graph, annotations)

    sorted_ic_twotuple = sorted([(cls, ic) for cls, ic in unsorted_ic.items()], key=lambda x: x[1])
    # Int encode in ascending order
    id = 0
    ic_map = {}
    id_map = bidict()
    for node, ic in sorted_ic_twotuple:
        id_map[tmp_graph.id_map.inverse[node]] = id
        ic_map[id] = ic
        id += 1

    new_graph = FamilyTree(family_tree.ancestors, family_tree.descendants, id_map)
    ancestors, descendants, namespaces = _make_bitmaps(new_graph)
    ic_store = ICStore(ic_map=ic_map, id_map=id_map)

    return ICGraph(root, id_map, ancestors, descendants, ic_store, namespaces)


def _get_closures(
    closure_file: TextIO, root: str
) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """
    Convert two column closure file to dictionaries of
    curie (key) to sets of curies (value)

    :param closure_file:
      text I/O stream such as returned by open(), containing a two column file with
      parent-child class relationships with transitive relationships enumerated
    :param root: root class as  curie formatted string

    :return: Tuple of ancestors Dict[str, Set[str]], and descendants Dict[str, Set[str]]
    """
    ancestors = defaultdict(set)
    descendants = defaultdict(set)
    reader = csv.reader(closure_file, delimiter='\t', quotechar='\"')
    for row in reader:
        if row[0].startswith('#'):
            continue
        (node_a, node_b) = row[0:2]

        descendants[node_b].add(node_a)
        ancestors[node_a].add(node_b)

    # Remove ancestors above the root (eg owl:Class, HP:0000001)
    for node in ancestors.keys():
        ancestors[node] = descendants[root] & ancestors[node]

    return ancestors, descendants


def _make_bitmaps(
    family_graph: FamilyTree,
) -> Tuple[Dict[str, FrozenBitMap], Dict[str, FrozenBitMap], Dict[str, FrozenBitMap]]:
    """
    Convert ancestor and descendent str:Set dicts to str:bitmap dicts and create
    a namespace str:bitmap dictionary using the namespaces defined
    in models.Namespace

    :param id_map:
    :param ancestors:
    :param descendants:

    :return: Tuple of ancestors, descendants, namespace
    """
    namespaces = {}
    ancestor_bmap = {}
    descendant_bmap = {}

    for ns in Namespace:
        namespaces[ns] = FrozenBitMap(
            [
                family_graph.id_map[node]
                for node in family_graph.id_map.keys()
                if node.startswith(ns.value + ':') or node.startswith('UPHENO:')
            ]
        )

    for node in family_graph.ancestors.keys():
        ancestor_bmap[node] = FrozenBitMap(
            [family_graph.id_map[node] for node in family_graph.ancestors[node]]
        )

    for node in family_graph.descendants.keys():
        descendant_bmap[node] = FrozenBitMap(
            [family_graph.id_map[node] for node in family_graph.descendants[node]]
        )

    return ancestor_bmap, descendant_bmap, namespaces


def get_ancestors(node: str, graph: RDFLibGraph, root: str) -> Set[str]:
    """
    Reflexive get_ancestors from an rdflib graph

    Currently traverses subClassOf, equivalentClass outgoing,
    equivalentClass incoming

    Note that this doesn't search mixed predicate paths up the graph, so paths like
    subClassOf - equivalentClass - subClassOf will not be included in
    the closure, but our ontology construction should not include this
    pattern, and RDFLib should only be used for testing anyway

    :param node: node as a curie
    :param graph: RDFLib graph object
    :return: Set of ancestors
    """
    nodes = set()
    root_seen = {}
    node = URIRef("http://purl.obolibrary.org/obo/" + node.replace(":", "_"))

    if root is not None:
        root = URIRef("http://purl.obolibrary.org/obo/" + root.replace(":", "_"))
        root_seen = {root: 1}
    for obj in graph.transitive_objects(node, RDFS['subClassOf'], root_seen):
        if isinstance(obj, Literal) or isinstance(obj, BNode):
            continue
        nodes.add(str(obj).replace("http://purl.obolibrary.org/obo/", "").replace("_", ":"))

    for obj in graph.transitive_objects(node, OWL['equivalentClass'], root_seen):
        if isinstance(obj, Literal) or isinstance(obj, BNode):
            continue
        nodes.add(str(obj).replace("http://purl.obolibrary.org/obo/", "").replace("_", ":"))

    for sub in graph.transitive_subjects(OWL['equivalentClass'], node, root_seen):
        if isinstance(sub, Literal) or isinstance(sub, BNode):
            continue
        nodes.add(str(sub).replace("http://purl.obolibrary.org/obo/", "").replace("_", ":"))

    # Add root to graph
    if root is not None:
        nodes.add(root.replace("http://purl.obolibrary.org/obo/", "").replace("_", ":"))

    return nodes


def get_descendants(node: str, graph: RDFLibGraph) -> Set[str]:
    """
    Reflexive get_descendants from an rdflib graph

    :param node: node as a curie
    :param graph: RDFLib graph object
    :return: Set of descendants
    """
    nodes = set()
    node = URIRef("http://purl.obolibrary.org/obo/" + node.replace(":", "_"))
    for sub in graph.transitive_subjects(RDFS['subClassOf'], node):
        if isinstance(sub, Literal):
            continue
        nodes.add(str(sub).replace("http://purl.obolibrary.org/obo/", "").replace("_", ":"))
    return nodes
