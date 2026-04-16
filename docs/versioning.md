---
layout: page
title: MMIF Specification
subtitle: Versioning Notes
---

This document details how MMIF is versioned. 

### MMIF components
1. JSON schema (`schema` hereinafter): a single file, defining JSON syntax of MMIF serialization. Published on [our github](https://raw.githubusercontent.com/clamsproject/mmif/develop/schema/mmif.json) and included in `mmif-python` Python package.
1. [CLAMS vocabulary](https://clams.ai/vocabulary/) (`vocab` hereinafter): defines annotation types and their hierarchy. Maintained and versioned independently as the [`clams-vocabulary`](https://pypi.org/project/clams-vocabulary/) Python package.
1. CLAMS vocabulary annotation types (`types` hereinafter): individual types within the vocabulary, each independently versioned. Type URIs (e.g. `http://clams.ai/vocabulary/type/TypeName/vX`) are used as IRIs in MMIF serialization.
1. MMIF specification (`spec` hereinafter): main documentation (a single markdown file) and a set of example files (published at https://mmif.clams.ai/x.y.z ).
1. `mmif-python` SDK (`sdk` hereinafter, DO NOT confuse `mmif-python` with `clams-python`)

### How MMIF is versioned

We use [semantic versioning](https://semver.org/) with the `major.minor.patch` version scheme for the MMIF specification. 

However, the CLAMS team doesn't maintain multiple branches for different levels of versions. So the only major/minor versions that get bug fixes and updates, including any changes in MMIF specifications regardless of their significance, are always the latest ones.
{: .box-note}

`schema` and `spec` share the same version number. `vocab` is versioned independently. The `sdk` version relationship with the spec is [under reconsideration](https://github.com/clamsproject/mmif-python/issues/293); historically they shared major and minor numbers, but this constraint is being relaxed. A version of `sdk` ships the `schema` and declares `clams-vocabulary` as a dependency for type definitions.

### Version compatibility and app pipeline
CLAMS pipeline means two or more CLAMS apps are chained together to process the same source data. Typically, a pipeline is formed to make use of outputs of one app as input to the next app. 

There are two dimensions of version checking process in CLAMS pipelines.
1. MMIF JSON syntax: As the `sdk` includes the `schema`, when a CLAMS app takes an input MMIF, the `sdk` will check if the input is valid under the `schema` included in it (If the app is not using `sdk`, it's app developer's responsibility to make sure the input is valid). Hence, **MMIF version numbers themselves should play no role** in the validation process.
1. Annotation type versions: each annotation type has its own versioning (not SemVer, just a single integer versions). If an app written to take `A_Type/vX` as a target to process but sees `A_Type/vY` in an input MMIF (where `X` != `Y`), the app should know there's possible version compatibility issue when processing the input. However, again, **MMIF version numbers should not play any role** in the type checking process.
 
In short, in most cases app developers does not need to worry about MMIF versions when writing a CLAMS app, unless a new version is "breaking" and thus makes an app unusable in pipelines. 

### What constitute "breaking" changes 

As mentioned above, there are two places where version compatibility matters. MMIF JSON syntax (`schema`), and definitions of `types`. 
1. breaking changes in the `schema`: any changes related to any required fields will probably be breaking changes. Required fields in JSON schema usually related to `required`, `additionalProperties`, or value conditions such as `mixLength`/`maxLength`. 
1. breaking changes in `vocab` and `types`: any changes in an individual annotation type will increase the version of itself. However, inside structures of annotation types are not validated by `schema`, hence app developers need to pay attention to the changes to the types that are relevant to their apps. 

When writing an app using `mmif-python` and `clams-python`, a developer usually just targets `A_Type` (version unspecified) and a version is automatically inferred from the `clams-vocabulary` package installed alongside the `sdk`. Then when the `clams-python`-based app sees an annotation type in the input that does not match the target version, the default behavior is showing warnings and continuing processing.
{: .box-note}
 
The CLAMS team will try the best to identify possible breakage in a new release of MMIF in the release note. 

