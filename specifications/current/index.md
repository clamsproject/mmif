# MMIF - Multi-Media Interchange Format

MMIF is an annotation format for audiovisual media as well as associated text like transcripts, closed captions and other OCR. MMIF is a JSON-LD format used to transport data between CLAMS services and is inspired by and partially based on LIF, the [LAPPS Interchange Format](https://wiki.lappsgrid.org/interchange/).

MMIF is pronounced *mif* or *em-mif*, or, if you like to hum, *mmmmmif*.

> In the following we are still rather cavalier on where all the versioned files are. For now we use version 0.1.0 as an example, but note that files may not yet be available where they are supposed to be.

The current JSON schema for MMIF are at http://mmif.clams.ai/0.1.0/schema/mmif.json and determine part of the syntactic shape of MMIF. The specifications here often refer to elements from the CLAMS  Vocabulary at http://mmif.clams.ai/o.1.0/vocabulary as well as to the LAPPS Vocabulary at [http://vocab.lappsgrid.org](http://vocab.lappsgrid.org). See section 2 in this document for an introduction and comparison of those vocabularies.



## 1. The structure of MMIF files

The basic idea is that in essence a MMIF file needs to represent two things:

1. Media like texts, videos, images and audio recordings.
2. Annotations over those media representing information that was added by processing the media. 

Annotations are always stored separately from the media. They can be directly linked to a slice in the media (a string in a text, a shape in an image, or a time frame in a  video or audio). Annotations can also refer to other annotations, for example to specify relations between text strings. More specifically, a MMIF file contains a context, metadata, a list of media and a list of annotation views, where each view contains a list of annotation types like Segment, BoundingBox, VideoObject or NamedEntity. The top-level structure of a MMIF file is as follows:

```json
{
  "@context": "http://mmif.clams.ai/0.1.0/context/miff.json",
  "metadata": { },
  "media": [ ],
  "views": [ ]
}
```

The following sub sections describe the values of these four properties.



### 1.1. The *@context* property

In JSON-LD, keys used in the various dictionaries, including the top-level dictionary show in section 1, need to be associated with a full URI. To keep the files from overflowing with full URIs we can use a context file that defines how short names like *media* can be expanded to a full URI like http://mmif.clams.ai/0.1.0/vocab/mmif/media. The value here is the fixed URL http://mmif.clams.ai/0.1.0/context/miff.json which is a JSON-LD context document that points to the MMIF vocabulary URI http://mmif.clams.ai/0.1.0/vocab/mmif. This vocabulary defines the full of the keys used in the overal MMIF file, which includes the three keys in the example in section 1above (*metadata*, *media* and *views*) as well as many others that will be introduced below (*text*, *annotations*, *properties*, etcetera). It does not include elements from the semantic vocabularies of CLAMS and LAPPS, we will return to those later when we talk about annotations in views.



### 1.2. The *metadata* property

Includes any metadata associated with the file including MMIF version and an index of contents of views.

```json
{
  "metadata": {
    "mmif": "http://miff.clams.ai/0.1.0",
    "contains": {
      "http://mmif.clams.ai/vocabulary/1.0/Segment": ["v1", "v2"],
      "http://vocab.lappsgrid.org/Token": ["v3"]
    }
  }
}
```

The *mmif* property points at the MMIF version that is used in the document. The *contains* property stores a dictionary of annotation types with the identifiers for the views that the annotation objects occur in. This dictionary is for quick access to file content and is generated automatically from the view metadata.

> MMIF has many parts to it: specifications, schema, context files, vocabulary and SDK. For now we assume that these are all included under the one version number. We are considering whether there is a need for keeping separate versioning for those components (but would liek to avoid that).



### 1.3. The *media* property

The value is a list of media specifications where each media element has an identifier, a type, a location and optional metadata. Here is an example for a video and its transcript:

``` json
{
  "media": [
    {
      "id": "m1",
      "type": "video",
      "mime": "video/mp4",
      "location": "/var/archive/video-0012.mp4"
    },
    {
      "id": "m2",
      "type": "text",
      "mime": "text/plain",
      "location": "/var/archive/video-0012-transcript.txt"
    }
  ]
}
```

The type is one of *text*, *video*, *audio* or *image*, but in the future more types may be added. The other properties store the MIME type and the location of the media file, the latter of which is a URL or a local path to a file. Alternatively, and for text only, the media could be inline, in which case the element is represented as in the *text* property in LIF, which is a JSON [value object](http://www.w3.org/TR/json-ld/#dfn-value-object) containing a *@value* key and optionally a *@language* key:

``` json
{
  "media": [
    {
      "id": "m1",
      "type": "video",
      "mime": "video/mp4",
      "location": "/var/archive/video-0012.mp4"
    },
    {
      "id": "m2",
      "type": "text",
      "text": {
        "@value": "Fido barks",
        "@language": "en" }
    }
  ]
}
```

The value associated with *@value* is a string and the value associated with *@language* follows the rules in [BCP47](http://www.w3.org/TR/json-ld/#bib-bcp47), which for our current purposes boils down to using the two-character ISO 639 code. With inline text there is no MIME type.

With LAPPS and LIF, there was only one medium, namely the text source, and how that source came into being was not represented in any way. For MMIF the situation is different in that there are four kinds of media and for each one there can be many instances in a MMIF document. And some of those media can actually be the result of processing other media, for example when we recognize a text box in an image and run OCR over that box. This introduces a need to elaborate on the representation of media, but we will return to this in section 1.5 after we have introduced annotations.



### 1.4. The *views* property

This is where all the annotations and associated metadata live. Views contain structured information about media but are separate from those media. The value of *views* is a JSON array of view objects where each view specifies what media the annotation is over, what information it contains and what service created that information. To that end, each view has four properties:  *id*, *@context*, *metadata* and *annotations*.

```json
{
  "views": [
    {
      "id": "v1",
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",
      "metadata": { },
      "annotations": [ ]
    }
  ]
}
```

Each view has a unique identifier. Annotation elements in the view have identifiers unique to the view and these elements can be uniquely referred to from outside the view by using the view identifier and the annotation element identifier. For example, if the view above had an annotation with identfier "a8" then it could be referred to from outside the view by "v1:a8".

The *@context* property defines the vocabulary contex for the annotations in the view. Recall the *@context* property in section 1.1, which allowed terms like *metadata* to be expanded to a full URI like http://mmif.clams.ai/0.1.0/vocab/mmif/metadata. That context was not set up to deal with the annotation categories that are used in a view. For example, CLAMS applications may use an annotation type named *Segment* and we want to use the linked data aspect of JSON-LD to link that that term to a URI that contains a definition of the type, so we want to expand *Segment* to http://mmif.clams.ai/0.1.0/vocab/Segment and the CLAMS context file has the definitions to allow for that. Note that the example here points the CLAMS vocabulary, but for views with results from LAPPS services we can use the LAPPS vocabulary context. See section 2 for more on the vocabulary.

Before describing the metadata and annotation we list a few general principles relevant to views:

1. There is no limit to the number of views.
2. Services may create as many new views as they want.
3. Services may not add information to existing views, that is, views are read only, which has many advantages at the cost of some redundancy. Since views are read-only, services may not overwrite or delete information in existing views. This holds for the view’s metadata as well as the annotations.
4. Annotations in views have identifiers that are unique to the view. Views have identifiers that uniquely define them relative to other views.
5. Views should not mix annotations from CLAMS and LAPPS services.
6. Each view is associated with a semantic context.



#### 1.4.1. The *view's metadata* property

This property contains information about the annotations in a view. Here is an example for a view over a video with medium identifier "m3" with segments added by the CLAMS bars-and-tones tool:

```json
{
  "contains": {
    "http://mmif.clams.ai/0.1.0/vocabulary/Segment": {
      "unit": "seconds"
    }
  },
  "medium": "m3",
  "timestamp": "2020-05-27T12:23:45",
  "tool": "http://tools.clams.ai/bars-and-tones/1.0.5"
}
```

The *contains* dictionary has keys that refer to annotation objects in the CLAMS or LAPPS vocabulary or properties of those annotation objects (they can also refer to user-defined objects or properties) and they indicate the kind of annotations that live in the view. The value of each of those keys is a JSON object which contains metadata specified for the annotation type. The example above specifies that the view contains *Segment* annotations and the metadata property *unit* is set to "seconds". Section 2 will go into more details on how the vocabulary and the view metadata interact.

The *medium* key gives the identfier of the medium that the annotations are over.

The *timestamp* key reflects when the view was created by the tool. This is using the ISO 8601 format where the T separates the date from the time of the day. The timestamp can also be used to order views which is significant because by default arrays in JSON-LD are not ordered.

The *tool* key contains a URL that specifies what service created the annotation data. That URL should contain all information relevant for the tool: description, tool metadata, configuration etcetera. The tool URL includes a version number for the tool. It should also contain a link to the Git repository for the tool (and that repository will actually maintain all the information in the URL).

See https://github.com/clamsproject/mmif/issues/9 for a discussion on view metadata.

See https://github.com/clamsproject/mmif/issues/9 for a discussion on view metadata.



#### 1.4.2. The *view's annotations* property

The value of the annotations property on a view is a list of annotation objects. Here is an example of an annotation object:

```json
{
  "@type": "Segment",
  "properties": {
    "id": "s1",
    "start": 0,
    "end": 5,
    "segmentType": "bars-and-tones"
  }
}
```

The two required keys are *@type* and *properties*. The *@type* key has a special meaning in JSON-LD. Its value should be a URI that contains a description of the type that the annotation is of. Recall that he semantic context of the view allows the type to be expanded to the full URI.  The example has *Segment* which will be expanded to http://mmif.clams.ai/0.1.0/vocab/Segment, which is an element of the CLAMS vocabulary. For views that the LAPPS context you can use elements from the LAPPS vocabulary. See section 3 for user-defined annotation  types.

The *id* key should have a value that is unique relative to all annotation elements in the view. Other annotations can refer to this identifier either with just the identifier (for example “s1”) or the identifier with a view identifier prefix (for example “v1:s1”). If there is no prefix the current view is assumed.

The *properties* dictionary typically contains the features defined for the annotation category as defined in the vocabularies at http://mmif.clams.ai/0.1.0/vocabulary or [http://vocab.lappsgrid.org](http://vocab.lappsgrid.org/). For example, for the *Segment* annotation type the vocabulary includes the feature *segmentType* as well as the inherited features *id*, *start* and *end*. Values should be as specified in the vocabulary, values typically are strings, identifiers and integers, or lists of strings, identifiers and integers.

Technically all that is required of the keys in the properties dictionary is that they expand to a URI. In most cases, the keys reflect properties in the LAPPS vocabulary and we prefer to use the same name. So if we have a property *segmentType*, we will use *segmentType* in the properties dictionary. This implies that *segmentType* needs to be defined in the context so that it can be expanded to the correct URI in the vocabulary. And, in fact, the context has the following line that takes care of exactly that:

```txt
"segmentType": "Segment#segmentType"
```

So when using *segmentType* the full URI is http://mmif.clams.ai/0.1.0/vocabulary/Segment#segmentType.

We allow arbitrary features in the properties dictionary. However, when an arbitray feature is used the semantic context as provided by the CLAMS and LAPPS vocabulary context will not have specific rules to expand the feature a sensible URI. For example, if we add a feature *segmentLength* the feature will be expanded to a generic  http://mmif.clams.ai/0.1.0/vocabulary/segmentLength. This is not horrible, but not ideal either, see section 3 on how to deal with annotation types and features that do not occur in the dictionary.

> We have to be careful with properties that are defined on more than one annotation category. Say, for the sake of argument, that we have “pos” as a property on both the Token and NamedEntity annotation types in LAPPS. We then can use “pos” as the abbreviation of only one of the full URI and if we expand “pos” to http://vocab.lapps.grid.org/Token#pos then we need either use “NamedEntity#pos” or come up with a new abbreviated term. So far we have avoided this in CLAMS by having a property defined on one type only.

The annotations list is shallow, that is, all annotations in a view are in that list and annotations are not embedded inside of other annotations. For example, LAPPS Constituent annotations will not contain other Constituent annotations. However, in the features dictionary annotations can refer to other annotations using the identifiers of the other annotations.

Here is an other example of a view containing two bounding boxes created by the EAST text recognition tool:

```json
{
  "id": "v1",
  "metadata": {
    "contains": {
      "http://miff.clams.ai/0.1.0/vocabulary/BoundingBox": {
        "unit": "pixels" }
    },
    "medium": "image3",
    "timestamp": "2020-05-27T12:23:45",
    "tool": "http://tools.clams.io/east/1.0.4"
  },
  "annotations": [
      { "@type": "http://miff.clams.ai/0.1.0/vocabulary/BoundingBox",
        "properties": {
          "id": "bb0",
          "coordinates": [[10,20], [60,20], [10,50], [60,50]] }
      },
      { "@type": "http://miff.clams.ai/0.1.0/vocabulary/BoundingBox",
        "properties": {
          "id": "bb1",
          "coordinates": [[90,40], [110,40], [90,80], [110,80]] }
      }
    ]
  }
}
```



### 1.5. More on the *media* property

Media can be generated from other media and/or from information in views. Assume the Tesseract OCR tool that takes an image and the coordinates of a bounding box (or a new images created from the source image and coordinates) and generates a new text for the bounding box. That text will be stored as a text medium in the MMIF document and that text can be the starting point for chains of text processing where views over the medium are created.

> The alternative is to store the results in a view, but this introduces complextities when we want to run an NLP tool over the text since the text will then need to be extracted from the view first. In addition, it seemed conceptually clearer to represent text media as media, even though they may be derived.

Let's use an example of an image of a barking dog where a region of the image has been recognized by the EAST tool as containing text (image taken from http://clipart-library.com/dog-barking-clipart.html): 

<img src="pi78oGjdT-annotated.jpg" border="1" height="200"/>

In MMIF, this looks like the following (leaving out some details, coordinates somewhat made up):

```json
{
  "media": [
    {
      "id": "m1",
      "type": "image",
      "location": "/var/archive/image-0012.jpg"
    }
  ],
	"views": [
    {
      "id": "v1",
      "metadata": {
        "contains": {
          "BoundingBox": {"unit": "pixels"}},
        "medium": "m1",
    		"tool": "http://tools.clams.io/east/1.0.4"
      },
      "annotations": [
      	{
          "@type": "BoundingBox",
          "id": "bb1",
          "properties": {
            "coordinates": [[90,40], [110,40], [90,50], [110,50]] }
        }  
      ]
    }
  ]
}
```

When we add results of processing as new media then those media need to assume some of the characteristics of views and we may want to store metadata information just as we did with views:

```json
{
  "id": "m2",
  "type": "text",
  "text": {
    "@value": "yelp",
    "@language": "en"
  },
  "metadata": { 
    "source": "v1:bb1",
    "tool": "http://tools.clams.io/tesseract/1.2.1" 
  }
}
```

Note the use of *source*, which points to a bounding box annotation in view *v1*. Indirectly that alo represents that the bounding box was from image *m1*. Other metadata like timestamps and version information can/should be added as well.

> This glances over the problem that we need some way for Tesseract to know what bounding boxes to take. Either introducing some kind of type or maybe a subtype for BoundingBox like TextBox. In general, we may need to solve what we never really solved for LAPPS which is what view should be used as input for a tool.

Note that the image just had a bounding box for the part of the image with the word *yelp*, but there were three other image regions that could have been input to OCR as well. The representation above would be rather inefficient because it would repeat similar metadata over and over again. So we introduce a mechanism that in a way does the same as the annotations list in a view in that it allows metadata to be stored only once:

```json
{
  "id": "m2",
  "type": "text/plain",
  "metadata": { 
    "source": "v1",
    "tool": "http://tools.clams.io/tesseract/1.2.1" 
  },
  "submedia": [
    { "id": "sm1", "annotation": "bb1", "text": { "@value": "yelp" }},
    { "id": "sm2", "annotation": "bb2", "text": { "@value": "Arf" }},
    { "id": "sm3", "annotation": "bb3", "text": { "@value": "bark" }},
    { "id": "sm4", "annotation": "bb4", "text": { "@value": "woof" }}
  ]
}
```

The media set as a whole can be referred to with "m2", and the submedia by concatenating the medium and submedium identifiers as in "m2:sm1". Note how indivudual media have *annotation* properties that pick out the bounding box in the view that the text media were created from.

> Note that this is all rather preliminary and that experimentation is needed.



## 2. MIFF and the CLAMS Vocabulary



## 3. User-defined extensions

The value of *@type* in an annotation is typically an element of the CLAMS or LAPPS vocabulary, but you can also enter a user-defined annotation category defined elsewhere, for example by the creator of a tool. If a user-defined category is used then it would be defined outside of the CLAMS or LAPPS vocabulary and in that case the user should use the full URI.

> To be finished



## 4. Compatibility with LAPPS Tools

A converter is required to run LIF tools with MMIF as input. Here's two possible scenarios that the converter must be able to handle.

##### Running LAPPS tools on the primary text sources

In this simple case, a dummy LIF payload should be generated by the converter with the contents of the primary text source file taken as `text`. LAPPS tools can run taking the dummy LIF and returns a LIF with a number of new views generated. Then the converter takes that regular LIF payload and inserts new views in the LIF to the original MMIF.

##### Running LAPPS tools on existing text annotation objects

**This scenario includes running LAPPS tools on text sources generated from the primary AV meterial.**

* OCR from video -> an annotation per box?  -> then, should LAPPS tools handle each box as one "document"? or can we concatenate all text from all boxes linearly and pass to linguistics tools?
  * THIS case needs a lot more thoughts.
* ASR from audio -> an annotation for an entire audio stream? -> then it's easy, treat it as one document
* forced-aligned text -> forced alignment assumes the existence of a external original primary text file -> it's easy, treat it as primary text source



## 5. MIFF Examples



## 6. Related Work

An exchange format for multimodal annotations.
Schmidt et al. 2008. An exchange format for multimodal annotations. In *International LREC Workshop on Multimodal Corpora*.

IIIF (International Image Interoperability Framework). 
See https://iiif.io/ and https://iiif.io/api/#current-specifications.

CMDI (Component MetaData Infrastructure).
https://www.clarin.eu/content/component-metadata
Broeder et all. 2012. CMDI: a component meta- data infrastructure. In *Describing LRs with metadata: towards flexibility and interoperability in the documen- tation of LR workshop programme*. 

Image and video annotation tools.




