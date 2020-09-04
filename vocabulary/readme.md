# CLAMS Vocabulary Creation

This directory contains the files to create the CLAMS vocabulary pages. The code requires Python 3, preferably 3.7 or higher (but older versions may work too), and you need to install [PyYAML](https://pypi.org/project/PyYAML/) and [Beautiful Soup](https://pypi.org/project/beautifulsoup4/) and its lxml parser:

````bash
$ pip install PyYAML, bs4, lxml
````

The vocabulary itself is stored in `clams.vocabulary.yaml`. Edit the YAML file to change the vocabulary.

To create webpages from the YAML file run the following:

```bash
$ python publish.py
```

This creates the webpages from the YAML file and writes results to `../docs/VERSION/vocabulary` where `VERSION` is retrieved from the `VERSION` file at the top-level directory of this repository. Commiting those pages, merging them into the master branch and then pushing them to https://github.com/clamsproject/mmif will update or create pages at http://mmif.clams.ai/0.2.0/vocabulary/. The script will also add other files to http://mmif.clams.ai/0.2.0/ including the JSON schema and the informal specifications.

You can create a test version in the `www` directory by using the `--test` option:

```bash
$ python publish.py --test
```

There is a `Makefile` in this directory that you can use.  It runs the publish script, but also creates ontology files by running `yaml_to_vdsl.py`, which creates `rdf/clams.vocabulary`, which is then used by `rdf/Makefile` to create JSON-LD, OWL, RDF and TTL files in `rdf/target`.

````bash
$ make dev
````

For now, we are not creating those files because we are considering taking the JSON-LD out of MMIF.