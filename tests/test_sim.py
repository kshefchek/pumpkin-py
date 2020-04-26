from pumpkin.graph.RDFGraph import RDFGraph
from pumpkin.graph.CacheGraph import CacheGraph
from pumpkin.io import flat_to_annotations, flat_to_graph
from pumpkin.sim.semantic_dist import SemanticDist
from pumpkin.sim.semantic_sim import SemanticSim
from pathlib import Path


ontology = Path(__file__).parent / 'resources' / 'ontology.ttl'
closures = Path(__file__).parent / 'resources' / 'closures.tsv'
annotations = Path(__file__).parent / 'resources' / 'annotations.tsv'
epsilon = 1e-3


class TestSemanticWithRDFGraph():

    @classmethod
    def setup_class(self):
        root = "HP:0000118"
        self.graph = RDFGraph(root=root, iri=ontology.as_uri())

        with open(annotations, 'r') as annot_file:
            self.annot_map = flat_to_annotations(annot_file)

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


class TestSemanticWithCacheGraph():

    @classmethod
    def setup_class(self):
        root = "HP:0000118"

        with open(closures, 'r') as closure_file:
            ancestors, descendants = flat_to_graph(closure_file, root)

        self.graph = CacheGraph(root, ancestors, descendants)

        with open(annotations, 'r') as annot_file:
            self.annot_map = flat_to_annotations(annot_file)

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
