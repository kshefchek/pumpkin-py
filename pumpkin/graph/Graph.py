from abc import ABCMeta, abstractmethod
from typing import Optional, Set, Dict


class Graph(metaclass=ABCMeta):
    """
    Interface for a graph object that contains methods
    for traversing ancestors, descendants, and storing
    information content about classes
    """
    ic_map: Dict[str, float]

    @abstractmethod
    def load_ic_map(self):
        """
        Initializes ic_map
        """
        pass

    @abstractmethod
    def get_closure(self, node: str, negative: Optional[bool] = False) -> Set[str]:
        pass

    @abstractmethod
    def get_descendants(self, node: str) -> Set[str]:
        pass

    @abstractmethod
    def get_ancestors(self,  node: str) -> Set[str]:
        pass
