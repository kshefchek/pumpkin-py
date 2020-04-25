from enum import Enum


class Datasets(Enum):
    DISEASES    = 'diseases'
    MOUSE_GENES = 'mouse_genes'
    ZFISH_GENES = 'zfish_genes'
    FLY_GENES   = 'fly_genes'
    WORM_GENES  = 'worm_genes'
    CASES       = 'cases'
