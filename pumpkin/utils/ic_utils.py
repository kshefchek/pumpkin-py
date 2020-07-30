"""
Utilities for loading parts of an IC store

Alternatively could be part of the ICStore class as methods
"""
from typing import Dict, Set, BinaryIO
import numpy as np

from pumpkin.utils.math_utils import information_content
from ..graph.graph import Graph
from ..utils.math_utils import binomial_coeff


def load_ic_store(self, graph: Graph, outfile: BinaryIO) -> np.ndarray:
    """
    Creates an array of MICA values for every
    pair of phenotypes in a graph

    This is a symmetric matrix represented
    in a one dimension array, where to get the index
    of the MICA for A,B, retrieve their integer identifiers,
    sort A,B in ascending order, then take A x len(classes) - A + B - 1

    As of July 2020, there are 40296 classes with one or more
    subclasses, so we use uint16 to save memory (limit 65535)

    :param graph:
    :param outfile:
    :return: numpy 1d array of uint16
    """
    num_classes = len(self.id_map)
    combinations = int(binomial_coeff(num_classes))
    ic_store = np.zeros(combinations, dtype=np.uint16)
    for pheno_a, id_a in self.id_map.items():
        for pheno_b, id_b in self.id_map.items():
            if id_a < id_b:
                index = (((id_a * num_classes) - id_a) + id_b) - 1
                ic_store[index] = self.get_mica_ic(pheno_a, pheno_b, graph)
                if index % 100000000 == 0:
                    print("{} out of {}".format(index, combinations))
    np.save(outfile, ic_store)

    return ic_store


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
    node_annotations = {
        node: 0
        for node in graph.get_descendants(graph.root)
    }
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
