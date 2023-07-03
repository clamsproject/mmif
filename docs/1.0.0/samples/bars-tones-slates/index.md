---
layout: single
classes: wide
title: MMIF Specification
subtitle: Version 1.0.0
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
  - What kind of annotations are in the view and what metadata are there on those annotations (for example, in the view with id=v2, the *contains* field has a property "http://mmif.clams.ai/vocabulary/TimeFrame/v1" with a dictionary as the value and that dictionary contains the metadata. Here the metadata specify what document the annotations are over what unit is used for annotation offsets.

Only one annotation is shown for each view, this is to keep the file as small as possible. Of course, often the bars-and-tones and slate views often have only one annotation so it is likely only the tokens view where annotations were left out.



## Full MMIF File

```json
{% include_relative raw.json %}
```



