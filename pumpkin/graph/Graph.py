from abc import ABCMeta, abstractmethod
from typing import Optional, Set, Dict
from ..utils.math_utils import information_content


class Graph(metaclass=ABCMeta):
    """
    Interface for a graph object that contains methods
    for traversing ancestors, descendants, and storing
    information content about classes
    """
    root: str
    ic_map: Dict[str, float]

    def get_closure(self, node: str, negative: Optional[bool] = False) -> Set[str]:
        if negative:
            nodes = self.get_descendants(node)
        else:
            nodes = self.get_ancestors(node)
        return nodes

    def load_ic_map(self, annotations: Dict[str, Set[str]]):
        """
        Initializes ic_map
        """
        explicit_annotations = 0
        node_annotations = {node: 0 for node in self.get_descendants(self.root)}
        for profile in annotations.values():
            for node in profile:
                explicit_annotations += 1
                for cls in self.get_ancestors(node):
                    node_annotations[cls] += 1

        # laplacian smoothing
        for node, annot_count in node_annotations.items():
            if annot_count == 0:
                explicit_annotations += 1
                for ancestor in self.get_ancestors(node):
                    node_annotations[ancestor] += 1

        for node, annot_count in node_annotations.items():
            self.ic_map[node] = information_content(annot_count / explicit_annotations)


    @abstractmethod
    def get_descendants(self, node: str) -> Set[str]:
        pass

    @abstractmethod
    def get_ancestors(self,  node: str) -> Set[str]:
        pass
