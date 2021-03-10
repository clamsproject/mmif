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

- [x] Collect all changes (schema, vocabulary and specifications)
- [x] Update the `VERSION` file.
- [ ] Test all examples to see whether they match the schema.
- [x] Update `specifications/index.md`. Make sure it matches new schema and/or vocabulary if needed and replace version numbers.
- [x] Upate VERSIONS list in `docs/_config.yml`.
- [x] Update `docs/index.md` (date at the bottom).
- [ ] Run publish.py script.
- [ ] Check all pages
- [x] Final updates to `CHANGELOG.md`.
- [ ] Submit and merge to master branch.

