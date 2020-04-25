from typing import Dict, Set
import csv


def two_col_to_annotations(file_path: str) -> Dict[str, Set[str]]:
    """
    Convert a two column file to an annotation dictionary
    :param file_path: path to the file
    :return: annotations: Dict[str, Set[str]]
    """
    annotations = {}
    with open(file_path, 'r') as annot_file:
        reader = csv.reader(annot_file, delimiter='\t', quotechar='\"')
        for row in reader:
            if row[0].startswith('#'): continue
            (individual, cls) = row[0:2]
            if individual in annotations:
                annotations[individual].add(cls)
            else:
                annotations[individual] = {cls}

    return annotations
