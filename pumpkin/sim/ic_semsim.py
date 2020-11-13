from typing import Iterable, List, Union, Optional
from enum import Enum
import numpy as np
from pyroaring import BitMap
from . import metric, matrix
from .graph_semsim import GraphSemSim
from ..graph.ic_graph import ICGraph
from ..utils.math_utils import geometric_mean


# Union types
Num = Union[int, float]


class PairwiseSim(Enum):
    GEOMETRIC = 1
    IC        = 2
    JACCARD   = 3


class MatrixMetric(Enum):
    MAX = 1  # Max
    AVG = 2  # Average
    BMA = 3  # Best Match Average


class ICSemSim:
    """
    Information content based semantic similarity: similarity based on
    the most informative common term between two terms, where information
    content is the -log(term annotation frequency)

    See Resnik's first manuscript on IC based similarity as a background:
    https://arxiv.org/pdf/cmp-lg/9511007.pdf

    Implemented methods:
     1. Resnik
     2. PhenoDigm
     3. simGIC
     3. IC weighted cosine sim
    """

    def __init__(self, graph: ICGraph):
        self.graph = graph

    def resnik_sim(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str],
            matrix_metric: Union[MatrixMetric, str, None] = MatrixMetric.BMA,
            is_symmetric: Optional[bool] = False,
            is_normalized: Optional[bool] = False
    ) -> float:
        """
        Resnik similarity

        Implementations:
        BMA (Best Match Average) - Average of the best match (max) per row in matrix
        Max - Max of matrix
        Average - Average IC of every item (mica) in matrix
        :param profile_a: Sequence of phenotypes
        :param profile_b: Sequence of phenotypes
        :param matrix_metric: BMA, max, avg Default: BMA
        :param is_symmetric: avg(Pa vs Pb, Pb vs Pa) Default: False
        :param is_normalized: Normalize by dividing by the resnik
                              of the optimal matrix Default: False
        :return: resnik score, a float between 0-MaxIC in cache,
                 if normalized a float between 0-1
        """
        # Filter out negative phenotypes
        profile_a = {pheno for pheno in profile_a if not pheno[0] == "-"}
        profile_b = {pheno for pheno in profile_b if not pheno[0] == "-"}

        sim_measure = PairwiseSim.IC

        query_matrix = self._get_score_matrix(
            profile_a, profile_b, sim_measure)

        if is_normalized:
            optimal_matrix = self._get_optimal_matrix(
                profile_a, sim_measure=sim_measure)
        else:
            optimal_matrix = None

        resnik_score = 0
        if is_symmetric:
            b2a_matrix = matrix.flip_matrix(query_matrix)
            optimal_b_matrix = self._get_optimal_matrix(
                profile_b, sim_measure=sim_measure)
            resnik_score = np.mean(
                [self._compute_resnik_score(
                    query_matrix, optimal_matrix, matrix_metric),
                 self._compute_resnik_score(
                     b2a_matrix, optimal_b_matrix, matrix_metric)],
                dtype=np.float64
            )
        else:
            resnik_score = self._compute_resnik_score(
                query_matrix, optimal_matrix, matrix_metric)

        return resnik_score

    @staticmethod
    def _compute_resnik_score(
            query_matrix: List[List[float]],
            optimal_matrix: Optional[List[List[float]]] = None,
            matrix_metric: Optional[MatrixMetric] = MatrixMetric.BMA
    )-> float:

        is_normalized = True if optimal_matrix else False

        resnik_score = 0

        if matrix_metric == MatrixMetric.BMA:
            if is_normalized:
                resnik_score = matrix.bma_percentage_score(
                    query_matrix, optimal_matrix)
            else:
                resnik_score = matrix.bma_score(query_matrix)
        elif matrix_metric == MatrixMetric.MAX:
            if is_normalized:
                resnik_score = matrix.max_percentage_score(
                    query_matrix, optimal_matrix)
            else:
                resnik_score = matrix.max_score(query_matrix)
        elif matrix_metric == MatrixMetric.AVG:
            if is_normalized:
                resnik_score = matrix.avg_percentage_score(
                    query_matrix, optimal_matrix)
            else:
                resnik_score = matrix.avg_score(query_matrix)

        return resnik_score

    def phenodigm_compare(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str],
            is_symmetric: Optional[bool] = False,
            is_same_species: Optional[bool] = True,
            sim_measure: Optional[PairwiseSim] = PairwiseSim.GEOMETRIC
    ) -> Union[float, np.ndarray]:
        """
        Phenodigm algorithm:
        https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649640/pdf/bat025.pdf

        There are two common variations of the pairwise similarity calculations
        1. geometric mean of the jaccard index and ic of the MICA
        2. ic of the MICA

        The first is the metric used in the published algorithm, the second
        is used in the owltools OWLTools-Sim package
        """
        # Filter out negative phenotypes
        profile_a = {pheno for pheno in profile_a if not pheno[0] == "-"}
        profile_b = {pheno for pheno in profile_b if not pheno[0] == "-"}

        query_matrix = self._get_score_matrix(profile_a, profile_b, sim_measure)
        if is_same_species:
            optimal_matrix = self._get_optimal_matrix(
                profile_a, is_same_species, sim_measure)
        else:
            raise NotImplementedError

        if is_symmetric:
            b2a_matrix = matrix.flip_matrix(query_matrix)
            optimal_b_matrix = self._get_optimal_matrix(
                profile_b, is_same_species, sim_measure)
            score = np.mean(
                [self.compute_phenodigm_score(query_matrix, optimal_matrix),
                 self.compute_phenodigm_score(b2a_matrix, optimal_b_matrix)],
                dtype=np.float64
            )
        else:
            score = self.compute_phenodigm_score(query_matrix, optimal_matrix)

        return score

    @staticmethod
    def compute_phenodigm_score(
            query_matrix: List[List[float]],
            optimal_matrix: List[List[float]]) -> np.ndarray:
        return 100 * np.mean(
            [matrix.max_percentage_score(query_matrix, optimal_matrix),
             matrix.sym_bma_percentage_score(query_matrix, optimal_matrix)],
            dtype=np.float64
        )

    def sim_gic(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str]
    ) -> float:
        """
        Summed resnik similarity:
        Summed information content of common ancestors divided by summed
        information content of all ancestors in profile a and profile b
        https://bmcbioinformatics.biomedcentral.com/track/
        pdf/10.1186/1471-2105-9-S5-S4

        Equivalent to jaccard if you were to replace 0s and 1s with
        information content
        """
        # Filter out negative phenotypes
        profile_a = {pheno for pheno in profile_a if not pheno[0] == "-"}
        profile_b = {pheno for pheno in profile_b if not pheno[0] == "-"}

        a_closure = self.graph.get_profile_closure(profile_a)
        b_closure = self.graph.get_profile_closure(profile_b)

        numerator = sum(
            [self.graph.ic_store.ic_map[pheno] for pheno in a_closure.intersection(b_closure)]
        )
        denominator = sum(
            [self.graph.ic_store.ic_map[pheno] for pheno in a_closure.union(b_closure)]
        )

        return numerator/denominator

    def _make_row(
            self,
            pheno_a: str,
            profile_b: Iterable,
            sim_measure: PairwiseSim = PairwiseSim.IC
    )-> List[float]:

        if sim_measure == PairwiseSim.GEOMETRIC:
            row = [metric.jac_ic_geomean(pheno_a, pheno_b, self.graph) for pheno_b in profile_b]
        elif sim_measure == PairwiseSim.IC:
            row = [self.graph.get_mica_ic(pheno_a, pheno_b) for pheno_b in profile_b]
        else:
            raise NotImplementedError

        return row

    def _get_score_matrix(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str],
            sim_measure: PairwiseSim = PairwiseSim.IC
    ) -> List[List[float]]:

        return [self._make_row(pheno_a, profile_b, sim_measure)
                for pheno_a in profile_a]

    def symmetric_resnik_bma(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str]
    ) -> float:
        return self.resnik_sim(profile_a, profile_b, is_symmetric=True)

    def cosine_ic_sim(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str],
            negative_weight: Optional[Num] = .1,
    ) -> float:
        """
        IC weighted cosine similarity (instead of vectors of 0/1 absent/present
        vectors are the information content values for each phenotype

        :param profile_a: Iterable of curies
        :param profile_b: Iterable of curies
        :param negative_weight: Vector weight for negative phenotypes (weight * ic)
        :return: cosine similarity score as a float between 0-1
        """
        graph_sim = GraphSemSim(self.graph)
        return graph_sim.cosine_sim(
            profile_a,
            profile_b,
            negative_weight,
            lambda term: self.graph.ic_store.ic_map[term]
        )

    def symmetric_phenodigm(
            self,
            profile_a: Iterable[str],
            profile_b: Iterable[str],
            is_same_species: Optional[bool] = True,
            sim_measure: Union[PairwiseSim, str, None] = PairwiseSim.GEOMETRIC
    ) -> float:
        return self.phenodigm_compare(
            profile_a, profile_b, True, is_same_species, sim_measure
        )

    def groupwise_sim_gic(
            self,
            profiles: Iterable[Iterable[str]]
    ) -> float:
        """
        sim_gic applied to greater than 2 profiles,
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

        numerator = sum(
            [self.graph.ic_store.ic_map[pheno] for pheno in profile_intersection]
        )
        denominator = sum(
            [self.graph.ic_store.ic_map[pheno] for pheno in profile_union]
        )

        return numerator/denominator

    def _get_optimal_matrix(
            self,
            profile: Iterable[str],
            is_same_species: Optional[bool] = True,
            sim_measure: Union[PairwiseSim, None] = PairwiseSim.IC
    ) -> List[List[float]]:
        """
        Only implemented for same species comparisons
        """
        score_matrix = []
        if is_same_species:
            for pheno in profile:
                if sim_measure == PairwiseSim.GEOMETRIC:
                    score_matrix.append(
                        [geometric_mean([1, self.graph.get_ic(pheno)])])
                elif sim_measure == PairwiseSim.IC:
                    score_matrix.append([self.graph.get_ic(pheno)])
                else:
                    raise NotImplementedError
        else:
            raise NotImplementedError
        return score_matrix
