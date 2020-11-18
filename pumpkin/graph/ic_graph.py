from typing import Dict, Optional

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
            namespaces: Dict[Namespace, FrozenBitMap]
    ):
        """

        :param root:
        :param id_map:
        :param ancestors:
        :param descendants:
        :param ic_store:
        :param namespace_map:
        """
        super(ICGraph, self).__init__(root, id_map, ancestors, descendants, namespaces)
        self.ic_store = ic_store

        if ic_store.id_map is not self.id_map:
            raise ValueError("Must use same id_map for graph and ic_store")

    def get_mica_ic(
            self,
            pheno_a: str,
            pheno_b: str,
            ns_filter: Optional[Namespace] = None
    ) -> float:
        """
        Gets the most informative common ancestor from two IC sorted
        bitmaps, optionally filtered by a target namespace
        :param pheno_a: phenotype curie
        :param pheno_b: phenotype curie
        :param ns_filter: filter for a specific namespace, for example,
        for mica queries targeting a specific species
        "what is the mica in mouse between p1 and p2"
        :return: information content of the mica
        """
        try:
            p1_closure = self.ancestors[pheno_a]
            p2_closure = self.ancestors[pheno_b]
        except KeyError:
            return 0

        if ns_filter:
            mica_id = p1_closure\
                .intersection(p2_closure)\
                .intersection(self.namespaces[ns_filter])\
                .max()
            mica = self.ic_store.ic_map[mica_id]
        else:
            mica = self.ic_store.ic_map[p1_closure.intersection(p2_closure).max()]

        return mica

    def get_ic(self, node: str) -> float:
        return self.ic_store.ic_map[self.id_map[node]]

    def get_mica_id(
            self,
            pheno_a: str,
            pheno_b: str,
            ns_filter: Optional[Namespace] = None
    ) -> str:
        """
        Return ID of most informative common ancestor of two phenotypes
        Currently does not handle ambiguity (>1 equal MICAs)
        """
        mica_id = ''

        try:
            p1_closure = self.ancestors[pheno_a]
            p2_closure = self.ancestors[pheno_b]
        except KeyError:
            return mica_id

        if ns_filter:
            mica_id = p1_closure \
                .intersection(p2_closure) \
                .intersection(self.namespaces[ns_filter]) \
                .max()
        else:
            mica_id = p1_closure.intersection(p2_closure).max()

        return self.id_map.inverse[mica_id]
