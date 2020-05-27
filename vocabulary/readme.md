# CLAMS Vocabulary Creation

This directory contains the files to create the CLAMS vocabulary pages. The vocabulary itself is stored in `clams.vocabulary-VERSION.yaml`. The first version of the vocabulary is in `clams.vocabulary-1.0.yaml`. 

Editteh YAML file to change the vocabulary.  Bump up the version number for non-cosmetic changes. You should increment the minor version number for changes to the types (significant changes to the definition of types or properties) and increment the major version for changes to the hierarchy (adding or deleting types). While CLAMS workflows are unpublished we can stick to version 1.0.

To create webpages from the YAML file run the following:

```bash
$ python clams.vocabulary.py 1.0
```

This creates the webpages from the versioned YAML file and write results to `../docs/vocabulary/1.0`. See the docstring in the script to see how to overrule the output directory.

