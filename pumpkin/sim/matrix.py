from typing import Union, Sequence, Iterator, Tuple, Any
from itertools import chain
import numpy as np


# Union types
Num = Union[int, float]


def flip_matrix(matrix: Sequence[Sequence]) -> Iterator[Tuple[Any]]:
    """
    swap rows and columns in a list of lists, ie transpose
    zip is faster than np.transpose or for loops
    """
    return zip(*matrix)


def max_score(matrix: Sequence[Sequence[Num]]) -> float:
    return max(list(chain.from_iterable(matrix)))


def sym_bma_score(matrix: Sequence[Sequence[Num]]) -> np.ndarray:
    """
    symmetric best max average score
    """
    forwards = [max(row) for row in matrix]
    flipped = flip_matrix(matrix)
    backwards = [max(row) for row in flipped]
    return np.mean([*forwards, *backwards], dtype=np.float64)


def bma_score(matrix: Sequence[Sequence[Num]]) -> np.ndarray:
    """
    best max average score
    """
    return np.mean([max(row) for row in matrix], dtype=np.float64)


def best_min_avg(matrix: Sequence[Sequence[Num]]) -> np.ndarray:
    """
    best min average score
    """
    return np.mean(
        [min(row) for row in matrix],
        dtype=np.float64
    )


def avg_score(matrix: Sequence[Sequence[Num]]) -> np.ndarray:
    """
    average of every value in the matrix
    """
    return np.mean(
        list(chain.from_iterable(matrix)),
        dtype=np.float64
    )


def max_percentage_score(
        query_matrix: Sequence[Sequence[Num]],
        optimal_matrix: Sequence[Sequence[float]]) -> float:
    return max_score(query_matrix) / max_score(optimal_matrix)


def bma_percentage_score(
        query_matrix: Sequence[Sequence[Num]],
        optimal_matrix: Sequence[Sequence[Num]]) -> float:
    return bma_score(query_matrix) / bma_score(optimal_matrix)


def sym_bma_percentage_score(
        query_matrix: Sequence[Sequence[Num]],
        optimal_matrix: Sequence[Sequence[Num]]) -> float:
    return sym_bma_score(query_matrix) / sym_bma_score(optimal_matrix)


def avg_percentage_score(
        query_matrix: Sequence[Sequence[Num]],
        optimal_matrix: Sequence[Sequence[Num]]) -> float:
    return avg_score(query_matrix) / avg_score(optimal_matrix)
