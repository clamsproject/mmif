dev:
	python yaml_to_vdsl.py rdf
	python publish.py --test
	java -version
	# Known to work with Java 8. Does not work with some later Java versions. Run with Java 8.
	make -C ./rdf all
	mkdir -p www/ontologies
	cp ./rdf/target/* www/ontologies
