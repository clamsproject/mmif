# CLAMS Vocabulary Creation

This directory contains the files to create the CLAMS vocabulary pages. The vocabulary itself is stored in `clams.vocabulary.yaml`. Edit the YAML file to change the vocabulary.  

To create webpages from the YAML file run the following:

```bash
$ python clams.vocabulary.py 0.1.0
```

This creates the webpages from the YAML file and writes results to `../docs/vocabulary/0.1.0`. The versioning system is not yet decided and in this stage we are just working on the very first version.

