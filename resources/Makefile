WGET = /usr/bin/wget --timestamping --no-verbose

MONARCH = https://archive.monarchinitiative.org/latest/owlsim/data/

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

all: $(ANNOTATION_FILES) bin/robot.jar closures/hp-closures.tsv \
     closures/hp-labels.tsv closures/metazoa-slim.owl \
     closures/upheno-closures.tsv closures/upheno-labels.tsv \
     annotations/all-annotations.tsv

bin/:
	mkdir --parents $@

tmp/:
	mkdir --parents $@

bin/robot.jar: | bin/
	curl -L -o bin/robot.jar \
		https://github.com/ontodev/robot/releases/latest/download/robot.jar

annotations/:
	mkdir --parents $@

$(ANNOTATION_FILES): | annotations/
	cd annotations && $(WGET) --recursive --no-parent --no-host-directories \
		--cut-dirs=3 --reject 'index.html*' --reject 'README*' $(MONARCH)

closures/:
	mkdir --parents $@

tmp/hp-closures.tsv: | tmp/
	$(ROBOT) \
	  merge \
	    --input-iri http://purl.obolibrary.org/obo/hp.owl \
	  reason \
	    --reasoner ELK \
	  filter \
	    --axioms logical \
	  remove \
	    --select anonymous \
	  query \
	    --query sparql/hp-closures.rq \
		$@

tmp/hp-labels.tsv: | tmp/
	$(ROBOT) \
	  merge \
	    --input-iri http://purl.obolibrary.org/obo/hp.owl \
	  remove \
	    --select anonymous \
	  query \
	    --query sparql/hp-labels.rq \
		$@

closures/metazoa-slim.owl: | closures/
	$(ROBOT) \
	  merge \
	    --input-iri http://purl.obolibrary.org/obo/upheno/metazoa.owl \
 	  remove \
	    --axioms "disjoint" \
	  remove \
	    --term owl:Nothing \
	    --term rdfs:comment \
	  reason \
	    --reasoner ELK \
	    --axiom-generators "SubClass EquivalentClass" \
	  remove \
	    --select "anonymous individuals <http://purl.obolibrary.org/obo/IAO*> <http://www.geneontology.org/formats/oboInOwl*>" \
	    --output $@

tmp/upheno-closures.tsv: closures/metazoa-slim.owl tmp/
	$(ROBOT) \
	  query \
	    --input closures/metazoa-slim.owl \
	    --query sparql/upheno-closures.rq \
		$@

tmp/upheno-labels.tsv: closures/metazoa-slim.owl tmp/
	$(ROBOT) \
	  query \
	    --input closures/metazoa-slim.owl \
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

closures/upheno-labels.tsv: tmp/upheno-labels.tsv
	$(CURIFY) $< | sed 's/^?/#/' > $@

closures/hp-labels.tsv: tmp/hp-labels.tsv
	$(CURIFY) $< | sed 's/^?/#/' > $@

closures/upheno-closures.tsv: tmp/upheno-closures.tsv
	$(CURIFY) $< | sed 's/^?/#/' > $@

closures/hp-closures.tsv: tmp/hp-closures.tsv
	$(CURIFY) $< | sed 's/^?/#/' > $@
