from enum import Enum


class Namespace(Enum):
    UPHENO = 1
    HP = 2
    MP = 3
    ZP = 4
    FBcv = 5
    WBPhenotype = 6


namespace = {
    Namespace.UPHENO: 'UPHENO',
    Namespace.HP: 'HP',
    Namespace.MP: 'MP',
    Namespace.ZP: 'ZP',
    Namespace.FBcv: 'FBcv',
    Namespace.WBPhenotype: 'WBPhenotype',
}
