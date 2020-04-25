from typing import Set, Optional, Iterable
from itertools import chain
from ..graph import Graph


def get_mica_ic(
        pheno_a: str,
        pheno_b: str,
        graph: Graph
) -> float:
    p1_closure = graph.get_closure(pheno_a)
    p2_closure = graph.get_closure(pheno_b)
    return max([graph.ic_map[parent]for parent in p1_closure.intersection(p2_closure)])


def get_mica_id(
        pheno_a: str,
        pheno_b: str,
        graph: Graph,
) -> str:
    """
    Return ID of most informative common anscestor of two phenotypes
    Currently does not handle ambiguity (>1 equal MICAs)
    """
    p1_closure = graph.get_closure(pheno_a)
    p2_closure = graph.get_closure(pheno_b)
    overlap = p1_closure.intersection(p2_closure)
    max_ic = max([graph.ic_map[parent]for parent in overlap])
    mica = ''
    for pheno in overlap:
        if graph.ic_map[pheno] == max_ic:
            mica = pheno
    return mica


def get_profile_closure(
        profile: Iterable[str],
        graph: Graph,
        negative: Optional[bool] = False
) -> Set[str]:
    """
    Given a list of phenotypes, get the reflexive closure for each phenotype
    stored in a single set.  This can be used for jaccard similarity or
    simGIC
    """
    return set(chain.from_iterable(
        [graph.get_closure(node, negative=negative)
         for node in profile])
    )
