from enum import Enum


class Dataset(str, Enum):
    DISEASE        = 'DISEASE'
    MOUSE_GENE     = 'MOUSE_GENE'
    ZFISH_GENE     = 'ZFISH_GENE'
    FLY_GENE       = 'FLY_GENE'
    WORM_GENE      = 'WORM_GENE'
    CASE           = 'CASE'
    MOUSE_GENOTYPE = 'MOUSE_GENOTYPE'
    ZFISH_GENOTYPE = 'ZFISH_GENOTYPE'
    FLY_ALLELE     = 'FLY_ALLELE'
    ALL            = 'ALL'
