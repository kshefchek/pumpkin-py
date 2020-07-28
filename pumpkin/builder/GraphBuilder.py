from typing import Dict, Set, TextIO, Optional, Tuple
from pyroaring import FrozenBitMap
import csv
from bidict import bidict
from ..graph.CacheGraph import CacheGraph
from ..models.Namespace import Namespace, namespace


def build_ordered_graph(
        closure_file: TextIO,
        root: str,
        annotations: Optional[Dict[str, Set[str]]] = None
) -> CacheGraph:
    """
    There's an awkward two-way dependency on an ordered cached graph
    and an ic store.  An ic store requires a graph object, and
    an ordered graph requires an ic store (to order integer encoded phenotypes)

    :param closure_file:
      text I/O stream such as returned by open(), containing a two column file with
      parent-child class relationships with transitive relationships enumerated
    :param root: root class as  curie formatted string
    :param annotations

    :return: CacheGraph object with is_ordered=True
    """
    id_map = bidict()
    ancestors, descendants = _get_closures(closure_file, root)

    tmp_graph = CacheGraph(root, id_map, ancestors, descendants)
    tmp_graph.load_ic_map(annotations)

    sorted_ic_map = zip(*sorted(
        [(cls, ic) for cls, ic in tmp_graph.ic_map.items()],
        key=lambda x: x[1]
    ))
    # Int encode in ascending order
    id = 0
    for node in next(sorted_ic_map):
        id_map[node] = id
        id += 1

    ancestors, descendants, namespace_map = _make_bitmaps(
        id_map, ancestors, descendants
    )

    return CacheGraph(root, id_map, ancestors, descendants, namespace_map, is_ordered=True)


def build_graph(closure_file: TextIO, root: str) -> CacheGraph:
    """
    Build unordered cache graph

    :param closure_file:
      text I/O stream such as returned by open(), containing a two column file with
      parent-child class relationships with transitive relationships enumerated
    :param root: root class as  curie formatted string

    :return: CacheGraph object with is_ordered=False
    """
    id_map = bidict()
    ancestors, descendants = _get_closures(closure_file, root)

    # Int encode non ordered
    id = 0
    for node in descendants[root]:
        id_map[node] = id
        id += 1

    ancestors, descendants, namespace_map = _make_bitmaps(
        id_map, ancestors, descendants
    )

    return CacheGraph(root, id_map, ancestors, descendants, namespace_map, is_ordered=False)


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
    anscestor_bmap = {}
    descendant_bmap = {}

    for ns in namespace.keys():
        namespace_map[ns] = FrozenBitMap(
            [id_map[node] for node in id_map.keys()
             if node.startswith(namespace[ns] + ':')]
        )

    for node in ancestors.keys():
        anscestor_bmap[node] = FrozenBitMap([id_map[node] for node in ancestors[node]])

    for node in descendants.keys():
        descendant_bmap[node] = FrozenBitMap([id_map[node] for node in descendants[node]])

    return anscestor_bmap, descendant_bmap, namespace_map

