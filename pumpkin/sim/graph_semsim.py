from typing import Iterable, Callable, Union, Optional
import math
from pyroaring import BitMap
from . import metric
from ..graph.graph import Graph


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
            negative_weight: Optional[Num] = .1,
            score_lambda: Optional[Callable] = lambda term: 1
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
        .01-.1 may be desirable
        """

        positive_a_profile = {item for item in profile_a if not item[0] == '-'}
        negative_a_profile = {item[1:] for item in profile_a if item[0] == '-'}

        positive_b_profile = {item for item in profile_b if not item[0] == '-'}
        negative_b_profile = {item[1:] for item in profile_b if item[0] == '-'}

        pos_a_closure = self.graph.get_profile_closure(positive_a_profile)
        pos_b_closure = self.graph.get_profile_closure(positive_b_profile)

        neg_a_closure = {"-{}".format(item)
                         for item in self.graph.get_profile_closure(
            negative_a_profile, negative=True)
                         } if negative_a_profile else set()

        neg_b_closure = {"-{}".format(item)
                         for item in self.graph.get_profile_closure(
            negative_b_profile, negative=True)
                         } if negative_b_profile else set()

        pos_intersect_dot_product = sum(
            [math.pow(score_lambda(item), 2)
             for item in pos_a_closure.intersection(pos_b_closure)]
        )

        neg_intersect_dot_product = sum(
            [math.pow(score_lambda(item) * negative_weight, 2)
             for item in neg_a_closure.intersection(neg_b_closure)]
        )

        a_square_dot_product = math.sqrt(
            sum(
                [math.pow(score_lambda(item), 2) for item in pos_a_closure],
            ) +
            sum(
                [math.pow(score_lambda(item) * negative_weight, 2)
                 for item in neg_a_closure]
            )
        )

        b_square_dot_product = math.sqrt(
            sum(
                [math.pow(score_lambda(item), 2) for item in pos_b_closure]
            ) +
            sum(
                [math.pow(score_lambda(item) * negative_weight, 2)
                 for item in neg_b_closure]
            )
        )

        numerator = pos_intersect_dot_product + neg_intersect_dot_product
        denominator = a_square_dot_product * b_square_dot_product

        try:
            result = numerator / denominator
        except ZeroDivisionError:
            result = 0

        return result

    def jaccard_sim(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str]
    ) -> float:
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


    def groupwise_jaccard(
            self,
            profiles: Iterable[Iterable[str]]
    ) -> float:
        """
        jaccard similarity applied to greater than 2 profiles,
        ie groupwise similarity instead of pairwise

        Useful for quantifying the strength of a cluster of
        profiles (eg disease clustering)
        """
        # Filter out negative phenotypes

        profile_union = BitMap.union(
            *[self.graph.get_profile_closure(profile) for profile in profiles]
        )
        profile_intersection = BitMap.intersection(
            *[self.graph.get_profile_closure(profile) for profile in profiles]
        )

        return len(profile_intersection)/len(profile_union)
