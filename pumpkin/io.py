from typing import Dict, Set, Tuple, TextIO, Optional
from pyroaring import FrozenBitMap
import csv
from .graph.CacheGraph import CacheGraph
from .models.Namespace import namespace


def flat_to_annotations(file: TextIO) -> Dict[str, Set[str]]:
    """
    Convert a two column file to an annotation dictionary
    :param file: text I/O stream such as returned by open()
    :return: annotations: Dict[str, Set[str]]
    """
    annotations = {}
    reader = csv.reader(file, delimiter='\t', quotechar='\"')
    for row in reader:
        if row[0].startswith('#'): continue
        (individual, cls) = row[0:2]
        try:
            annotations[individual].add(cls)
        except KeyError:
            annotations[individual] = {cls}

    return annotations


def flat_to_graph(
        file: TextIO,
        root: str,
        annotations: Optional[Dict[str, Set[str]]] = None
) -> CacheGraph:
    """
    Convert a two column file to map of ancestors and desecendants
    :param file: text I/O stream such as returned by open()
    :param root: root class as  curie formatted string
    :param annotations

    :return: Tuple(id_map, ancestors, descendants)
             an id_map of shape Dict[str, int]
             and two maps with shapes: Dict[str, FrozenBitMap]
    """
    ancestors = {}
    descendants = {}
    id_map = {}
    namespace_map = {}
    reader = csv.reader(file, delimiter='\t', quotechar='\"')
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

    # If annotations were passed sort the bitmap by IC in ascending order
    if annotations:
        graph = CacheGraph(root, id_map, ancestors, descendants)
        graph.load_ic_map(annotations)

        sorted_ic_map = zip(*sorted(
            [(cls, ic) for cls, ic in graph.ic_map.items()],
            key=lambda x: x[1]
        ))
        id = 1
        for node in next(sorted_ic_map):
            id_map[node] = id
            id += 1
    else:
        # Int encode non ordered
        id = 1
        for node in descendants[root]:
            id_map[node] = id
            id += 1

    for ns in namespace.keys():
        namespace_map[ns] = FrozenBitMap(
            [id_map[node] for node in id_map.keys()
             if node.startswith(namespace[ns] + ':')]
        )

    for node in ancestors.keys():
        ancestors[node] = FrozenBitMap([id_map[node] for node in ancestors[node]])

    for node in descendants.keys():
        descendants[node] = FrozenBitMap([id_map[node] for node in descendants[node]])

    if annotations:
        graph = CacheGraph(root, id_map, ancestors, descendants, namespace_map, is_ordered=True)
    else:
        graph = CacheGraph(root, id_map, ancestors, descendants, namespace_map, is_ordered=False)

    return graph
