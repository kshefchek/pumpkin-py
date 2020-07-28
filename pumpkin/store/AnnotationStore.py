from dataclasses import dataclass
from typing import Dict, Set
from ..models.Dataset import Dataset


@dataclass
class AnnotationStore():
    """
    Named tuple storing information content per class and optionally
    a cached array of micas between all classes
    """
    store: Dict[Dataset, Dict[str, Set[str]]]
    id_label: Dict[str, str]
