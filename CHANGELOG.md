# Change Log

All notable changes to this project are documented in this file.

The format is loosely based on [Keep a Changelog](http://keepachangelog.com/). Loosely because we do not keep separate sections within a version for additions and fixes etcetera, instead most logged changes will start with one of Added, Changed, Deprecated, Removed, Fixed, or Security. This project follows [Semantic Versioning](http://semver.org/), but until we hit version 1.0.0 we will be somewhat cavalier in our versioning.

This file documents changes made to the MMIF specification. Version names used to start with `spec-` because the Python MMIF SDK was also maintained in this repository. Starting with version 0.2.2 the repository was split and the prefix was discarded.

## Version 0.4.1 − 2022-11-17

- Cosmetic changes and documentation updates.


## Version 0.4.0 − 2021-06-09

- Removed all optional attributes from `annotationProperties` in the JSON schema. We figured that it is impossible to keep all attributes from all individual vocabulary types in a single JSON schema file (e.g. no way to deal with naming conflicts).
- Renamed `Region.unit` to `Region.timeUnit`. We realized that only time needs a unit to measure. Image regions are always based on pixels and text regions are always on unicode codepoints (not bytes).
- Renamed `TimePoint.point` to `TimePoint.timePoint` to make it more consistent with `Polygon.timePoint`.
- Added `sourceType` and `targetType` as metadata props to `Alignment` type, to simplify navigation over simple bi-modal aliangments.

## Version 0.3.1 − 2021-05-11

- Added and `error` property to the view metadata. The view metadata now either have an non-empty error section or a non-empty contains section. This is not a breaking change since the old schema did allow arbitrary extra properties in the view metadata.
- Replaced hard-coded version numbers with a variable. The build script uses templating to deal with them.
- Changed the old script `vocabulary/publish` to make it more general, it was also moved to `build.py`.


## Version 0.3.0 − 2021-03-10

- Updated the MMIF schema. Most significant change is that the location property is now a URI. This is likely a breaking change for all applications that work with version 0.2.2, hence the minor version bump up.
- Added boxType property to BoundingBox.


## Version 0.2.2 − 2020-12-03

- Fixed typos in the MMIF sample files.
- Updated documentation.
- Added notes on MMIF to PBCore mapping
- Removed all Python SDK code, which now lives at [https://github.com/clamsproject/mmif-python](https://github.com/clamsproject/mmif-python).

## Version spec-0.2.1 − 2020-09-28

- Removed the `@contexts` and the `mediumMetadata` from the MMIF context. This would usually not be a patch-level change but for just this occasion we decided it was.
- Fixed a variety of spelling errors in the sample MMIF documents and specifications.


## Version spec-0.2.0 − 2020-09-11

- Added document types to the vocabulary, this included adding a new top type.
- Changed the *Annotation* type by adding *document* as a metadata property and a regular property.
- Changed the *Alignment* type by making it parent the top type.
- Removed the *context* property from the top-level in the MMIF file and from the views.
- Removed the contexts files from the published specifications.
- Changed the *media* property on the MMIF files into the *documents* property.
- Made the *documents* list property read only. If new primary data are created then they will be put in a new view as a document.
- Fixed issue [#75](https://github.com/clamsproject/mmif/issues/75) (we are now using *app* instead of *tool* in the view metadata).
- Changed the JSON schema to fit the new syntax of MMIF.
- Changed the informal specifications to reflect all the above changes.
- Added full MMIF samples to the specifications.


## Version 0.1.0 − 2020-07-23

First released version. 
