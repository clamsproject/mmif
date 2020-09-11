---
layout: page
title: MMIF Specification
subtitle: Version 0.2.0
---

# Example: Segmenter, Kaldi and NER 

This example contains one audio document and three views: one created by the audio segmenter, one created by Kaldi and one created by a named entity recognizer. 

We now give fragments of the three views, each with some comments.

To see the full example scroll down to the end or open the [raw json file](raw.json).

### Fragment 1: the Segmenter view

Metadata:

```json
{
  "app": "http://mmif.clams.ai/apps/audio-segmenter/0.2.1",
  "contains": {
    "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame": {
      "unit": "milliseconds",
      "document": "m1" } 
}
```

All time frames in the view are anchored to document "m1" and milliseconds are used for the unit.

Partial  annotations list:

```json
[
  {
    "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
    "properties": {
      "id": "tf1",
      "frameType": "speech",
      "start": 17,
      "end": 132 }
  },
  {
    "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
    "properties": {
      "frameType": "non-speech",
      "id": "tf2",
      "start": 132,
      "end": 194 }
  }
]
```

Two of the three time frames are shown here: one for a speech segment and one for a non-speech segment. Only the speech frames are input to Kaldi.

### Fragment 2: the Kaldi view

Metadata:

```json
{
  "app": "http://mmif.clams.ai/apps/kaldi/0.2.1",
  "contains": {
    "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument": {},
    "http://vocab.lappsgrid.org/Token": {},
    "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame": {
      "unit": "milliseconds",
      "document": "m1" },
    "http://mmif.clams.ai/0.2.0/vocabulary/Alignment": {} }
}
```

Kaldi creates five kinds of annotations:

1. Text documents for each speech time frame.
2. Tokens for each text document.
3. Time frames that correspond to each token, these time frames are all anchored to document "m1".
4. Alignments from speech frames to text documents, the speech frames were created by the segmenter. 
5. Alignments from time frames to tokens.

The annotations list has two documents, one shown here:

```json
{
  "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument",
  "properties": {
    "id": "td1",
    "text": {
      "@value": "Fido barks" } }
}
```

This document does not know it's history, but Kaldi also creates an alignment that spells out what time frame the document is aligned to:

```json
{
  "@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
  "properties": {
    "id": "a1",
    "source": "v1:tf1",
    "target": "td1" }
}
```

Each document is tokenized, here showing one token from the document above:

```json
{
  "@type": "http://vocab.lappsgrid.org/vocabulary/Token",
  "id": "t1",
  "properties": {
    "document": "v2:td1",
    "start": 0,
    "end": 4,
    "text": "Fido" }
}
```

Note how the token uses the *document* property to specify what document this is an annotation of. This has to be specified for each token because the Kaldi view has more than one text document. 

The token is associated with a time frame in document "m1":

```json
{
  "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
  "properties": {
    "id": "tf1",
    "start": 17,
    "end": 64 }
}
```

And the token and time frame are linked by an alignment:

```json
{
  "@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
  "properties": {
    "id": "a2",
    "source": "tf1",
    "target": "t1" }
}
```

If Kaldi had run on the entire document (not using just speech frames) then the result could be a bit different in that there would be just one text document and the token metadata in the view could specify that so tokens would not have individual *document* properties.

### Fragment 3: the NET view

Metadata:

```json
{
  "app": "http://mmif.clams.ai/apps/stanford-ner/0.2.1",
  "contains": {
    "http://vocab.lappsgrid.org/NamedEntity": {} }
}
```

One of the two named entity annotations:

```json
{
  "@type": "http://vocab.lappsgrid.org/NamedEntity",
  "properties": {
    "id": "ne1",
    "document": "v2:td1",
    "start": 0,
    "end": 4,
    "category": "Person",
    "word": "Fido" }
}
```

Notice how the entity anchors to one of the document created by Kaldi.



## Full MMIF File

