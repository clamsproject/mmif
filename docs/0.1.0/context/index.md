---
layout: page
title: MMIF Context Files
subtitle: version 0.1.0
---

JSON-LD context definitions can be used to help expand terms in the MMIF document to full URIs. Rather than using inline context definitions we use context files.

There are two kinds of terms that we want to expand:

1. Context for MMIF Terms. Terms that are part of the structure of MMIF and that are the same for any MMIF document. These include structural properties like *metadata*, *views* and *properties*. The full URIs for these terms all include *mmif*, for example http://mmif.clams.ai/0.1.0/vocab/mmif/metadata.
2. Vocabulary Context. Terms that are relevant only to the output of a particular tool or pipeline. These define the annotation types and their properties and include types like *TimeFrame* and *BoundingBox* and features of those terms like *frameType* and *coordinates*. The full URIs point to files directly inside *vocab*, without the *mmif* suffix, for example http://mmif.clams.ai/0.1.0/vocab/TimeFrame.

Here is a simple and somewhat simplified example that we use for further explanation:

```json
{
  "@context": "http://mmif.clams.ai/0.1.0/context/mmif.json",

  "metadata": {
	  "mmif": "http://mmif.clams.ai/0.1.0",
	  "contains": {
	    "http://mmif.clams.ai/1.0/vocabulary/TimeFrame": ["v1"] }},

  "media": [
	  {
	    "id": "m1",
	    "type": "video",
	    "location": "/var/archive/video-0012.mp4"
	  }
  ],

  "views": [
	{
	  "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",
	  "id": "v1",
	  "metadata": {
		  "medium": "m1",
		  "timestamp": "2020-05-27T12:23:45",
		  "tool": "http://tools.clams.ai/bars-and-tones/1.0.5",
		  "contains": {
		    "TimeFrame": { "unit": "seconds" }}},
	  "annotations": [
		  {
		    "@type": "TimeFrame",
		    "properties": {
          "id": "s1",
          "start": 87,
          "end": 145,
          "frameType": "bars-and-tones",
          "frameLength": 58 }}
	    ]
	}
}
```

This example has most of the main structural MMIF properties, some annotation types and properties from the CLAMS vocabulary and one property that is not defined in the CLAMS vocabulary (*frameLength*). Here, we are assuming version 0.1.0.



## Context for MMIF Terms

This context is referred to at the top-level of the MMIF file and is available at http://mmif.clams.ai/0.1.0/context/mmif.json. Its content is printed here in full:

```json
{
  "@context" : {
    "@vocab" : "http://mmif.clams.ai/0.1.0/vocab/mmif/"
  }
}
```

That is, all the file does is define a vocabulary URI and all unexpanded terms in the MMIF document will be interpreted relative to the vocabulary URI. As a result terms will be expanded as follows:

```
term ==> http://mmif.clams.ai/0.1.0/vocab/mmif/term
```

For example, the top-level metadata section ends up as

```json
{
  "http://mmif.clams.ai/0.1.0/vocab/mmif/metadata": {
    "http://mmif.clams.ai/0.1.0/vocab/mmif/mmif": "http://mmif.clams.ai/0.1.0",
    "http://mmif.clams.ai/0.1.0/vocab/mmif/contains": {
      "http://mmif.clams.ai/1.0/vocabulary/TimeFrame": ["v1"] }}
}
```

The top-level context file has scope over the entire document and you may expect it to also govern expansion of terms inside the views. But those views have their own context file and we will see that that context takes precedence over the top-level context.. 



## Vocabulary Context

The example view above uses http://mmif.clams.ai/0.1.0/context/vocab-clams.json which contains the CLAMS context. Like the top-level it defines a vocabulary which in this case is located at the URL http://mmif.clams.ai/0.1.0/vocab/. If this were all that were in the context then all terms in the view would be expanded relative to that URL and this would include a term like *metadata*. But we do not want to expand *metadata* into http://mmif.clams.ai/0.1.0/vocab/metadata because *metadata* is not part of the type vocabulary but rather of the structural terms in MMIF.

So the context file has special definition to make sure that MMIF structural terms get expanded properly:

```json
{
  "@context" : {
    "@vocab" : "http://mmif.clams.ai/0.1.0/vocab/",
    "mmif": "http://mmif.clams.ai/0.1.0/vocab/mmif/",
    "id": "mmif:id",
    "metadata": "mmif:metadata",
    "timestamp": "mmif:timestamp"
  }
}
```

This is a fragment of the full context file and shows that MMIF terms are expanded properly. In the full file all terms known to be used in views that are not directly related to the CLAMS vocabulary will be listed, including *annotations* and *properties*. If you want to list a term that is not defined like that you would have to use the *mmif* prefix. For example, if you want to use a new metadata property named *validated* then without any changes that would be expanded to http://mmif.clams.ai/0.1.0/vocab/validated, which is not ideal. If you want it to be expanded to  http://mmif.clams.ai/0.1.0/vocab/mmif/validated then you should use *mmif:validated* in the metadata.

With the vocabulary above a term like *TimeFrame* will be correctly expanded to http://mmif.clams.ai/0.1.0/vocab/TimeFrame, so new machinary is needed there. But we also want to use properties like *start*, *end* and *TimeFrameType* and we want them to be related to the annotation type they are defined for. Fo this we have special rules as in the fragment below (omitting the MMIF-specific rules):

```json
{
  "@context" : {
		"@vocab" : "http://mmif.clams.ai/0.1.0/vocab/",
    "start": "Interval#start",
    "end": "Interval#end",
    "frameType": "TimeFrame#frameType"
  }
}
```

Now *frameType* will be expanded to http://mmif.clams.ai/0.1.0/vocab/TimeFrame#frameType, which is what we want.

With the rules in place now, the single annotation in the example will be expanded to

```json
{
  "@type": "TimeFrame",
  "http://mmif.clams.ai/0.1.0/vocab/mmif/properties": {
    "http://mmif.clams.ai/0.1.0/vocab/mmif/id": "s1",
    "http://mmif.clams.ai/0.1.0/vocab/Interval#start": 87,
    "http://mmif.clams.ai/0.1.0/vocab/Interval#end": 145,
    "http://mmif.clams.ai/0.1.0/vocab/TimeFrame#frameType": "bars-and-tones",
    "http://mmif.clams.ai/0.1.0/vocab/frameLength": 58
  }
}
```

Note how *properties* and *id* are in the MMIF structural domain while the others are in the CLAMS vocabulary. The one issue here is that *frameLength* is not defined as a property of an annotation type in the CLAMS vocabulary so it receives a default expansion. While there is nothing illegal about this, there are two options that might make more sense. One is to use a full URI for the property and have this lead to some informative URI. The other is to use *TimeFrame#frameLength* as the property name and thus at least suggest a connection to the type.
