from typing import Dict, Set, TextIO
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
