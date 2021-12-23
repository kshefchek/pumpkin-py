MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

.DEFAULT_GOAL := all
SHELL := bash

WGET = /usr/bin/wget --timestamping --no-verbose

MONARCH = https://archive.monarchinitiative.org/latest/owlsim/data/

ROBOT_JAR = https://github.com/ontodev/robot/releases/latest/download/robot.jar

ROBOT := java -jar bin/robot.jar

ANNOTATION_FILES = \
	annotations/Homo_sapiens/Hs_disease_labels.txt \
	annotations/Homo_sapiens/Hs_disease_phenotype.txt \
	annotations/Mus_musculus/Mm_gene_labels.txt \
	annotations/Mus_musculus/Mm_gene_phenotype.txt \
	annotations/Danio_rerio/Dr_gene_labels.txt \
	annotations/Danio_rerio/Dr_gene_phenotype.txt \
	annotations/Drosophila_melanogaster/Dm_gene_labels.txt \
	annotations/Drosophila_melanogaster/Dm_gene_phenotype.txt \
	annotations/Cases/UDP_case_labels.txt  \
	annotations/Cases/UDP_case_phenotype.txt \
	annotations/Caenorhabditis_elegans/Ce_gene_labels.txt \
	annotations/Caenorhabditis_elegans/Ce_gene_phenotype.txt

CURIFY = sed 's@<http://purl.obolibrary.org/obo/\([A-Za-z]*\)_\([A-Za-z0-9]*\)>@\1:\2@g'

.PHONY: all
all: $(ANNOTATION_FILES) \
     bin/robot.jar \
     closures/hp-closures.tsv \
     closures/hp-labels.tsv \
     closures/upheno-1.owl \
     closures/upheno-1-closures.tsv \
     closures/upheno-1-labels.tsv \
     closures/upheno-2.owl \
     closures/upheno-2-closures.tsv \
     closures/upheno-2-labels.tsv \
     annotations/all-annotations.tsv \

.PHONY: FORCE
FORCE:

bin/:
	mkdir --parents $@

tmp/:
	mkdir --parents $@

bin/robot.jar: FORCE | bin/
	curl -L -o bin/robot.jar $(ROBOT_JAR)

annotations/:
	mkdir --parents $@

$(ANNOTATION_FILES): | annotations/
	cd annotations && $(WGET) --recursive --no-parent --no-host-directories \
		--cut-dirs=3 --reject 'index.html*' --reject 'README*' $(MONARCH)

closures/:
	mkdir --parents $@

tmp/hp-closures.tsv: FORCE | tmp/
	$(ROBOT) \
	  merge \
	    --input-iri http://purl.obolibrary.org/obo/hp.owl \
	  filter \
	    --axioms logical \
	  remove \
	    --select anonymous \
	  query \
	    --query sparql/hp-closures.rq \
		$@

tmp/hp-labels.tsv: FORCE | tmp/
	$(ROBOT) \
	  merge \
	    --input-iri http://purl.obolibrary.org/obo/hp.owl \
	  remove \
	    --select anonymous \
	  query \
	    --query sparql/hp-labels.rq \
		$@

closures/upheno-1.owl: FORCE | closures/
	$(ROBOT) \
	  merge \
	    --input-iri https://bbop-ontologies.s3.amazonaws.com/upheno/current/upheno-release/all/upheno_old_metazoa.owl \
 	  remove \
	    --axioms "disjoint" \
	  remove \
	    --term owl:Nothing \
	    --term rdfs:comment \
	  remove \
	    --select "anonymous individuals <http://purl.obolibrary.org/obo/IAO*> <http://www.geneontology.org/formats/oboInOwl*>" \
	    --output $@

closures/upheno-2.owl: FORCE | closures/
	$(ROBOT) \
	  merge \
	    --input-iri https://bbop-ontologies.s3.amazonaws.com/upheno/current/upheno-release/all/upheno_lattice_model.owl \
 	  remove \
	    --axioms "disjoint" \
	  remove \
	    --term owl:Nothing \
	    --term rdfs:comment \
	  remove \
	    --select "anonymous individuals <http://purl.obolibrary.org/obo/IAO*> <http://www.geneontology.org/formats/oboInOwl*>" \
	    --output $@

tmp/upheno-1-closures.tsv: closures/upheno-1.owl tmp/
	$(ROBOT) \
	  query \
	    --input closures/upheno-1.owl \
	    --query sparql/upheno-closures.rq \
		$@

tmp/upheno-1-labels.tsv: closures/upheno-1.owl tmp/
	$(ROBOT) \
	  query \
	    --input closures/upheno-1.owl \
	    --query sparql/upheno-labels.rq \
		$@

tmp/upheno-2-closures.tsv: closures/upheno-2.owl tmp/
	$(ROBOT) \
	  query \
	    --input closures/upheno-2.owl \
	    --query sparql/upheno-closures.rq \
		$@

tmp/upheno-2-labels.tsv: closures/upheno-2.owl tmp/
	$(ROBOT) \
	  query \
	    --input closures/upheno-2.owl \
	    --query sparql/upheno-labels.rq \
		$@

annotations/all-annotations.tsv: $(ANNOTATION_FILES)
	cat annotations/Homo_sapiens/Hs_disease_phenotype.txt \
	    annotations/Mus_musculus/Mm_gene_phenotype.txt \
	    annotations/Danio_rerio/Dr_gene_phenotype.txt \
	    annotations/Drosophila_melanogaster/Dm_gene_phenotype.txt \
	    annotations/Cases/UDP_case_phenotype.txt \
	    annotations/Caenorhabditis_elegans/Ce_gene_phenotype.txt \
	    > $@

closures/upheno-1-closures.tsv: tmp/upheno-1-closures.tsv closures/
	$(CURIFY) $< | sed 's/^?/#/' > $@

closures/upheno-1-labels.tsv: tmp/upheno-1-labels.tsv closures/
	$(CURIFY) $< | sed 's/^?/#/' > $@

closures/upheno-2-closures.tsv: tmp/upheno-2-closures.tsv closures/
	$(CURIFY) $< | sed 's/^?/#/' > $@

closures/upheno-2-labels.tsv: tmp/upheno-2-labels.tsv closures/
	$(CURIFY) $< | sed 's/^?/#/' > $@

closures/hp-closures.tsv: tmp/hp-closures.tsv closures/
	$(CURIFY) $< | sed 's/^?/#/' > $@

closures/hp-labels.tsv: tmp/hp-labels.tsv closures/
	$(CURIFY) $< | sed 's/^?/#/' > $@
