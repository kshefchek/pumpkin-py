Running `make` will generate three directories:

bin/
    robot.jar - https://github.com/ontodev/robot
    
closures/
    *-closures.tsv - two column file, where two IRIs are linked by a
                     subClassOf|equivalent|part_of edge, 1 -> 2
    *-closures.tsv - two column file, where two IRIs are linked by a
                     subClassOf|equivalent|part_of edge, 1 -> 2
    *-labels.tsv - two columns: iri, label
    metazoa-slim.owl - Upheno slim OWL file
    
annotations/
    Homo_sapiens/Hs_gene_labels.txt  
	Homo_sapiens/Hs_gene_phenotype.txt  
	Mus_musculus/Mm_gene_labels.txt  
	Mus_musculus/Mm_gene_phenotype.txt  
	Danio_rerio/Dr_gene_labels.txt  
	Danio_rerio/Dr_gene_phenotype.txt  
	Drosophila_melanogaster/Dm_gene_labels.txt  
	Drosophila_melanogaster/Dm_gene_phenotype.txt  
	Cases/UDP_case_labels.txt  
	Cases/UDP_case_phenotype.txt  
	Caenorhabditis_elegans/Ce_gene_labels.txt  
	Caenorhabditis_elegans/Ce_gene_phenotype.txt


Generating the metazoa-slim file takes a chunk of memory (>8gb), an alternative
is downloading from https://archive.monarchinitiative.org/latest/owl/metazoa-slim.owl
