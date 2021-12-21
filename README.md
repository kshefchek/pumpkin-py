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

##### Getting Started

Requires python 3.8+ and python3-dev to install pyroaring

Installing from pypi

```
pip install pumpkin_py
```

Running make will install locally and run the tests
```
make
```

###### Fetching annotations and closures

Uses robot and sparql to generate closures and class labels

Annotation data is fetched from the latest Monarch release
 - Requires >Java 8
 
```cd data/monarch/ && make```


PhenoDigm Reference: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649640/  
Exomiser: https://github.com/exomiser/Exomiser  
OWLTools: https://github.com/owlcollab/owltools  
OWLSim-v3: https://github.com/monarch-initiative/owlsim-v3  
