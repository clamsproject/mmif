dev:
	python yaml_to_vdsl.py rdf
	python publish.py --test
	make -C ./rdf all
	mkdir -p www/ontologies
	cp ./rdf/target/* www/ontologies
