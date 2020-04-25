from pumpkin.graph.RDFGraph import RDFGraph
from pumpkin.io.io import two_col_to_annotations
from pumpkin.sim.semantic_dist import SemanticDist
from pumpkin.sim.semantic_sim import SemanticSim
from pathlib import Path


ontology = Path(__file__).parent / 'resources' / 'ontology.ttl'
annotations = Path(__file__).parent / 'resources' / 'annotations.tsv'
epsilon = 1e-3

class TestSemanticStar():

    @classmethod
    def setup_class(self):
        root = "HP:0000118"
        self.graph = RDFGraph(root=root, iri=ontology.as_uri())
        self.annot_map = two_col_to_annotations(annotations)
        self.graph.load_ic_map(self.annot_map)
        self.semantic_sim = SemanticSim(self.graph)
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

