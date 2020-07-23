from pathlib import Path
import timeit
import gzip
from pumpkin.io import flat_to_annotations, flat_to_graph
from pumpkin.sim.semantic_sim import SemanticSim, PairwiseSim


closures = Path(__file__).parent / 'resources' / 'upheno-closures.tsv.gz'
annotations = Path(__file__).parent / 'resources' / 'all-annotations.tsv.gz'
g2p = Path(__file__).parent / 'resources' / 'Mm_gene_phenotype.txt.gz'

root = "UPHENO:0001001"

print("Loading closures")

with gzip.open(annotations, 'rt') as annot_file:
    annot_map = flat_to_annotations(annot_file)

with gzip.open(closures, 'rt') as closure_file:
    graph = flat_to_graph(closure_file, root, annot_map)

with gzip.open(g2p, 'rt') as annot_file:
    mouse_genes = flat_to_annotations(annot_file)

print("Calculating information content")
graph.load_ic_map(annot_map)

semantic_sim = SemanticSim(graph)

profile_a = "HP:0000403,HP:0000518,HP:0000565,HP:0000767," \
            "HP:0000872,HP:0001257,HP:0001263,HP:0001290," \
            "HP:0001629,HP:0002019,HP:0002072".split(',')

profile_b = "HP:0000496,HP:0005257,HP:0008773,HP:0010307," \
            "HP:0100017,HP:0001249".split(',')

print('Running comparisons')


print('phenodigm: ',
      timeit.timeit(
          stmt="for profile_b in mouse_genes.values(): semantic_sim.phenodigm_compare(profile_a, profile_b, sim_measure=PairwiseSim.IC)",
          globals=globals(),
          number=1
      )
)

print('resnik: ',
      timeit.timeit(
          stmt="for profile_b in mouse_genes.values(): semantic_sim.resnik_sim(profile_a, profile_b)",
          globals=globals(),
          number=1
      )
)

print('jaccard: ',
      timeit.timeit(
          stmt="for profile_b in mouse_genes.values(): semantic_sim.jaccard_sim(profile_a, profile_b)",
          globals=globals(),
          number=1
      )
)

print('cosine: ',
      timeit.timeit(
          stmt="for profile_b in mouse_genes.values(): semantic_sim.cosine_sim(profile_a, profile_b)",
          globals=globals(),
          number=1
      )
)

print(semantic_sim.phenodigm_compare(profile_a, profile_b))
print(semantic_sim.resnik_sim(profile_a, profile_b))
print(semantic_sim.jaccard_sim(profile_a, profile_b))
print(semantic_sim.cosine_sim(profile_a, profile_b))
