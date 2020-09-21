---
layout: page
title: MMIF Specification
subtitle: Version 0.2.0
---

# Example: Bars and Tones and Slates

To see the full example scroll down to the end or open the [raw json file](raw.json).

This is a minimal example that contains two media documents, one pointing at a video and the other at a transcript. For the first document there are two views, one with bars-and-tone annotations and one with slate annotations. For the second document there is one view with the results of a tokenizer. This example file, while minimal, has everything required by MMIF.

Some notes:

- The metadata just specify the MMIF version.
- Both media documents in the *documents* list refer to a location on a local disk or a mounted disk. If this document is not on a local disk or mounted disk then URLs should be used. 
- Each view has some metadata spelling out several kinds of things:
  - The application that created the view.
  - A timestamp of when the view was created.
  - What kind of annotations are in the view and what metadata are there on those annotations (for example, in the view with id=v2, the *contains* field has a property "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame" with a dictionary as the value and that dictionary contains the metadata. Here the metadata specify what document the annotations are over what unit is used for annotation offsets.

Only one annotation is shown for each view, this is to keep the file as small as possible. Of course, often the bars-and-tones and slate views often have only one annotation so it is likely only the tokens view where annotations were left out.



## Full MMIF File

```json
{
  "metadata": {
    "mmif": "http://mmif.clams.ai/0.2.0" },

  "documents": [
    {
      "@type": "http://mmif.clams.ai/0.2.0/vocabulary/VideoDocument",
      "properties": {
        "id": "m1",
        "mime": "video/mp4",
        "location": "/var/archive/video-0012.mp4" }
    },
    {
      "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument",
      "properties": {
        "id": "m2",
        "mime": "text/plain",
        "location": "/var/archive/video-0012-transcript.txt" }
    }
  ],

  "views": [

    {
      "id": "v1",

      "metadata": {
        "app": "http://apps.clams.ai/bars-and-tones/1.0.5",
        "timestamp": "2020-05-27T12:23:45",
        "contains": {
          "http://mmif.clams.ai/0.1.0/vocabulary/TimeFrame": {
            "document": "m1",
            "unit": "seconds" } },
      },

      "annotations": [
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "id": "s1",
            "start": 0,
            "end": 5,
            "frameType": "bars-and-tones" }
        }
      ]
    },

    {
      "id": "v2",

      "metadata": {
        "app": "http://apps.clams.ai/slates/1.0.3",
        "timestamp": "2020-05-27T12:23:45",
        "contains": {
          "http://mmif.clams.ai/0.1.0/vocabulary/TimeFrame": {
            "document": "m1",
            "unit": "seconds" } }
      },

      "annotations": [
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "id": "s1",
            "start": 25,
            "end": 38,
            "frameType": "slate" }
        }
      ]
    },

    {
      "id": "v3",

      "metadata": {
        "app": "http://apps.clams.ai/spacy/1.3.0",
        "timestamp": "2020-05-27T12:25:15",
        "contains": {
          "http://vocab.lappsgrid.org/Token": {
            "document": "m2" } }
      },

      "annotations": [
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "properties": {
            "id": "s1",
            "start": 0,
            "end": 3,
            "word": "The" }
        }
      ]
    }

  ]
}
```



