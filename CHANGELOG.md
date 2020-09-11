# Change Log

All notable changes to this project are documented in this file.

The format is loosely based on [Keep a Changelog](http://keepachangelog.com/). Loosely because we do not keep separate sections within a version for additions and fixes etcetera, instead most logged changes will start with one of Added, Changed, Deprecated, Removed, Fixed, or Security. This project follows [Semantic Versioning](http://semver.org/).

This file documents changes made to the specification as well as changes to the Python SDK. Changes to the former are listed under section headers named `spec-X.Y.Z` and changes to the latter in headers named `py-X.Y.Z`.


## Version py-0.2.0 − In Progress

- Changed the SDK to work with the specifications in `spec-0.2.0`.


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
