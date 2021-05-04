# MMIF

Repository for MMIF specifications, MMIF schema and the CLAMS vocabulary.

To create a new version use the `publish.py` script:

```bash
$> cd vocabulary
$> python publish.py
```

This creates a new version in `docs/VERSION` where the version is taken from the `VERSION` file.

### Checklist

List of things to do when creating a new version:

- [ ] Update the `VERSION` file.
- [ ] Run publish.py script. This will automatically do 
  - Collect all changes (schema, vocabulary and specifications)
  - Update `specifications/index.md` to replace version numbers.
  - Update all the sample files so they all have the right version number.
  - Update VERSIONS list in `docs/_config.yml`.
  - Update `docs/index.md` (date at the bottom).
- [ ] Check `specifications/index.md`. Make sure it matches new schema and/or vocabulary if needed.
- [ ] Test all examples to see whether they match the schema.
- [ ] Check all pages
- [ ] Final updates to `CHANGELOG.md`.
- [ ] Submit and merge to master branch.

