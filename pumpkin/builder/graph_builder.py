from typing import Dict, Set, TextIO, Optional, Tuple
import csv

from pyroaring import FrozenBitMap
from bidict import bidict
from rdflib import Graph as RDFLibGraph
from rdflib import URIRef, BNode, Literal, RDFS, util

from ..graph.graph import Graph
from ..graph.ic_graph import ICGraph
from ..store.ic_store import ICStore
from ..models.namespace import Namespace, namespace
from ..utils.ic_utils import make_ic_map


def build_graph_from_rdflib(iri: str, root: str):
    """
    Build graph using RDFLib

    Easier for testing small ontologies and datasets without robot
    :param iri:
    :param root:
    :return:
    """
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

    ancestors, descendants, namespace_map = _make_bitmaps(
        id_map, ancestors, descendants
    )

    return Graph(root, id_map, ancestors, descendants, namespace_map)


def build_graph_from_closures(
        ancestors: Dict[str, Set[str]],
        descendants: Dict[str, Set[str]],
        root: str
) -> Graph:
    id_map = bidict()
    id = 0
    for node in descendants[root]:
        id_map[node] = id
        id += 1

    ancestors, descendants, namespace_map = _make_bitmaps(
        id_map, ancestors, descendants
    )

    return Graph(root, id_map, ancestors, descendants, namespace_map)


def build_ic_graph_from_closures(
        closure_file: TextIO,
        root: str,
        annotations: Optional[Dict[str, Set[str]]] = None
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
    :param annotations

    :return: CacheGraph object with is_ordered=True
    """
    ancestors, descendants = _get_closures(closure_file, root)
    tmp_graph = build_graph_from_closures(ancestors, descendants, root)
    unsorted_ic = make_ic_map(tmp_graph, annotations)

    sorted_ic_twotuple = sorted(
        [(cls, ic) for cls, ic in unsorted_ic.items()],
        key=lambda x: x[1]
    )
    # Int encode in ascending order
    id = 0
    ic_map = {}
    id_map = bidict()
    for node, ic in sorted_ic_twotuple:
        id_map[tmp_graph.id_map.inverse[node]] = id
        ic_map[id] = ic
        id += 1

    ancestors, descendants, namespace_map = _make_bitmaps(
        id_map, ancestors, descendants
    )
    ic_store = ICStore(ic_map=ic_map, id_map=id_map)

    return ICGraph(root, id_map, ancestors, descendants, ic_store, namespace_map)


def _get_closures(
        closure_file: TextIO,
        root: str
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
    ancestors = {}
    descendants = {}
    reader = csv.reader(closure_file, delimiter='\t', quotechar='\"')
    for row in reader:
        if row[0].startswith('#'): continue
        (node_a, node_b) = row[0:2]

        try:
            descendants[node_b].add(node_a)
        except KeyError:
            descendants[node_b] = {node_a}

        try:
            ancestors[node_a].add(node_b)
        except KeyError:
            ancestors[node_a] = {node_b}

    # Remove ancestors above the root (eg owl:Class, HP:0000001)
    for node in ancestors.keys():
        ancestors[node] = descendants[root] & ancestors[node]

    return ancestors, descendants


def _make_bitmaps(
        id_map: bidict,
        ancestors: Dict[str, Set[str]],
        descendants: Dict[str, Set[str]]
) -> Tuple[
    Dict[str, FrozenBitMap],
    Dict[str, FrozenBitMap],
    Dict[Namespace, FrozenBitMap]
]:
    """
    Convert ancestor and descendent str:Set dicts to str:bitmap dicts and create
    a namespace str:bitmap dictionary using the namespaces defined
    in models.Namespace

    :param id_map:
    :param ancestors:
    :param descendants:

    :return: Tuple of ancestors, descendants, namespace
    """
    namespace_map = {}
    ancestor_bmap = {}
    descendant_bmap = {}

    for ns in namespace.keys():
        namespace_map[ns] = FrozenBitMap(
            [
                id_map[node] for node in id_map.keys()
                if node.startswith(namespace[ns] + ':') or node.startswith('UPHENO:')
            ]
        )

    for node in ancestors.keys():
        ancestor_bmap[node] = FrozenBitMap([id_map[node] for node in ancestors[node]])

    for node in descendants.keys():
        descendant_bmap[node] = FrozenBitMap([id_map[node] for node in descendants[node]])

    return ancestor_bmap, descendant_bmap, namespace_map


def get_ancestors(node: str, graph: RDFLibGraph, root: str) -> Set[str]:
    """
    Reflexive get_ancestors from an rdflib graph
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
