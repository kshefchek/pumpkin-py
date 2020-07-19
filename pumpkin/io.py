from typing import Dict, Set, Tuple, TextIO, Optional
from collections import OrderedDict
from pyroaring import FrozenBitMap
import csv
from pumpkin.graph.CacheGraph import CacheGraph


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
) -> Tuple[Dict[str, int], Dict[str, FrozenBitMap], Dict[str, FrozenBitMap]]:
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

    # If annotations were passed sort the bitmap by IC
    if annotations:
        graph = CacheGraph(root, id_map, ancestors, descendants)
        graph.load_ic_map(annotations)

        # Sort ascending by IC for int encoding
        sorted_ic_map = OrderedDict(
            sorted(
                [(cls, ic) for cls, ic in graph.ic_map.items()],
                key=lambda x: x[1]
            )
        )
        id = 1
        for node in sorted_ic_map.keys():
            id_map[node] = id
            id += 1
    else:
        # Int encode
        id = 1
        for node in descendants[root]:
            id_map[node] = id
            id += 1

    for node in ancestors.keys():
        ancestors[node] = FrozenBitMap([id_map[node] for node in ancestors[node]])

    for node in descendants.keys():
        descendants[node] = FrozenBitMap([id_map[node] for node in descendants[node]])

    return id_map, ancestors, descendants
