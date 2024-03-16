---
layout: page
title: MMIF Specification
subtitle: Version 1.0.3
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
    "http://mmif.clams.ai/vocabulary/TimeFrame/v4": {
      "timeUnit": "milliseconds",
      "document": "m1" } 
}
```

All time frames in the view are anchored to document "m1" and milliseconds are used for the unit.

Partial  annotations list:

```json
[
  {
    "@type": "http://mmif.clams.ai/vocabulary/TimeFrame/v4",
    "properties": {
      "id": "tf1",
      "frameType": "speech",
      "start": 17,
      "end": 132 }
  },
  {
    "@type": "http://mmif.clams.ai/vocabulary/TimeFrame/v4",
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
    "http://mmif.clams.ai/vocabulary/TextDocument/v1": {},
    "http://vocab.lappsgrid.org/Token": {},
    "http://mmif.clams.ai/vocabulary/TimeFrame/v4": {
      "timeUnit": "milliseconds",
      "document": "m1" },
    "http://mmif.clams.ai/vocabulary/Alignment/v1": {} }
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
  "@type": "http://mmif.clams.ai/vocabulary/TextDocument/v1",
  "properties": {
    "id": "td1",
    "text": {
      "@value": "Fido barks" } }
}
```

This document does not know it's history, but Kaldi also creates an alignment that spells out what time frame the document is aligned to:

```json
{
  "@type": "http://mmif.clams.ai/vocabulary/Alignment/v1",
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
  "@type": "http://mmif.clams.ai/vocabulary/TimeFrame/v4",
  "properties": {
    "id": "tf1",
    "start": 17,
    "end": 64 }
}
```

And the token and time frame are linked by an alignment:

```json
{
  "@type": "http://mmif.clams.ai/vocabulary/Alignment/v1",
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
{% include_relative raw.json %}
```
