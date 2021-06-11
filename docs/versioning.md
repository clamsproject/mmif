---
layout: page
title: MMIF Specification
subtitle: Versioning Notes
---

We use [semantic versioning](https://semver.org/) with the `major.minor.patch` version scheme. 

All components of the specification (the specifications document, the JSON schema and the CLAMS vocabulary) share the same version number. Major updates to the specification including changing the schema and modification to the vocabulary types will increase the major version number, minor changes like adding types or properties change the minor version number. The patch number increases for small fixes and documentation updates.

Currently, major and minor version updates are considered as *breaking*, meaning one simply cannot mix MMIF files with different major and/or minor version in a single pipeline of CLAMS apps. Patch updates, on the other hand, are not breaking. Individual CLAMS apps must declare which specification they are targeting in their app metadata (If an app is developed using `mmif-python` and `clams-python` SDK, this is done automatically). When an app targets, for example, `a.b.c` specification version, it means the output MMIF file from the app is version `a.b.c`. Users should be careful and use only *compatible* apps in a pipeline, namely all input MMIF files and output MMIF files in a single pipeline must share the same major and minor version numbers. 
{: .box-note}

The Python SDK ([`mmif-python`](https://pypi.org/project/mmif-python/)) shares `major` and `minor` numbers with the specification version and if a new version `X.Y.0` is created for the specifications then a new version `X.Y.0` will be created for the SDK as well, even if there were no changes to the SDK. Patch-level updates to the specifications will not result in new versions of the SDK. Changes to the SDK will always result in an update of the patch number, no matter how major those changes are. 

As a result, it is sufficient to use specifications and SDK with the same `major` and `minor` version numbers. Typically one would take the highest patch level for each of the two. A specific version of the SDK is tied to specific version of the specification, and thus the applications based on different versions of SDK may not be compatible to each other, and may not be used together in a single pipeline. 

See [this document](https://clams.ai/mmif-python/latest/target-versions.html) to find target specification of each SDK version. 

> Note: this requires some thoughts on whether and how the CLAMS platform ensures that applications using different versions of the schema and vocabulary can fit together.
