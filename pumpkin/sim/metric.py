from typing import Union
from ..utils.math_utils import geometric_mean
from ..utils.sim_utils import get_mica_ic
from ..graph import Graph
import math
from pyroaring import BitMap


# Union type for numbers
Num = Union[int, float]


def jaccard(set1: BitMap, set2: BitMap) -> float:
    return set1.jaccard_index(set2)


def pairwise_jaccard(pheno_a: str, pheno_b: str, graph: Graph) -> float:
    return jaccard(
        graph.get_closure(pheno_a),
        graph.get_closure(pheno_b)
    )


def pairwise_euclidean(
        pheno_a: str,
        pheno_b: str,
        graph: Graph
) -> float:
    """
    sqrt ( pow(IC(a) - MICA, 2) + pow(IC(b) - MICA), 2) )
    """
    max_ic = get_mica_ic(pheno_a, pheno_b, graph)
    ic_a = graph.get_ic(pheno_a)
    ic_b = graph.get_ic(pheno_b)
    return math.sqrt(math.pow(ic_a - max_ic, 2) + math.pow(ic_b - max_ic, 2))


def jin_conrath_distance(
        pheno_a: str,
        pheno_b: str,
        graph: Graph
) -> float:
    """
    Jin Conrath distance

    IC(a) + IC (b) - 2 IC(MICA(a,b))
    """
    max_ic = get_mica_ic(pheno_a, pheno_b, graph)
    ic_a = graph.get_ic(pheno_a)
    ic_b = graph.get_ic(pheno_b)
    return ic_a + ic_b - 2 * max_ic


def jac_ic_geomean(
        pheno_a: str,
        pheno_b: str,
        graph: Graph
) -> float:
    jaccard_sim = pairwise_jaccard(pheno_a, pheno_b, graph)
    mica = get_mica_ic(pheno_a, pheno_b, graph)
    return geometric_mean([jaccard_sim, mica])
