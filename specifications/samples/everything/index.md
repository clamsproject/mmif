---
layout: page
title: MMIF Specification
subtitle: Version 0.2.0
---

# Example: Everything and the kitchen sink

To see the full example scroll down to the end or open the [raw json file](raw.json).

This is an example with a bunch of different annotations created by a variety of tools. For the input we have  a short totally made up video which starts with some bars-and-tone and a simple slate. Those are followed by about a dozen seconds of a talking head followed by an image of a barking dog.

<img src="images/newshour-loud-dogs.jpg" />

The timeline includes markers for seconds. In the views below all anchors will be using milliseconds.

We apply the following processing tools:

1. bars-and-tones
1. slate extraction
1. audio segmentation
1. Kaldi speech recognition and alignment
1. EAST
1. Tesseract
1. slate parsing
1. named entity recognition

Following now are short explanations of some frgaments of the full MMIF file, some application output was explained in more detail in other examples, refer to those for more details.

### Extracting time frames

The first three steps are straightforward and all result in views with time frame annotations (views with id=v1, id=v2 and id=v3). The bars-and-tones and slate extraction applications each find one time frame and the audio segmenter finds two segments with the second one being a speech time frame that starts at about 5500ms from the start. 

```json
{
	"@type": "http://mmif.clams.ai/0.2.0/vocabulary/TimeFrame",
	"properties": {
		"id": "tf2",
		"frameType": "speech",
		"start": 5500,
		"end": 22000 }
}
```

This time frame will provide the input to Kaldi.

### Kaldi speech recognition

kaldi creates one view (with id=v4) which has

- a text document
- an alignment of that document with the speech time frame from the segmenter
- a list of tokens for the document
- a list of time frames corresponding to each token
- a list of alignments between the tokens and the time frames

Note that a text document can refer to its text by either using the *text* property which contains the text verbatim or by referring to an external file with the *location* property, here we use the second approach:

```json
{
	"@type": "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument",
	"properties": {
		"id": "td1",
		"mime": "text/plain",
		"location": "/var/processed/transcript-002.txt" }
}
```

For the sake of argument, we assume perfect speech recognition and that the content of the external file is as follows. 

>  Hello, this is Jim Lehrer with the NewsHour on PBS. In the nineteen eighties, barking dogs have increasingly become a problem in urban areas.

This text is aligned with the second time frame from the segmenter.

```json
{
	"@type": "http://mmif.clams.ai/0.2.0/vocabulary/Alignment",
	"properties": {
		"id": "a1",
		"source": "v3:tf2",
		"target": "td1" }
}
```

See below for all the tokens, time frames for each token and the alignment between the token and the time frame.

### EAST and Tesseract

blah

### Slate parsing

blah

### Named entity recognition

blah

## Full MMIF File

```json
{
}
```



