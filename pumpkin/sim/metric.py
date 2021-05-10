from typing import Union, Optional
import math
from statistics import geometric_mean
from functools import lru_cache

from pyroaring import FrozenBitMap

from ..graph.ic_graph import ICGraph
from ..models.namespace import Namespace

from diskcache import Cache
import tempfile

cache = Cache(tempfile.gettempdir())


# Union type for numbers
Num = Union[int, float]


def jaccard(set1: FrozenBitMap, set2: FrozenBitMap) -> float:
    return set1.jaccard_index(set2)


@lru_cache(maxsize=None)
def mica_ic(
        pheno_a: str,
        pheno_b: str,
        graph: ICGraph,
        ns_filter: Optional[Namespace] = None
) -> float:
    return graph.get_mica_ic(pheno_a, pheno_b, ns_filter)


#@lru_cache(maxsize=None)
def pairwise_jaccard(
        pheno_a: str,
        pheno_b: str,
        graph: ICGraph,
        ns_filter: Optional[Namespace] = None
) -> float:
    """
    Pairwise jaccard between two ids

    Namespace filter applies only to pheno_b, and looks up
    the nearest mica with the namespace and uses that node
    to compute the jaccard index
    """

    if ns_filter:
        # requires ICGraph
        ns_filtered_b = graph.get_mica_id(pheno_a, pheno_b, ns_filter)
        jaccard_sim = jaccard(
            graph.get_closure(pheno_a),
            graph.get_closure(ns_filtered_b)
        )
    else:
        jaccard_sim = jaccard(
            graph.get_closure(pheno_a),
            graph.get_closure(pheno_b)
        )
    return jaccard_sim


def pairwise_euclidean(
        pheno_a: str,
        pheno_b: str,
        graph: ICGraph
) -> float:
    """
    sqrt ( pow(IC(a) - MICA, 2) + pow(IC(b) - MICA), 2) )
    """
    max_ic = graph.get_mica_ic(pheno_a, pheno_b)
    ic_a = graph.get_ic(pheno_a)
    ic_b = graph.get_ic(pheno_b)
    return math.sqrt(math.pow(ic_a - max_ic, 2) + math.pow(ic_b - max_ic, 2))


def jin_conrath_distance(
        pheno_a: str,
        pheno_b: str,
        graph: ICGraph
) -> float:
    """
    Jin Conrath distance

    IC(a) + IC (b) - 2 IC(MICA(a,b))
    """
    max_ic = graph.get_mica_ic(pheno_a, pheno_b)
    ic_a = graph.get_ic(pheno_a)
    ic_b = graph.get_ic(pheno_b)
    return ic_a + ic_b - 2 * max_ic


@lru_cache(maxsize=None)
def jac_ic_geomean(
        pheno_a: str,
        pheno_b: str,
        graph: ICGraph,
        ns_filter: Optional[Namespace] = None
) -> float:
    jaccard_sim = pairwise_jaccard(pheno_a, pheno_b, graph, ns_filter)
    mica = graph.get_mica_ic(pheno_a, pheno_b, ns_filter)
    return jaccard_ic_geometric_mean(jaccard_sim, mica)


@lru_cache(maxsize=None)
def jaccard_ic_geometric_mean(jaccard_sim: Num, mica: Num) -> float:
    geom_mean = 0
    if jaccard_sim != 0 and mica != 0:
        geom_mean = geometric_mean([jaccard_sim, mica])
    return geom_mean
