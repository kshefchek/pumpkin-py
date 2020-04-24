PumpkinPy (likely to be renamed) - PhenoDigm implemented in python

##### Background

A python implementation for PhenoDigm and other semantic similarity methods.

This started as a [gist](https://gist.github.com/kshefchek/dc9324023f9cc54333298658e1f9f49e)
then ended up being used to analyze the
[lay subset of the HPO](https://github.com/monarch-initiative/hpo-survey-analysis/tree/master/phenom/similarity).

###### Fetching annotations and closures

Uses robot and sparql to generate closures and class labels

Annotation data is fetched from the latest Monarch release
 - Requires >Java 8
 
```cd resources && make```


PhenoDigm Reference: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649640/  
Exomiser: https://github.com/exomiser/Exomiser  
OWLTools: https://github.com/owlcollab/owltools  
OWLSim-v3: https://github.com/monarch-initiative/owlsim-v3  
