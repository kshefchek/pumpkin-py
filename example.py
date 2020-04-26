from pumpkin.graph.CacheGraph import CacheGraph
from pumpkin.io import flat_to_annotations, flat_to_graph
from pumpkin.sim.semantic_sim import SemanticSim, PairwiseSim
from pathlib import Path
import timeit

closures = Path(__file__).parent / 'resources' / 'closures' / 'upheno-closures.tsv'
annotations = Path(__file__).parent / 'resources' / 'annotations' /\
              'all-annotations.tsv'

root = "UPHENO:0001001"

print("Loading closures")

with open(closures, 'r') as closure_file:
    id_map, ancestors, descendants = flat_to_graph(closure_file, root)

graph = CacheGraph(root, id_map, ancestors, descendants)

print("Calculating information content")
with open(annotations, 'r') as annot_file:
    annot_map = flat_to_annotations(annot_file)

graph.load_ic_map(annot_map)

semantic_sim = SemanticSim(graph)

profile_a = "HP:0000403,HP:0000518,HP:0000565,HP:0000767," \
            "HP:0000872,HP:0001257,HP:0001263,HP:0001290," \
            "HP:0001629,HP:0002019,HP:0002072".split(',')

profile_b = "HP:0000496,HP:0005257,HP:0008773,HP:0010307," \
            "HP:0100017,HP:0001249".split(',')

print('phenodigm: ', timeit.timeit(
    stmt="semantic_sim.phenodigm_compare(profile_a, profile_b)",
    globals=globals(),
    number=10000)
)

print('jaccard: ', timeit.timeit(
    stmt="semantic_sim.jaccard_sim(profile_a, profile_b)",
    globals=globals(),
    number=10000)
)

print(semantic_sim.phenodigm_compare(profile_a, profile_b))
print(semantic_sim.jaccard_sim(profile_a, profile_b))
