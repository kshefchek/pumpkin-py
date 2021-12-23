"""
Search interface intended to be aligned with some REST API call
"""
import inspect
from typing import Dict, Iterable, List, Union

from pumpkin_py.graph.graph import Graph
from pumpkin_py.graph.ic_graph import ICGraph
from pumpkin_py.models.methods import ICMethod, SetMethod
from pumpkin_py.models.result import SearchResult, SimMatch
from pumpkin_py.sim.graph_semsim import GraphSemSim
from pumpkin_py.sim.ic_semsim import ICSemSim
from pumpkin_py.utils.ranker import RankMethod, rank_results


def search(
    profile: Iterable[str],
    dataset: Dict[str, Iterable[str]],
    graph: Union[ICGraph, Graph],
    method: Union[ICMethod, SetMethod, str] = ICMethod.phenodigm,
    rank_method: Union[RankMethod, str] = RankMethod.AVG,
    **kwargs,
) -> SearchResult:
    """

    :param profile: An iterable of ontology identifiers
    :param dataset: A dictionary where the key is the entity and the value is an iterable of ontology
                    ids (see output from builder.annotation_builder.flat_to_annotations)
    :param graph: A graph object that supports the semantic sim calculation, either an ICGraph or Graph
    :param method: Semantic sim method, see output from get_methods()
    :param rank_method: Method for ranking, either avg, min, max
    :param kwargs: Optional arguments specific to each algorithm,
                   TODO document and make it easier to inspect
    :return: SearchResult
    """

    search_result = SearchResult(results=[])

    if method == 'phenodigm':
        ic_sim = ICSemSim(graph)
        # Get the subset of keyword args that are available for this fx
        args = inspect.getfullargspec(ic_sim.phenodigm_compare)[0]
        new_kwargs = {k: v for k, v in kwargs.items() if k in args}
        for profile_id, profile_b in dataset.items():
            score = ic_sim.phenodigm_compare(profile, profile_b, **new_kwargs)
            result = SimMatch(id=profile_id, rank=0, score=score)
            search_result.results.append(result)

    elif method == 'symmetric_phenodigm':
        ic_sim = ICSemSim(graph)
        # Get the subset of keyword args that are available for this fx
        args = inspect.getfullargspec(ic_sim.symmetric_phenodigm)[0]
        new_kwargs = {k: v for k, v in kwargs.items() if k in args}
        for profile_id, profile_b in dataset.items():
            score = ic_sim.symmetric_phenodigm(profile, profile_b, **new_kwargs)
            result = SimMatch(id=profile_id, rank=0, score=score)
            search_result.results.append(result)

    elif method == 'resnik':
        ic_sim = ICSemSim(graph)
        # Get the subset of keyword args that are available for this fx
        args = inspect.getfullargspec(ic_sim.resnik_sim)[0]
        new_kwargs = {k: v for k, v in kwargs.items() if k in args}
        for profile_id, profile_b in dataset.items():
            score = ic_sim.resnik_sim(profile, profile_b, **new_kwargs)
            result = SimMatch(id=profile_id, rank=0, score=score)
            search_result.results.append(result)

    elif method == 'symmetric_resnik':
        ic_sim = ICSemSim(graph)

        for profile_id, profile_b in dataset.items():
            score = ic_sim.symmetric_resnik_bma(profile, profile_b)
            result = SimMatch(id=profile_id, rank=0, score=score)
            search_result.results.append(result)

    elif method == 'ic_cosine':
        ic_sim = ICSemSim(graph)
        # Get the subset of keyword args that are available for this fx
        args = inspect.getfullargspec(ic_sim.cosine_ic_sim)[0]
        new_kwargs = {k: v for k, v in kwargs.items() if k in args}
        for profile_id, profile_b in dataset.items():
            score = ic_sim.cosine_ic_sim(profile, profile_b, **new_kwargs)
            result = SimMatch(id=profile_id, rank=0, score=score)
            search_result.results.append(result)

    elif method == 'sim_gic':
        ic_sim = ICSemSim(graph)

        for profile_id, profile_b in dataset.items():
            score = ic_sim.sim_gic(profile, profile_b)
            result = SimMatch(id=profile_id, rank=0, score=score)
            search_result.results.append(result)

    elif method == 'jaccard':
        graph_sim = GraphSemSim(graph)

        for profile_id, profile_b in dataset.items():
            score = graph_sim.jaccard_sim(profile, profile_b)
            result = SimMatch(id=profile_id, rank=0, score=score)
            search_result.results.append(result)

    elif method == 'cosine':
        graph_sim = GraphSemSim(graph)
        # Get the subset of keyword args that are available for this fx
        args = inspect.getfullargspec(graph_sim.cosine_sim)[0]
        new_kwargs = {k: v for k, v in kwargs.items() if k in args}
        for profile_id, profile_b in dataset.items():
            score = graph_sim.cosine_sim(profile, profile_b, **new_kwargs)
            result = SimMatch(id=profile_id, rank=0, score=score)
            search_result.results.append(result)

    else:
        raise ValueError(f'{method} not supported')

    return rank_results(search_result, rank_method)


def get_methods() -> List[str]:
    return [member.value for member in SetMethod] + [member.value for member in ICMethod]
