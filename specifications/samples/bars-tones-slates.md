---
layout: page
title: MMIF Specification
subtitle: Version $VERSION
---



# Example: Bars and Tones and Slates







We use [semantic versioning](https://semver.org/) with the `major.minor.patch` version scheme. 

All components of the specification (the specifications document, the JSON schema and the CLAMS vocabulary) share the same version number. Major updates to the specification including changing the schema and major changes to the hierarchy will increase the major version number, minor changes like adding types or properties change the minor version number. The patch number increases for small fixes and documentation updates.

The SDK shares `major` and `minor` numbers with the specification version and if a new version `X.Y.0` is created for the specifications then a new version `X.Y.0` will be created for the SDK as well, even if there were no changes to the SDK. Patch-level updates to the specifications will not result in new versions of the SDK. Changes to the SDK will always result in an update of the patch number, no matter how major those changes are. 

As a result, it is sufficient to use specifications and SDK with the same `major` and `minor` version numbers. Typically one would take the highest patch level for each of the two. A specific version of the SDK is tied to specific version of the specification, and thus the applications based on different versions of SDK may not be compatible to each other, and may not be used together in a single pipeline. 

> Note: this requires some thoughts on whether and how the CLAMS platform ensures that applications using different versions of the schema and vocabulary can fit together.