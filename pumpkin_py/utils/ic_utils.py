"""
Utilities for loading parts of an IC store

Alternatively could be part of the ICStore class as methods
"""
from typing import Dict, Set

from pumpkin_py.utils.math_utils import information_content

from ..graph.graph import Graph


def make_ic_map(graph: Graph, annotations: Dict[str, Set[str]]) -> Dict[int, float]:
    """
    Create an map of integer (integer encoded phenotype class) and its information content
    based on a set of input annotations

    :param graph:
    :param annotations:
    :return: ic_map, Dict[int, float]
    """
    ic_map: Dict[int, float] = {}
    explicit_annotations = 0
    node_annotations = {node: 0 for node in graph.get_descendants(graph.root)}
    for profile in annotations.values():
        for node in profile:
            has_ancestors = False
            for cls in graph.get_ancestors(node):
                node_annotations[cls] += 1
                has_ancestors = True
            if has_ancestors:
                explicit_annotations += 1

    # laplacian smoothing
    for node, annot_count in node_annotations.items():
        if annot_count == 0:
            explicit_annotations += 1
            for ancestor in graph.get_ancestors(node):
                node_annotations[ancestor] += 1

    for node, annot_count in node_annotations.items():
        ic_map[node] = information_content(annot_count / explicit_annotations)

    return ic_map
