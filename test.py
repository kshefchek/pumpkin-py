from pumpkin.graph.CacheGraph import CacheGraph
from pumpkin.io import flat_to_annotations, flat_to_graph
from pathlib import Path

closures = Path(__file__).parent / 'resources' / 'closures' / 'upheno-closures.tsv'
annotations = Path(__file__).parent / 'resources' / 'annotations' /\
              'Homo_sapiens' / 'Hs_disease_phenotype.txt'

root = "UPHENO:0001001"

print("Loading closures")

with open(closures, 'r') as closure_file:
    ancestors, descendants = flat_to_graph(closure_file, root)

graph = CacheGraph(root, ancestors, descendants)

print("Calculating information content")
with open(annotations, 'r') as annot_file:
    annot_map = flat_to_annotations(annot_file)

graph.load_ic_map(annot_map)
