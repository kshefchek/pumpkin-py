"""
TODO , a lot of DRY violation in here, parameterize these tests
https://docs.pytest.org/en/6.2.x/parametrize.html
"""

from pathlib import Path

import pytest

from pumpkin_py import MatrixMetric  # noqa
from pumpkin_py import PairwiseSim  # noqa
from pumpkin_py import (
    GraphSemSim,
    ICSemSim,
    SemanticDist,
    build_graph_from_closure_file,
    build_graph_from_rdflib,
    build_ic_graph_from_closures,
    build_ic_graph_from_iri,
    flat_to_annotations,
)

ontology = Path(__file__).parent / 'resources' / 'mock-hpo' / 'ontology.ttl'
closures = Path(__file__).parent / 'resources' / 'mock-hpo' / 'closures.tsv'
annotations = Path(__file__).parent / 'resources' / 'mock-hpo' / 'annotations.tsv'

with open(annotations, 'r') as annot_file:
    annotation_map = flat_to_annotations(annot_file)

epsilon = 1e-3

graph_sim_tests = [
    ("self.graph_semsim.jaccard_sim(annotation_map['1'], annotation_map['2'])", 0.3),
    ("self.graph_semsim.cosine_sim(annotation_map['1'], annotation_map['2'])", 0.474),
]

ic_sim_tests = [
    ("self.semantic_sim.resnik_sim(annotation_map['1'], annotation_map['2'])", 0.693),
    (
        "self.semantic_sim.resnik_sim(annotation_map['1'], annotation_map['2'], matrix_metric=MatrixMetric.MAX)",
        1.386,
    ),
    (
        "self.semantic_sim.resnik_sim(annotation_map['1'], annotation_map['2'], matrix_metric=MatrixMetric.AVG)",
        0.346,
    ),
    ("self.semantic_sim.symmetric_resnik_bma(annotation_map['1'], annotation_map['2'])", 0.596),
    ("self.semantic_sim.phenodigm_compare(annotation_map['1'], annotation_map['2'])", 48.707),
    (
        "self.semantic_sim.phenodigm_compare(annotation_map['1'], annotation_map['2'], sim_measure=PairwiseSim.IC)",
        51.515,
    ),
    ("self.semantic_sim.sim_gic(annotation_map['1'], annotation_map['2'])", 0.157),
    ("self.semantic_sim.symmetric_phenodigm(annotation_map['1'], annotation_map['2'])", 53.700),
    ("self.semantic_sim.cosine_ic_sim(annotation_map['1'], annotation_map['2'])", 0.234),
]

# TODO semantic distance tests


class TestGraphSimWithRDFGraph:
    @classmethod
    def setup_class(self):
        root = "HP:0000118"
        self.graph = build_graph_from_rdflib(iri=ontology.as_uri(), root=root)

        self.graph_semsim = GraphSemSim(self.graph)
        print(self.graph.ancestors[root])

    @classmethod
    def teardown_class(self):
        self.graph = None

    @pytest.mark.parametrize('test_fx,expected', graph_sim_tests)
    def test_graph_sim(self, test_fx, expected):
        sim_score = eval(test_fx)
        assert abs(sim_score - expected) < epsilon


class TestICSimWithRDFGraph:
    @classmethod
    def setup_class(self):
        root = "HP:0000118"
        self.graph = build_ic_graph_from_iri(
            iri=ontology.as_uri(), annotations=annotation_map, root=root
        )

        self.semantic_sim = ICSemSim(self.graph)
        print(self.graph.ancestors[root])

    @classmethod
    def teardown_class(self):
        self.graph = None

    @pytest.mark.parametrize('test_fx,expected', ic_sim_tests)
    def test_ic_sim(self, test_fx, expected):
        sim_score = eval(test_fx)
        assert abs(sim_score - expected) < epsilon


class TestICSimWithClosureFile:
    @classmethod
    def setup_class(self):
        root = "HP:0000118"

        with open(closures, 'r') as closure_file:
            self.graph = build_ic_graph_from_closures(closure_file, root, annotation_map)

        self.semantic_sim = ICSemSim(self.graph)
        self.semantic_dist = SemanticDist(self.graph)

    @classmethod
    def teardown_class(self):
        self.graph = None

    @pytest.mark.parametrize('test_fx,expected', ic_sim_tests)
    def test_ic_sim(self, test_fx, expected):
        sim_score = eval(test_fx)
        assert abs(sim_score - expected) < epsilon


class TestGraphSimWithClosureFile:
    """
    TODO parameterize these tests
    https://docs.pytest.org/en/6.2.x/parametrize.html
    """

    @classmethod
    def setup_class(self):
        root = "HP:0000118"

        with open(closures, 'r') as closure_file:
            self.graph = build_graph_from_closure_file(closure_file, root)

        self.graph_semsim = GraphSemSim(self.graph)

    @classmethod
    def teardown_class(self):
        self.graph = None

    @pytest.mark.parametrize('test_fx,expected', graph_sim_tests)
    def test_graph_sim(self, test_fx, expected):
        sim_score = eval(test_fx)
        assert abs(sim_score - expected) < epsilon
