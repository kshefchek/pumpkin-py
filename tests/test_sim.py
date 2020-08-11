from pumpkin.sim.semantic_dist import SemanticDist
from pumpkin.sim.ic_semsim import ICSemSim
from pumpkin.sim.graph_semsim import GraphSemSim
from pumpkin.builder.annotation_builder import flat_to_annotations
from pumpkin.builder.graph_builder import build_ic_graph_from_closures, build_graph_from_rdflib
from pathlib import Path


ontology = Path(__file__).parent / 'resources' / 'ontology.ttl'
closures = Path(__file__).parent / 'resources' / 'closures.tsv'
annotations = Path(__file__).parent / 'resources' / 'annotations.tsv'
epsilon = 1e-3


class TestGraphSimWithRDFGraph():

    @classmethod
    def setup_class(self):
        root = "HP:0000118"
        self.graph = build_graph_from_rdflib(iri=ontology.as_uri(), root=root)

        with open(annotations, 'r') as annot_file:
            self.annot_map = flat_to_annotations(annot_file)

        self.graph_semsim = GraphSemSim(self.graph)
        print(self.graph.ancestors[root])

    @classmethod
    def teardown_class(self):
        self.graph = None

    def test_jaccard(self):
        expected = .3
        profile_a = self.annot_map['1']
        profile_b = self.annot_map['2']
        jaccard_sim = self.graph_semsim.jaccard_sim(profile_a, profile_b)
        assert abs(jaccard_sim - expected) < epsilon


class TestICSimWithClosureGraph():

    @classmethod
    def setup_class(self):
        root = "HP:0000118"

        with open(annotations, 'r') as annot_file:
            self.annot_map = flat_to_annotations(annot_file)

        with open(closures, 'r') as closure_file:
            self.graph = build_ic_graph_from_closures(closure_file, root, self.annot_map)

        self.semantic_sim = ICSemSim(self.graph)
        self.semantic_dist = SemanticDist(self.graph)

    @classmethod
    def teardown_class(self):
        self.graph = None

    def test_resnik(self):
        expected = .693
        profile_a = self.annot_map['1']
        profile_b = self.annot_map['2']
        resnik_sim = self.semantic_sim.resnik_sim(profile_a, profile_b)
        assert abs(resnik_sim - expected) < epsilon
