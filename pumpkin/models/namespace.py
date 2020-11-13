from enum import Enum


class Namespace(Enum):
    HP          = 1
    MP          = 2
    ZP          = 3
    FBcv        = 4
    WBPhenotype = 5


namespace = {
    Namespace.HP: 'HP',
    Namespace.MP: 'MP',
    Namespace.ZP: 'ZP',
    Namespace.FBcv: 'FBcv',
    Namespace.WBPhenotype: 'WBPhenotype',
}
