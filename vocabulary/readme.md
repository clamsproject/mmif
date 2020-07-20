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

This creates the webpages from the YAML file and writes results to `../docs/VERSION/vocabulary` where `VERSION` is retrieved from the `VERSION` file at the top-level directory of this repository. Commiting those pages, merging them into the master branch and then pushing them to https://github.com/clamsproject/mmif will update or create pages at http://mmif.clams.ai/0.1.0/vocabulary/.

You can create a test version in the `www` directory by using the `--test` option:

```bash
$ python publish.py --test
```



````bash
$ pip install PyYAML, bs4, lxml
````

