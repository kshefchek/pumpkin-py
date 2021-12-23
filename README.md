[![Pyversions](https://img.shields.io/pypi/pyversions/pumpkin-py.svg)](https://pypi.python.org/pypi/koza)
![](https://github.com/kshefchek/pumpkin-py/actions/workflows/test.yml/badge.svg)
[![PyPi](https://img.shields.io/pypi/v/pumpkin-py.svg)](https://pypi.python.org/pypi/pumpkin-py)

PumpkinPy - Semantic similarity implemented in python

##### About

PumpkinPy uses IC ordered bitmaps for fast ranking of genes and diseases
(phenotypes are sorted by descending frequency and one-hot encoded).
This is useful for larger ontologies such as Upheno and large datasets such
as ranking all mouse genes given a set of input HPO terms.
This approach was first used in OWLTools and OwlSim-v3.

The goal of this project was to build an implementation of the PhenoDigm algorithm in python.
There are also implementations for common measures for distance and similarity
(euclidean, cosine, Jin-Conrath, Resnik, jaccard)

*Disclaimer*: This is a side project needs more documentation and testing

#### Getting Started

Requires python 3.8+ and python3-dev to install pyroaring

##### Installing from pypi

```
pip install pumpkin-py
```

##### Building locally
To build locally first install poetry - 

https://python-poetry.org/docs/#installation

Then run make:

```make```

##### Usage

Get a list of implemented similarity measures
```python
from pumpkin_py import get_methods
get_methods()
['jaccard', 'cosine', 'phenodigm', 'symmetric_phenodigm', 'resnik', 'symmetric_resnik', 'ic_cosine', 'sim_gic']
```

Load closures and annotations

```python
import gzip
from pathlib import Path

from pumpkin_py import build_ic_graph_from_closures, flat_to_annotations, search

closures = Path('.') / 'data' / 'hpo' / 'hp-closures.tsv.gz'
annotations = Path('.') / 'data' / 'hpo' / 'phenotype-annotations.tsv.gz'

root = "HP:0000118"

with gzip.open(annotations, 'rt') as annot_file:
    annot_map = flat_to_annotations(annot_file)

with gzip.open(closures, 'rt') as closure_file:
    graph = build_ic_graph_from_closures(closure_file, root, annot_map)
```

Search for the best matching disease given a phenotype profile

```python
import pprint
from pumpkin_py import search

profile_a = (
    "HP:0000403,HP:0000518,HP:0000565,HP:0000767,"
    "HP:0000872,HP:0001257,HP:0001263,HP:0001290,"
    "HP:0001629,HP:0002019,HP:0002072".split(',')
)

search_results = search(profile_a, annot_map, graph, 'phenodigm')

pprint.pprint(search_results.results[0:5])
```
```
[SimMatch(id='ORPHA:94125', rank=1, score=72.67599348696685),
 SimMatch(id='ORPHA:79137', rank=2, score=71.57368233248252),
 SimMatch(id='OMIM:619352', rank=3, score=70.98305459477629),
 SimMatch(id='OMIM:618624', rank=4, score=70.94596234638497),
 SimMatch(id='OMIM:617106', rank=5, score=70.83097366257857)]
```


##### Example scripts for fetching Monarch annotations and closures

Uses robot and sparql to generate closures and class labels

Annotation data is fetched from the latest Monarch release
 - Requires >Java 8
 
```cd data/monarch/ && make```


PhenoDigm Reference: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649640/  
Exomiser: https://github.com/exomiser/Exomiser  
OWLTools: https://github.com/owlcollab/owltools  
OWLSim-v3: https://github.com/monarch-initiative/owlsim-v3  
