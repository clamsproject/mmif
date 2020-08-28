---
layout: page
title: MMIF Specification
subtitle: Versioning Notes
---

We use [semantic versioning](https://semver.org/) with the `major.minor.patch` version scheme. All components of the specification (the specifications document, the JSON schema and the CLAMS vocabulary) share the same version number. Major updates to the specification including changing the schema and major changes to the hierarchy will increase the major version number, minor changes like adding types or properties change the minor version number. The patch number increases for small fixes and documentation updates.

The SDK shares `major` and `minor` numbers with the specification version. So if a new version `X.Y.0` is created a new version `X.Y.0` will be created as well. 

See the [versioning notes](versioning.md) for more information.

That is, 

1. A change in a single component of the specification will increase version numbers of other components as well, and thus some components can be identical to their immediate previous version. 
1. A specific version of the SDK is tied to certain versions of the specification, and thus the applications based on different versions of SDK may not be compatible to each other, and may not be used together in a single pipeline. 

> 