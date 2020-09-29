# MMIF Example — Segmenter, Kaldi and NER 

This example contains:

-  one audio medium
- one view created by the audio segmenter
- two text media created by Kaldi, grouped together
- one view created by Kaldi
- one view created by a named entity recognizer

Notice that there still is an issue with the context in the Kaldi view since it only deals with the CLAMS types and not the LAPPS types.

We chose to not take this option, this file will be deprecated.

```json
{
  "metadata": {
    "mmif": "http://mmif.clams.ai/0.1.0" },

  "media": [
    {
      "@type": "http://mmif.clams.ai/0.1.0/AudioDocument",
      "properties": {
        "id": "m1",
        "mime": "audio/mp3",
        "location": "/var/archive/audio-002.mp3" }
    },
    {
      "@type": "http://mmif.clams.ai/0.1.0/TextDocument",
      "metadata": {
        "tool": "http://mmif.clams.ai/apps/kaldi/0.2.1",
        "textSource": "v1:tf1"
      },
      "properties": {
        "id": "m2" },
      "submedia": [
        {
          "@type": "http://mmif.clams.ai/0.1.0/TextDocument",
          "metadata": {
            "textSource": "v1:tf1" 
          },
          "properties": {
            "id": "sub1",
            "text": {
              "@value": "Fido barks" }}
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/TextDocument",
          "metadata": {
            "textSource": "v1:tf3" 
          },
          "properties": {
            "id": "sub2",
            "text": {
              "@value": "Fluffy sleeps" }}
        }
      ], 
    }
  ],

  "views": [

    {
      "id": "v1",
      "metadata": {
        "contains": {
          "http://mmif.clams.ai/0.1.0/TimeFrame": {
            "unit": "milliseconds" } },
        "medium": "m1",
        "tool": "http://mmif.clams.ai/apps/segmenter/0.2.1",
      },
      "annotations": [
        {
          "@type": "http://mmif.clams.ai/0.1.0/TimeFrame",
          "properties": {
            "id": "tf1",
            "frameType": "language",
            "start": 17,
            "end": 132 }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/TimeFrame",
          "properties": {
            "frameType": "non-language",
            "id": "tf2",
            "start": 132,
            "end": 194 }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/TimeFrame",
          "properties": {
            "id": "tf3",        
            "frameType": "language",
            "start": 194,
            "end": 342 }
        }
      ]
    },

    {  
      "id": "v2",
      "metadata": {
        "contains": {
          "http://mmif.clams.ai/0.1.0/TextDocument": {},
          "http://vocab.lappsgrid.org/Token": {},
          "http://mmif.clams.ai/0.1.0/TimeFrame": {
            "unit": "milliseconds" },
          "http://mmif.clams.ai/0.1.0/Alignment": {
            "sourceType": "http://mmif.clams.ai/0.1.0/TimeFrame",
            "targetType": "http://vocab.lappsgrid.org/Token" } },
        "medium": "m1",
        "tool": "http://mmif.clams.ai/apps/kaldi/0.2.1"
      },
      "annotations": [
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "id": "t1",
          "properties": {
            "document": "m2:sub1",
            "start": 0,
            "end": 4,
            "text": "Fido" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "id": "t2",
          "properties": {
            "document": "m2:sub1",
            "start": 5,
            "end": 10,
            "text": "barks" }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/TimeFrame",
          "id": "tf1",
          "properties": {
            "start": 17,
            "end": 64 }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/TimeFrame",
          "id": "tf2",
          "properties": {
            "start": 65,
            "end": 132 }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/Alignment",
          "id": "a1",
          "properties": {
            "source": "tf1",
            "target": "t1" }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/Alignment",
          "id": "a2",
          "properties": {
            "source": "tf2",
            "target": "t2" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "id": "t3",
          "properties": {
            "document": "m2:sub2",
            "start": 0,
            "end": 6,
            "text": "Fluffy" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "id": "t4",
          "properties": {
            "document": "m2:sub2",
            "start": 7,
            "end": 13,
            "text": "sleeps" }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/TimeFrame",
          "id": "tf3",
          "properties": {
            "start": 194,
            "end": 240 }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/TimeFrame",
          "id": "tf4",
          "properties": {
            "start": 241,
            "end": 342 }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/Alignment",
          "id": "a3",
          "properties": {
            "source": "tf3",
            "target": "t3" }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/Alignment",
          "id": "a4",
          "properties": {
            "source": "tf4",
            "target": "t4" }
        },
      ]
    },

    {
      "id": "v3",
      "metadata": {
        "contains": {
          "http://vocab.lappsgrid.org/NamedEntity": {} },
        "tool": "http://mmif.clams.ai/apps/stanford-ner/0.2.1"
      },
      "annotations": [
        {
          "@type": "http://vocab.lappsgrid.org/NamedEntity",
          "properties": {
            "id": "ne1",
            "document": "m2:sub1",
            "start": 0,
            "end": 4,
            "category": "Person",
            "word": "Fido" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/NamedEntity",
          "properties": {
            "id": "ne2",
            "document": "m2:sub2",
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

