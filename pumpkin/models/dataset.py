from enum import Enum


class Dataset(Enum):
    DISEASE        = 1
    MOUSE_GENE     = 2
    ZFISH_GENE     = 3
    FLY_GENE       = 4
    WORM_GENE      = 5
    CASE           = 6
    MOUSE_GENOTYPE = 7
    ZFISH_GENOTYPE = 8
    FLY_ALLELE     = 9
    ALL            = 10
