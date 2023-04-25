# MMIF

Repository for MMIF specifications, MMIF schema and the CLAMS vocabulary.

To create a new version use the `build.py` script:

```bash
$ python build.py
```

This creates a new version in `docs/VERSION` where the version is taken from the `VERSION` file.

### Local build and preview

HTML files generated from `build.py` will be deployed to a github.io page. The base webpage where all the versioned specifications reside is deployed via the `jekyll` engine. That is, to test and preview a local build, one needs to install `jekyll` for local serving, which in turn, requires ruby. Install ruby following [this documentation](https://www.ruby-lang.org/en/documentation/installation/). `jekyll` wants ruby>=2.5, but ruby is shipped with `bundle/bundler` (*THE* dependency management utility for ruby) only since 2.6, hence installing 2.6 or newer is preferred. For 2.5, one needs to manually install bundler after installing ruby.

Once ruby and bundler are ready,

1. `bundle env | grep Bin` # this is where jekyll is installed
1. `cd docs` 
1. `rm Gemfile.lock`
1. `bundle install`
1. `jekyll serve` # if the bundle Bin dir is not in your `$PATH`, use absolute path to jekyll binary

should give you a running instance of the MMIF specification website at localhost:4000.

Note that the starting jekyll will download website theme and L&F from the internet (Specifically from https://github.com/clamsproject/website-theme ). So you need an internet connection to get the full preview locally. To start jekyll without a connection (and lose styles) you need to comment `remote_theme` config line from `docs/_config.yaml` file before running the jekyll command. 

### Checklist for deployment 

List of things to do when creating a new version:

- [ ] Update the `VERSION` file.
- [ ] Run the build.py script. This will automatically do the following:
  - Collect all changes (schema, vocabulary and specifications)
  - Update `specifications/index.md` to replace version numbers.
  - Update all the sample files so they all have the right version number.
  - Update VERSIONS list in `docs/_config.yml`.
  - Update `docs/index.md` (date at the bottom).
- [ ] Test all examples to see whether they match the schema.
- [ ] Check all pages
- [ ] Final updates to `CHANGELOG.md`.
- [ ] Submit all changes (including ones that were made automatically, like the changes to the config file in the documentation directory) and merge to the main branch.

