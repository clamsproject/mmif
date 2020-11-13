---
layout: page
title: MMIF
subtitle: Multi-Media Interchange Format
---

MMIF can have two different meanings. First, in a narrow sense, MMIF is an annotation format for audiovisual media as well as associated text (transcripts, captions, on-screen text). In a wider sense, MMIF is a collection of linked-data components that specifies such a format syntactically and assigns semantics to elements in the format. The goal of MMIF is to have an open serialization format for computational analysis tools that support interoperability between such tools and software, so that users of the tools can create and customize different pipelines to extract meaningful information and insights from digitized audiovisual material. For syntactic specifications, we use the [JSON-LD format](https://json-ld.org/), which can be easily converted to other linked-data serialization formats (rdf, ttl). For semantic interoperability, we define the MMIF vocabulary, an open linked-data vocabulary for the semantics of media types and annotation types that can describe terminology used while computationally analyzing A/V material.

The current version of MMIF is {{ site.navbar-links["VERSIONS"].first.first[0] }} and it is available at [https://mmif.clams.ai/{{ site.navbar-links["VERSIONS"].first.first[0] }}]({{ site.navbar-links["VERSIONS"].first.first[0] }}).

For documentation on the Python distribution package `mmif-python`, visit the [documentation website](https://www.clams.ai/mmif-python).

Contributions are welcome via [the github issue tracker](https://github.com/clamsproject/mmif/issues).

---

*Last updated: September 3rd 2020*

