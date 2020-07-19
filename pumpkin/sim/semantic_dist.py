from typing import Iterable, Dict, List, Union, Optional
from enum import Enum
from ..graph.Graph import Graph
from . import metric, matrix
from ..utils import sim_utils
import numpy as np


# Union types
Num = Union[int, float]


class PairwiseDist(Enum):
    EUCLIDEAN   = 'euclidean'
    JIN_CONRATH = 'jin_conrath'


class SemanticDist():

    def __init__(
            self,
            graph: Graph,
    ):
        self.graph = graph

    def euclidean_distance(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str]
    ) -> float:
        """
        Groupwise euclidean distance

        The euclidean distance between two vectors of IC values,
        where a vector is created by taking the union of phenotypes
        in two profiles (including parents of each phenotype)

        This is roughly analogous to, but the not the inverse of simGIC
        """
        # Filter out negative phenotypes
        profile_a = {pheno for pheno in profile_a if not pheno.startswith("-")}
        profile_b = {pheno for pheno in profile_b if not pheno.startswith("-")}

        a_closure = sim_utils.get_profile_closure(
            profile_a, self.graph)
        b_closure = sim_utils.get_profile_closure(
            profile_b, self.graph)

        all_phenotypes = a_closure.union(b_closure)

        a_vector = np.array([self.graph.ic_map[item] if
                             item in a_closure else 0 for item in all_phenotypes])
        b_vector = np.array([self.graph.ic_map[item] if
                            item in b_closure else 0 for item in all_phenotypes])

        return np.linalg.norm(a_vector - b_vector)

    def euclidean_matrix(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str],
            distance_measure: Union[PairwiseDist, str, None] = PairwiseDist.EUCLIDEAN
    ) -> np.ndarray:
        """
        Matrix wise euclidean distance

        This is roughly analogous to, but the not the inverse of matrix
        based similarity metrics (resnik, phenodigm)

        Pairwise distance based metrics:
        Jin Contrath = IC(a) + IC (b) - 2 IC(MICA(a,b))
        Euclidean = sqrt ( pow(IC(a) - MICA, 2) + pow(IC(b) - MICA), 2) )
        """
        ab_matrix = self._get_score_matrix(profile_a, profile_b, distance_measure)
        ba_matrix = self._get_score_matrix(profile_b, profile_a, distance_measure)
        return np.mean(
            [matrix.best_min_avg(ab_matrix), matrix.best_min_avg(ba_matrix)],
            dtype=np.float64
        )

    def _get_score_matrix(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str],
            distance_measure: Optional[PairwiseDist] = PairwiseDist.EUCLIDEAN
    ) -> List[List[float]]:

        score_matrix = [[]]

        if distance_measure == PairwiseDist.EUCLIDEAN:
            sim_fn = metric.pairwise_euclidean
        elif distance_measure == PairwiseDist.JIN_CONRATH:
            sim_fn = metric.jin_conrath_distance
        else:
            raise NotImplementedError

        for index, pheno_a in enumerate(profile_a):
            if index == len(score_matrix):
                score_matrix.append([])
            for pheno_b in profile_b:
                score_matrix[index].append(sim_fn(pheno_a, pheno_b, self.graph))

        return score_matrix
