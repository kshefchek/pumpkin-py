import math
from typing import Callable, Collection, Iterable, Optional, Union

from pyroaring import BitMap, FrozenBitMap

from ..graph.graph import Graph
from . import metric

# Union types
Num = Union[int, float]


class GraphSemSim:
    """
    Graph based semantic similarity: similarity based on
    common sets of parent terms

    Implemented methods:
     1. jaccard (pairwise, groupwise)
     2. cosine (pairwise, negation support)
    """

    def __init__(self, graph: Graph):
        self.graph = graph

    def cosine_sim(
        self,
        profile_a: Iterable[str],
        profile_b: Iterable[str],
        negative_weight: Optional[Num] = 0.1,
        score_lambda: Optional[Callable] = lambda term: 1,
    ) -> float:
        """
        Cosine similarity
        Profiles are treated as vectors of numbers between 0-1:
        1: Phenotype present
        0: Absent (no information)
        1 * negative weight: Negated phenotypes

        0/1 scoring can be optionally overridden by passing in
        a lambda fx

        Inferred phenotypes are computed as parent classes for positive phenotypes
        and child classes for negative phenotypes.  Typically we do not want to
        weight negative phenotypes as high as positive phenotypes.  A weight between
        .01 - .1 may be desirable

        TODO optimize with numpy
        """

        positive_a_profile = {item for item in profile_a if not item[0] == '-'}
        negative_a_profile = {item[1:] for item in profile_a if item[0] == '-'}

        positive_b_profile = {item for item in profile_b if not item[0] == '-'}
        negative_b_profile = {item[1:] for item in profile_b if item[0] == '-'}

        pos_a_closure = self.graph.get_profile_closure(positive_a_profile)
        pos_b_closure = self.graph.get_profile_closure(positive_b_profile)

        neg_a_closure = (
            {
                "-{}".format(item)
                for item in self.graph.get_profile_closure(negative_a_profile, negative=True)
            }
            if negative_a_profile
            else set()
        )

        neg_b_closure = (
            {
                "-{}".format(item)
                for item in self.graph.get_profile_closure(negative_b_profile, negative=True)
            }
            if negative_b_profile
            else set()
        )

        pos_intersect_dot_product = sum(
            [math.pow(score_lambda(item), 2) for item in pos_a_closure.intersection(pos_b_closure)]
        )

        neg_intersect_dot_product = sum(
            [
                math.pow(score_lambda(item) * negative_weight, 2)
                for item in neg_a_closure.intersection(neg_b_closure)
            ]
        )

        a_square_dot_product = math.sqrt(
            sum(
                [math.pow(score_lambda(item), 2) for item in pos_a_closure],
            )
            + sum([math.pow(score_lambda(item) * negative_weight, 2) for item in neg_a_closure])
        )

        b_square_dot_product = math.sqrt(
            sum([math.pow(score_lambda(item), 2) for item in pos_b_closure])
            + sum([math.pow(score_lambda(item) * negative_weight, 2) for item in neg_b_closure])
        )

        numerator = pos_intersect_dot_product + neg_intersect_dot_product
        denominator = a_square_dot_product * b_square_dot_product

        try:
            result = numerator / denominator
        except ZeroDivisionError:
            result = 0

        return result

    def jaccard_sim(self, profile_a: Iterable[str], profile_b: Iterable[str]) -> float:
        """
        Jaccard similarity (intersection/union)
        Negative phenotypes must be prefixed with a '-'
        """
        # Filter out negative phenotypes
        profile_a = {pheno for pheno in profile_a if not pheno[0] == "-"}
        profile_b = {pheno for pheno in profile_b if not pheno[0] == "-"}

        pheno_a_set = self.graph.get_profile_closure(profile_a)
        pheno_b_set = self.graph.get_profile_closure(profile_b)

        return metric.jaccard(pheno_a_set, pheno_b_set)

    def groupwise_jaccard(self, profiles: Iterable[Iterable[str]]) -> float:
        """
        jaccard similarity applied to greater than 2 profiles,
        ie groupwise similarity instead of pairwise

        Useful for quantifying the strength of a cluster of
        profiles (eg disease clustering)
        """
        profile_union = BitMap.union(
            *[self.graph.get_profile_closure(profile) for profile in profiles]
        )
        profile_intersection = BitMap.intersection(
            *[self.graph.get_profile_closure(profile) for profile in profiles]
        )

        return len(profile_intersection) / len(profile_union)

    def proportion_subset(
        self, profile_a: Collection[str], profile_b: Collection[str], compute_inferred: bool = True
    ) -> float:
        """
        The proportion a profile a is subsumed by profile b
        for example: given two profiles
        A: {1,2,3,4}
        B: {3,4,5,6}
        The proportion A is subsumed by B is 50%
        """
        # An empty set is a proper subset of any other set
        if len(profile_a) == 0 and len(profile_b) >= 0:
            return 1.0
        # if profile_a is non empty and profile_b is, proportion is 0
        elif len(profile_b) == 0:
            return 0.0

        if compute_inferred:
            profile_a = self.graph.get_profile_closure(profile_a)
            profile_b = self.graph.get_profile_closure(profile_b)
        else:
            profile_a = FrozenBitMap([self.graph.id_map[node] for node in profile_a])
            profile_b = FrozenBitMap([self.graph.id_map[node] for node in profile_b])

        return len(BitMap.intersection(profile_a, profile_b)) / len(profile_a)
