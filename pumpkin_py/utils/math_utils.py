import math
from typing import Union

import numpy as np

# Union type for numbers
Num = Union[int, float]


def information_content(frequency: Num) -> float:
    if frequency == 0 or frequency == 1:
        ic = float(0)
    else:
        ic = -(math.log(frequency))
    return ic


def binomial_coeff(num) -> float:
    return (num * (num + 1)) / 2


def np_geometric_mean(iterable):
    """https://stackoverflow.com/a/43099751"""
    a = np.array(iterable)
    return a.prod() ** (1.0 / len(a))
