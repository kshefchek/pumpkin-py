from typing import Dict
from pyroaring import FrozenBitMap
from bidict import bidict
from .graph import Graph
from ..store.ic_store import ICStore
from ..models.namespace import Namespace


class ICGraph(Graph):
    """
    A graph implementation that caches ancestors and descendants
    as BitMaps using pyroaring
    (previously done with sets of ints)
    """

    def __init__(
            self,
            root: str,
            id_map: bidict,  # Dict[str, int]
            ancestors: Dict[str, FrozenBitMap],
            descendants: Dict[str, FrozenBitMap],
            ic_store: ICStore,
            namespace_map: Dict[Namespace, FrozenBitMap] = None
    ):
        """

        :param root:
        :param id_map:
        :param ancestors:
        :param descendants:
        :param ic_store:
        :param namespace_map:
        """
        super(ICGraph, self).__init__(root, id_map, ancestors, descendants, namespace_map)
        self.ic_store = ic_store

        if ic_store.id_map is not self.id_map:
            raise ValueError("Must use same id_map for graph and ic_store")

    def get_mica_ic(self, pheno_a: str, pheno_b: str) -> float:
        try:
            p1_closure = self.ancestors[pheno_a]
            p2_closure = self.ancestors[pheno_b]
        except KeyError:
            return 0

        mica = self.ic_store.ic_map[p1_closure.intersection(p2_closure).max()]

        return mica

    def get_ic(self, node: str) -> float:
        return self.ic_store.ic_map[self.id_map[node]]

    def get_mica_id(self, pheno_a: str, pheno_b: str) -> str:
        """
        Return ID of most informative common anscestor of two phenotypes
        Currently does not handle ambiguity (>1 equal MICAs)
        """
        try:
            p1_closure = self.ancestors[pheno_a]
            p2_closure = self.ancestors[pheno_b]
        except KeyError:
            pass  # TODO handle

        mica_id = None

        try:
            mica_id = p1_closure.intersection(p2_closure).max()
        except KeyError:
            pass  # TODO handle
        except ValueError:
            pass  # TODO handle

        return self.id_map.inverse(mica_id)
