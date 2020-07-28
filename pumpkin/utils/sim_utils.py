from typing import Optional, Iterable
from pyroaring import BitMap
from ..graph import Graph


def get_profile_closure(
        profile: Iterable[str],
        graph: Graph,
        negative: Optional[bool] = False
) -> BitMap:
    """
    Given a list of phenotypes, get the reflexive closure for each phenotype
    stored in a single set.  This can be used for jaccard similarity or
    simGIC

    This should probably be moved elsewhere as the loan fx here
    """
    return BitMap.union(
        *[graph.get_closure(node, negative=negative)
          for node in profile]
    )
