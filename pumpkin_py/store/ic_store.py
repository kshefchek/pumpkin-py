from typing import Dict, NamedTuple

from bidict import bidict


class ICStore(NamedTuple):
    """
    Tuple for storing information content per class and optionally
    a cached array of micas between all classes
    """

    ic_map: Dict[int, float]
    id_map: bidict  # bidict[Dict[str, int]]
