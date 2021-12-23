"""
Semantic sim and distance methods enumerated, should probably rename this python file
"""

from enum import Enum


class ICMethod(str, Enum):
    phenodigm = 'phenodigm'
    symmetric_phenodigm = 'symmetric_phenodigm'
    resnik = 'resnik'
    symmetric_resnik = 'symmetric_resnik'
    ic_cosine = 'ic_cosine'
    sim_gic = 'sim_gic'


class SetMethod(str, Enum):
    jaccard = 'jaccard'
    cosine = 'cosine'
