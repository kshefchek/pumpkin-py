from typing import Dict, Set, BinaryIO
from numpy import ndarray
import numpy as np
from bidict import bidict

from pumpkin.utils.math_utils import information_content
from pumpkin.graph import Graph
from pumpkin.utils.math_utils import binomial_coeff


class ICStore():
    """
    Class for storing information content per class and optionally
    a cached array of micas between all classes
    """
    store: ndarray
    ic_map: Dict[int, float]
    id_map: bidict  #bidict[Dict[str, int]]

    def __init__(self):
        pass

    def get_mica_ic(self, graph:Graph, pheno_a: str, pheno_b: str) -> float:
        if self.store is None:
            ic = self._get_mica_ic_from_graph(graph, pheno_a, pheno_b)
        else:
            ic = self._get_mica_ic_from_store(pheno_a, pheno_b)
        return ic

    def get_ic(self, node: str) -> float:
        return self.ic_map[self.id_map[node]]

    def _get_mica_ic_from_graph(
            self,
            graph: Graph,
            pheno_a: str,
            pheno_b: str
    ) -> float:
        p1_closure = graph.ancestors[pheno_a]
        p2_closure = graph.ancestors[pheno_b]

        if graph.is_ordered:
            try:
                mica = graph.ic_map[p1_closure.intersection(p2_closure).max()]
            except KeyError:
                mica = 0
            except ValueError:
                mica = 0

        else:
            mica = max(
                [self.ic_map[parent] for parent in p1_closure.intersection(p2_closure)],
                default=0
            )

        return mica

    def _get_mica_ic_from_store(self, pheno_a: str, pheno_b: str) -> float:
        id_a = self.id_map[pheno_a]
        id_b = self.id_map[pheno_b]
        index = ((id_a * len(self.id_map) - id_a) + id_b) - 1

        return self.ic_map[self.store[index]]

    def _get_mica_from_graph(
            self,
            pheno_a: str,
            pheno_b: str,
            graph: Graph
    ) -> str:
        """
        Return ID of most informative common anscestor of two phenotypes
        Currently does not handle ambiguity (>1 equal MICAs)
        """
        p1_closure = graph.ancestors[pheno_a]
        p2_closure = graph.ancestors[pheno_b]
        mica = None
        if graph.is_ordered:
            try:
                mica = p1_closure.intersection(p2_closure).max()
            except KeyError:
                pass  # TODO handle
            except ValueError:
                pass  # TODO handle

        else:
            overlap = p1_closure.intersection(p2_closure)
            max_ic = max([graph.ic_map[parent] for parent in overlap])
            mica = ''
            for pheno in overlap:
                if graph.ic_map[pheno] == max_ic:
                    mica = pheno
        return self.id_map.inverse(mica)

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

    @staticmethod
    def load_ic_map(graph:Graph, annotations: Dict[str, Set[str]]):
        """
        Initializes ic_map
        """
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
            graph.ic_map[node] = information_content(annot_count / explicit_annotations)
