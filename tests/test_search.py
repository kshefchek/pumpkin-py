import gzip
from pathlib import Path

from pumpkin_py import build_ic_graph_from_closures, flat_to_annotations, search

closures = Path(__file__).parents[1] / 'data' / 'hpo' / 'hp-closures.tsv.gz'
annotations = Path(__file__).parents[1] / 'data' / 'hpo' / 'phenotype-annotations.tsv.gz'


def test_search():
    root = "HP:0000118"

    with gzip.open(annotations, 'rt') as annot_file:
        annot_map = flat_to_annotations(annot_file)

    with gzip.open(closures, 'rt') as closure_file:
        graph = build_ic_graph_from_closures(closure_file, root, annot_map)

    profile_a = (
        "HP:0000403,HP:0000518,HP:0000565,HP:0000767,"
        "HP:0000872,HP:0001257,HP:0001263,HP:0001290,"
        "HP:0001629,HP:0002019,HP:0002072".split(',')
    )

    search_results = search(profile_a, annot_map, graph, 'phenodigm')

    assert search_results.results[0].id == 'ORPHA:94125'
    assert search_results.results[0].score > 50
    assert search_results.results[0].rank == 1
