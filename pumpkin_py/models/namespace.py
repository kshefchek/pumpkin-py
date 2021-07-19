from enum import Enum


class Namespace(str, Enum):
    HP = 'HP'
    MP = 'MP'
    ZP = 'ZP'
    FBcv = 'FBcv'
    WBPhenotype = 'WBPhenotype'
