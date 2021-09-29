from typing import Dict, Iterable, Optional

from bidict import bidict
from pyroaring import BitMap, FrozenBitMap

from ..models.namespace import Namespace


class Graph:
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
        namespaces: Dict[Namespace, FrozenBitMap] = None,
    ):
        """

        :param root: Root of the ontology (UPHENO:0001001, HP:0000118)
        :param id_map: dictionary of curie id (key) to integer encoded id (value)
        :param ancestors: dictionary of curie id (key) and frozen bitmap,
                          created from an array of integers for its ancestors
                          self included (reflexive closure)
        :param descendants: dictionary of curie id (key) and frozen bitmap,
                            created from an array of integers for its descendants
                            (self included)
        :param namespaces: dictionary of namespace (key) and frozen bitmap,
                           created from an array of integers of all ids in
                           the namespace
        """
        self.root = root
        self.id_map = id_map
        self.ancestors = ancestors
        self.descendants = descendants
        self.namespaces = namespaces

    def get_ancestors(self, node: str) -> FrozenBitMap:
        """
        TODO make this explicit (eg rename) that the input
        is a curie and the output is a list of integer encoded
        ids

        perhaps create get_ancestors_by_curie and get_ancestors_by_id

        :param node: Curie formatted string
        :return: List of integer encoded ids as a FrozenBitMap
        """
        try:
            nodes = self.ancestors[node]
        except KeyError as key_error:
            if not isinstance(node, str):
                raise key_error
            # TODO handle
            nodes = FrozenBitMap()
        return nodes

    def get_descendants(self, node: str) -> FrozenBitMap:
        """

        :param node: Curie formatted string
        :return: List of integer encoded ids as a FrozenBitMap
        """
        try:
            nodes = self.descendants[node]
        except KeyError as key_error:
            # TODO handle
            if not isinstance(node, str):
                raise key_error
            nodes = FrozenBitMap()
        return nodes

    def get_closure(self, node: str, negative: Optional[bool] = False) -> FrozenBitMap:
        if negative:
            nodes = self.get_descendants(node)
        else:
            nodes = self.get_ancestors(node)
        return nodes

    def get_profile_closure(
        self, profile: Iterable[str], negative: Optional[bool] = False
    ) -> BitMap:
        """
        Given a list of phenotypes, get the reflexive closure for each phenotype
        stored in a single set.  This can be used for jaccard similarity or
        simGIC
        """
        return BitMap.union(*[self.get_closure(node, negative=negative) for node in profile])
