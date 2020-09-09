VERSION=$(shell cat ../../VERSION)

VOCABULARY=clams.vocabulary

help:
	@echo
	@echo "Run 'make all' to generate ontologies fresh, or"
	@echo "run one of the following goals to perform a single task."
	@echo
	@echo "GOALS"
	@echo
	@echo "clean      - Removes generated files."
	@echo "rdf        - Generates RDF, OWL, and JSON versions of the vocabulary"
	@echo "help       - Displays this help message." 
	@echo

rdf:
	./bin/vocab -V $(VERSION) --output target --rdf rdf $(VOCABULARY) 
	./bin/vocab -V $(VERSION) --output target --rdf owl $(VOCABULARY) 
	./bin/vocab -V $(VERSION) --output target --rdf ttl $(VOCABULARY) 
	./bin/vocab -V $(VERSION) --output target --rdf jsonld $(VOCABULARY)

all: clean rdf

clean:
	rm -rf target
