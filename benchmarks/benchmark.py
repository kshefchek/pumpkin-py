from pathlib import Path
import timeit
import gzip

from pumpkin_py import PairwiseSim  # noqa
from pumpkin_py import ICSemSim,GraphSemSim, \
    flat_to_annotations, build_ic_graph_from_closures


closures = Path(__file__).parent / 'resources' / 'upheno-closures.tsv.gz'
annotations = Path(__file__).parent / 'resources' / 'all-annotations.tsv.gz'
g2p = Path(__file__).parent / 'resources' / 'Mm_gene_phenotype.txt.gz'

root = "UPHENO:0001001"

print("Loading closures")

with gzip.open(annotations, 'rt') as annot_file:
    annot_map = flat_to_annotations(annot_file)

with gzip.open(closures, 'rt') as closure_file:
    graph = build_ic_graph_from_closures(closure_file, root, annot_map)

with gzip.open(g2p, 'rt') as annot_file:
    mouse_genes = flat_to_annotations(annot_file)


ic_sim = ICSemSim(graph)
graph_sim = GraphSemSim(graph)

profile_a = "HP:0000403,HP:0000518,HP:0000565,HP:0000767," \
            "HP:0000872,HP:0001257,HP:0001263,HP:0001290," \
            "HP:0001629,HP:0002019,HP:0002072".split(',')

profile_b = "HP:0000496,HP:0005257,HP:0008773,HP:0010307," \
            "HP:0100017,HP:0001249".split(',')

for _ in range(2):
    # Run twice to see if caching speeds it up
    print('Running comparisons')

    print('phenodigm: ',
          timeit.timeit(
              stmt="for profile_b in mouse_genes.values(): ic_sim.phenodigm_compare(profile_a, profile_b, 'MP')",
              globals=globals(),
              number=1
          )
    )

    print('phenodigm no ns filter: ',
          timeit.timeit(
              stmt="for profile_b in mouse_genes.values(): ic_sim.phenodigm_compare(profile_a, profile_b)",
              globals=globals(),
              number=1
          )
    )

    print('resnik: ',
          timeit.timeit(
              stmt="for profile_b in mouse_genes.values(): ic_sim.resnik_sim(profile_a, profile_b)",
              globals=globals(),
              number=1
          )
    )

    print('jaccard: ',
          timeit.timeit(
              stmt="for profile_b in mouse_genes.values(): graph_sim.jaccard_sim(profile_a, profile_b)",
              globals=globals(),
              number=1
          )
    )

    print('cosine: ',
          timeit.timeit(
              stmt="for profile_b in mouse_genes.values(): graph_sim.cosine_sim(profile_a, profile_b)",
              globals=globals(),
              number=1
          )
    )

# print(ic_sim.phenodigm_compare(profile_a, profile_b, 'MP'))
# print(ic_sim.phenodigm_compare(profile_a, profile_b))
# print(ic_sim.resnik_sim(profile_a, profile_b))
# print(graph_sim.jaccard_sim(profile_a, profile_b))
# print(graph_sim.cosine_sim(profile_a, profile_b))
