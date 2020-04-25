from typing import List, Optional
from enum import Enum
from ..utils.math_utils import binomial_coeff
from ..models.Result import SearchResult


class RankMethod(Enum):
    MIN = 'min'
    AVG = 'average'
    MAX = 'max'


def rank_results(
        search_result: SearchResult,
        method: Optional[RankMethod] = RankMethod.MIN
) -> SearchResult:
    """
    Ranks results dealing with ties based on the RankMethod

    :param search_result: SimResult
    :param method: method used to rank results
    :return: Sorted results list
    """
    sorted_results = sorted(
        search_result.results, reverse=True, key=lambda k: k['score']
    )

    if len(sorted_results) > 0:
        rank = 1
        previous_score = sorted_results[0]['score']
        for result in sorted_results:
            if previous_score > result['score']:
                rank += 1
            result['rank'] = rank
            previous_score = result['score']

        if method != RankMethod.MIN:
            ranks = [res['rank'] for res in sorted_results]
            new_ranks = rerank_ties(ranks, method)
            for index, result in enumerate(sorted_results):
                result['rank'] = new_ranks[index]

    search_result.results = sorted_results

    return search_result


def average_ties(previous_rank: int, tie_count: int) -> int:
    deranked_summed = \
        binomial_coeff(previous_rank + (tie_count)) - \
        binomial_coeff(previous_rank)
    return round(deranked_summed / tie_count)


def rerank_ties(
        ranks: List[int],
        method: Optional[RankMethod] = RankMethod.AVG
) -> List[int]:
    """
    Given a list of ranked results, penalizes tied scores
    by taking the average, for example, 4 classes
    tied for 1st will be given a rank of 2

    :return: List of ranks
    """
    # list to store adjusted ranks
    new_ranks = []
    # Resolve ties, take the average rank
    last_rank = 1
    last_new_rank = 0
    tie_count = 1
    is_first = True
    for rank in ranks[1:]:
        if rank > last_rank:
            if tie_count == 1:
                last_new_rank += 1
                if is_first:
                    new_ranks.append(1)
                    is_first = False
                else:
                    new_ranks.append(last_new_rank)
            else:
                adj_ranks = []
                new_rank = None
                if method == RankMethod.AVG:
                    new_rank = average_ties(last_new_rank, tie_count)
                elif method == RankMethod.MAX:
                    # could also take current index + 1
                    new_rank = last_new_rank + tie_count

                adj_ranks = [new_rank for n in range(tie_count)]
                new_ranks.extend(adj_ranks)
                # reset tie count
                last_new_rank = new_rank
                tie_count = 1
        else:
            tie_count += 1
            is_first = False

        last_rank = rank

    if tie_count > 0:
        adj_ranks = []
        new_rank = None
        if method == RankMethod.AVG:
            new_rank = average_ties(last_new_rank, tie_count)
        elif method == RankMethod.MAX:
            new_rank = last_new_rank + tie_count

        adj_ranks = [new_rank for n in range(tie_count)]
        new_ranks.extend(adj_ranks)
    else:
        last_new_rank += 1
        new_ranks.append(last_new_rank)

    return new_ranks
