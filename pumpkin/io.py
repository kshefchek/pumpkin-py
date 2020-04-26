from typing import Dict, Set, Tuple, TextIO
import csv


def flat_to_annotations(file: TextIO) -> Dict[str, Set[str]]:
    """
    Convert a two column file to an annotation dictionary
    :param file: text I/O stream such as returned by open()
    :return: annotations: Dict[str, Set[str]]
    """
    annotations = {}
    reader = csv.reader(file, delimiter='\t', quotechar='\"')
    for row in reader:
        if row[0].startswith('#'): continue
        (individual, cls) = row[0:2]
        try:
            annotations[individual].add(cls)
        except KeyError:
            annotations[individual] = {cls}

    return annotations


def flat_to_graph(
        file: TextIO,
        root: str
) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """
    Convert a two column file to map of ancestors and desecendants
    :param file: text I/O stream such as returned by open()
    :param root: root class as  curie formatted string
    :return: Tuple(ancestors, descendants) of two maps of type: Dict[str, Set[str]]
    """
    ancestors = {}
    descendants = {}
    reader = csv.reader(file, delimiter='\t', quotechar='\"')
    for row in reader:
        if row[0].startswith('?'): continue
        (iri_a, iri_b) = row[0:2]

        # Fast lazy uri to curie
        node_a = iri_a[1:-1].replace("http://purl.obolibrary.org/obo/", "").replace("_", ":")
        node_b = iri_b[1:-1].replace("http://purl.obolibrary.org/obo/", "").replace("_", ":")

        try:
            descendants[node_b].add(node_a)
        except KeyError:
            descendants[node_b] = {node_a}

        try:
            ancestors[node_a].add(node_b)
        except KeyError:
            ancestors[node_a] = {node_b}

    # Remove ancestors above the root (eg owl:Class, HP:0000001)
    for node in ancestors.keys():
        ancestors[node] = descendants[root] & ancestors[node]

    return ancestors, descendants
