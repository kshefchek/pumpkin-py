from typing import List, Optional
from enum import Enum
from ..utils.math_utils import binomial_coeff
from ..models.Result import SimResult


class RankMethod(Enum):
    MIN = 'min'
    AVG = 'average'
    # not implemented MAX = 'max'


def rank_results(
        results: SimResult,
        method: Optional[RankMethod] = RankMethod.MIN
) -> SimResult:
    """
    Ranks results dealing with ties based on the RankMethod

    :param results: SimResult
    :param method: method used to rank results
    :return: Sorted results list
    """
    sorted_results = sorted(
        results, reverse=True, key=lambda k: k['score']
    )

    if len(sorted_results) > 0:
        rank = 1
        previous_score = sorted_results[0]['score']
        for result in sorted_results:
            if previous_score > result['score']:
                rank += 1
            result['rank'] = rank
            previous_score = result['score']
        if method == RankMethod.AVG:
            ranks = [res['rank'] for res in sorted_results]
            new_ranks = rerank_by_average(ranks)
            for index, result in enumerate(sorted_results):
                result['rank'] = new_ranks[index]


    return sorted_results


def average_ties(previous_rank: int, tie_count: int) -> int:
    deranked_summed = \
        binomial_coeff(previous_rank + (tie_count)) - \
        binomial_coeff(previous_rank)
    return round(deranked_summed / tie_count)


def rerank_ties(
        ranks: List[int],
        method: Optional[RankMethod] = RankMethod.MIN) -> List[int]:
    """
    Given a list of ranked results, penalizes tied scores
    by taking the average, for example, 4 classes
    tied for 1st will be given a rank of 2

    :return: List of ranks
    """
    # list to store adjusted ranks
    avg_ranks = []
    # Resolve ties, take the average rank
    last_rank = 1
    last_avg_rank = 0
    tie_count = 1
    is_first = True
    for rank in ranks[1:]:
        if rank > last_rank:
            if tie_count == 1:
                last_avg_rank += 1
                if is_first:
                    avg_ranks.append(1)
                    is_first = False
                else:
                    avg_ranks.append(last_avg_rank)
            else:
                avg_rank = average_ties(last_avg_rank, tie_count)
                tied_ranks = [avg_rank for n in range(tie_count)]
                avg_ranks.extend(tied_ranks)
                # reset tie count
                last_avg_rank = avg_rank
                tie_count = 1
        else:
            tie_count += 1
            is_first = False

        last_rank = rank

    if tie_count > 0:
        avg_rank = average_ties(last_avg_rank, tie_count)
        tied_ranks = [avg_rank for n in range(tie_count)]
        avg_ranks.extend(tied_ranks)
    else:
        last_avg_rank += 1
        avg_ranks.append(last_avg_rank)

    return avg_ranks


