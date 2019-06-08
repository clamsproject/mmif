# Multi-Media Interchange Format

MMIF can have two different meanings. First, in a narrow sense, MMIF is an annotation format for audiovisual media as well as associated text (transcripts, captions, on-screen text). In a wider sense, MMIF is a collection of linked-data components that specifies such a format syntactically and assigns semantics to elements in the format. The goal of MMIF is to have a open serialization format for computational analysis tools that support interoperability between such tools and software, so that users of the tools can create and customize different pipelines to extract meaningful information and insights from digitized audiovisual material. For syntactic specifications, we use [JSON-LD format](https://json-ld.org/) that can be easily converted to other linked-data serialization formats (rdf, ttl). For semantic interoperability, we define MMIF vocabulary - an open linked-data vocabulary for the semantics of media types and annotation types - that can describe terminology used in computationally analyzing A/V material.

The draft of MMIF components, their specifications, and their implementation ideas can be found on [the github repository](https://github.com/clamsproject/mmif/tree/master/specifications/draft). Contributions are welcome via [the github issue tracker](https://github.com/clamsproject/mmif/issues). 



<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-141649660-2"></script>

<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-141649660-2');
</script>


