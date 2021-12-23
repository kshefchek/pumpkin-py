"""
Top level package
"""

from .builder.annotation_builder import flat_to_annotations
from .builder.graph_builder import (
    build_graph_from_closure_file,
    build_graph_from_rdflib,
    build_ic_graph_from_closures,
    build_ic_graph_from_iri,
)
from .graph.graph import Graph
from .graph.ic_graph import ICGraph
from .sim.graph_semsim import GraphSemSim
from .sim.ic_semsim import ICSemSim, MatrixMetric, PairwiseSim
from .sim.search import get_methods, search
from .sim.semantic_dist import SemanticDist
from .utils.ranker import RankMethod, rerank_ties
