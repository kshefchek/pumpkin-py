from typing import Optional, Iterable
from pyroaring import BitMap, FrozenBitMap
from ..graph import Graph


def get_mica_ic(
        pheno_a: str,
        pheno_b: str,
        graph: Graph
) -> float:
    if graph.is_ordered:
        try:
            p1_closure = graph.ancestors[pheno_a]
            p2_closure = graph.ancestors[pheno_b]
            mica = graph.ic_map[p1_closure.intersection(p2_closure).max()]
        except KeyError:
            mica = 0
        except ValueError:
            mica = 0

    else:
        mica = max(
            [graph.ic_map[parent]
             for parent in graph
                 .get_ancestors(pheno_a)
                 .intersection(graph.get_ancestors(pheno_b))
             ],
            default=0
        )

    return mica


def get_mica_id(
        pheno_a: str,
        pheno_b: str,
        graph: Graph,
) -> str:
    """
    Return ID of most informative common anscestor of two phenotypes
    Currently does not handle ambiguity (>1 equal MICAs)
    """
    p1_closure = graph.get_ancestors(pheno_a)
    p2_closure = graph.get_ancestors(pheno_b)
    overlap = p1_closure.intersection(p2_closure)
    max_ic = max([graph.ic_map[parent] for parent in overlap])
    mica = ''
    for pheno in overlap:
        if graph.ic_map[pheno] == max_ic:
            mica = pheno
    return mica


def get_profile_closure(
        profile: Iterable[str],
        graph: Graph,
        negative: Optional[bool] = False
) -> BitMap:
    """
    Given a list of phenotypes, get the reflexive closure for each phenotype
    stored in a single set.  This can be used for jaccard similarity or
    simGIC
    """
    return BitMap.union(
        *[graph.get_closure(node, negative=negative)
          for node in profile]
    )
