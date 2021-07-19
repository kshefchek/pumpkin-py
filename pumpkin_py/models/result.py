from dataclasses import dataclass
from typing import List, Union


@dataclass
class Node:
    """
    Basic node
    """

    id: str
    label: str


@dataclass
class ICNode(Node):
    """
    Node with information content
    """

    ic: float


@dataclass
class TypedNode(Node):
    """
    Node with type and optional taxon
    """

    type: str
    label: str
    taxon: Node


@dataclass
class SimMatch(TypedNode):
    """
    Data class similarity match
    """

    rank: Union[int, str]
    score: Union[float, int]


@dataclass
class SearchResult:
    """
    Data class a list of similarity matches
    """

    results: List[SimMatch]
