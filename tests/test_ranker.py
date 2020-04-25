import pytest
from pumpkin.utils.ranker import rerank_ties, RankMethod


avg_rank_data = [
    (
        # Input rankings
        [1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 7, 8],
        # Expected output rankings
        [3, 3, 3, 3, 3, 4, 5, 6, 7, 9, 9, 9, 10, 11]
    ),
    (
        [1, 2, 2, 2, 2, 3, 3, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9],
        [1, 4, 4, 4, 4, 6, 6, 7, 8, 9, 10, 12, 12, 14, 14, 14, 14]
    ),
    (
        [1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 8, 8, 9, 9, 9, 10],
        [1, 2, 2, 4, 4, 6, 6, 8, 8, 10, 10, 11, 12, 12, 14, 14, 14, 15]
    ),
    (
        [1, 1, 2, 3],
        [2, 2, 3, 4]
    )
]

max_rank_data = [
    (
        # Input rankings
        [1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 7, 8],
        # Expected output rankings
        [5, 5, 5, 5, 5, 6, 7, 8, 9, 12, 12, 12, 13, 14]
    ),
    (
        [1, 2, 2, 2, 2, 3, 3, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9],
        [1, 5, 5, 5, 5, 7, 7, 8, 9, 10, 11, 13, 13, 17, 17, 17, 17]
    ),
    (
        [1, 1, 2, 3],
        [2, 2, 3, 4]
    )
]



@pytest.mark.parametrize("input_ranks, expected_ranks", avg_rank_data)
def test_reranking_by_avg(input_ranks, expected_ranks):
    """
    Test reranking by adjusting ties
    function: phenom.utils.simulate.rerank_by_average
    """
    rankings = rerank_ties(input_ranks, RankMethod.AVG)
    assert expected_ranks == rankings


@pytest.mark.parametrize("input_ranks, expected_ranks", max_rank_data)
def test_reranking_by_max(input_ranks, expected_ranks):
    """
    Test reranking by adjusting ties
    function: phenom.utils.simulate.rerank_by_average
    """
    rankings = rerank_ties(input_ranks, RankMethod.MAX)
    assert expected_ranks == rankings
