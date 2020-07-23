PumpkinPy (likely to be renamed) - Semantic similarity implemented in python

##### Getting Started

Requires python3-dev to install pyroaring

 ```
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=.:$PYTHONPATH
```

###### Fetching annotations and closures

Uses robot and sparql to generate closures and class labels

Annotation data is fetched from the latest Monarch release
 - Requires >Java 8
 
```cd resources && make```


PhenoDigm Reference: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649640/  
Exomiser: https://github.com/exomiser/Exomiser  
OWLTools: https://github.com/owlcollab/owltools  
OWLSim-v3: https://github.com/monarch-initiative/owlsim-v3  