```json
{
  "metadata": {
    "mmif": "http://miff.clams.ai/0.2.0" },

  "documents": [
    {
      "@type": "http://mmif.clams.ai/0.2.0/vocabulary/AudioDocument",
      "properties": {
        "id": "m1",
        "mime": "audio/mpeg",
        "location": "/var/archive/audio-002.mp3" }
    }
  ],

  "views": [

    {
      "id": "v1",
      "metadata": {
        "app": "http://mmif.clams.ai/apps/audio-segmenter/0.2.1",
        "contains": {
          "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame": {
            "unit": "milliseconds",
            "document": "m1" } }
      },
      "annotations": [
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "id": "tf1",
            "frameType": "speech",
            "start": 17,
            "end": 132 }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "frameType": "non-speech",
            "id": "tf2",
            "start": 132,
            "end": 194 }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "id": "tf3",        
            "frameType": "speech",
            "start": 194,
            "end": 342 }
        }
      ]
    },

    {  
      "id": "v2",
      "metadata": {
        "app": "http://mmif.clams.ai/apps/kaldi/0.2.1",
        "contains": {
          "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument": {},
          "http://vocab.lappsgrid.org/Token": {},
          "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame": {
            "unit": "milliseconds",
            "document": "m1" },
          "http://mmif.clams.ai/0.2.0/vocabulary/Alignment": {} }
      },
      "annotations": [
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument",
          "properties": {
            "id": "td1",
            "text": {
              "@value": "Fido barks" } }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
          "properties": {
            "id": "a1",
            "source": "v1:tf1",
            "target": "td1" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/vocabulary/Token",
          "properties": {
            "id": "t1",
            "document": "v2:td1",
            "start": 0,
            "end": 4,
            "text": "Fido" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/vocabulary/Token",
          "properties": {
            "id": "t2",
            "document": "v2:td1",
            "start": 5,
            "end": 10,
            "text": "barks" }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "id": "tf1",
            "start": 17,
            "end": 64 }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "id": "tf2",
            "start": 65,
            "end": 132 }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
          "properties": {
            "id": "a2",
            "source": "tf1",
            "target": "t1" }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
          "properties": {
            "id": "a3",
            "source": "tf2",
            "target": "t2" }
        },

        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument",
          "properties": {
            "id": "td2",
            "textSource": "v1:tf3",
            "text": {
              "@value": "Fluffy sleeps" } }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
          "properties": {
            "id": "a4",
            "source": "v1:tf3",
            "target": "td2" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/vocabulary/Token",
          "properties": {
            "id": "t3",
            "document": "v2:td2",
            "start": 0,
            "end": 6,
            "text": "Fluffy" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/vocabulary/Token",
          "properties": {
            "id": "t4",
            "document": "v2:td2",
            "start": 7,
            "end": 13,
            "text": "sleeps" }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "id": "tf3",
            "start": 194,
            "end": 240 }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
          "properties": {
            "id": "tf4",
            "start": 241,
            "end": 342 }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
          "properties": {
            "id": "a5",
            "source": "tf3",
            "target": "t3" }
        },
        {
          "@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
          "properties": {
            "id": "a5",
            "source": "tf4",
            "target": "t4" }
        },
      ]
    },

    {
      "id": "v3",
      "metadata": {
        "app": "http://mmif.clams.ai/apps/stanford-ner/0.2.1",
        "contains": {
          "http://vocab.lappsgrid.org/NamedEntity": {} }
      },
      "annotations": [
        {
          "@type": "http://vocab.lappsgrid.org/NamedEntity",
          "properties": {
            "id": "ne1",
            "document": "v2:td1",
            "start": 0,
            "end": 4,
            "category": "Person",
            "word": "Fido" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/NamedEntity",
          "properties": {
            "id": "ne2",
            "document": "v2:td2",
            "start": 0,
            "end": 6,
            "category": "Person",
            "word": "Fluffy" }
        }
      ]
    }

  ]
}
```

