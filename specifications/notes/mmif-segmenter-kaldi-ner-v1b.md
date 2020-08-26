# MMIF Example — Segmenter, Kaldi and NER 

This example contains:

-  one audio medium
- one view created by the audio segmenter
- one view created by Kaldi
- one view created by a named entity recognizer

Notice how the entity recognizer ran over the documents in the Kaldi view.

```json
{
  "metadata": {
    "mmif": "http://miff.clams.ai/0.1.0" },

  "documents": [
    {
      "@type": "http://mmif.clams.ai/0.1.0/AudioDocument",
      "properties": {
        "id": "m1",
        "mime": "audio/mp3",
        "location": "/var/archive/audio-002.mp3" }
    }
  ],

  "views": [

    {
      "id": "v1",
      "metadata": {
        "contains": {
          "http://mmif.clams.ai/0.1.0/TimeFrame": {
            "unit": "milliseconds",
            "document": "m1" } },
        "app": "http://mmif.clams.ai/apps/segmenter/0.2.1",
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
            "unit": "milliseconds",
            "document": "m1" },
          "http://mmif.clams.ai/0.1.0/Alignment": {} },
        "app": "http://mmif.clams.ai/apps/kaldi/0.2.1"
      },
      "annotations": [
        {
          "@type": "http://mmif.clams.ai/0.1.0/TextDocument",
          "properties": {
            "id": "td1",
            "text": {
              "@value": "Fido barks" } }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/Alignment",
          "properties": {
            "id": "a1",
            "source": "v1:tf1",
            "target": "td1" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "id": "t1",
          "properties": {
            "document": "v2:td1",
            "start": 0,
            "end": 4,
            "text": "Fido" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "id": "t2",
          "properties": {
            "document": "v2:td1",
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
          "id": "a2",
          "properties": {
            "source": "tf1",
            "target": "t1" }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/Alignment",
          "id": "a3",
          "properties": {
            "source": "tf2",
            "target": "t2" }
        },

        {
          "@type": "http://mmif.clams.ai/0.1.0/TextDocument",
          "properties": {
            "id": "td2",
            "textSource": "v1:tf3",
            "text": {
              "@value": "Fluffy sleeps" } }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/Alignment",
          "properties": {
            "id": "a4",
            "source": "v1:tf3",
            "target": "td2" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "id": "t3",
          "properties": {
            "document": "v2:td2",
            "start": 0,
            "end": 6,
            "text": "Fluffy" }
        },
        {
          "@type": "http://vocab.lappsgrid.org/Token",
          "id": "t4",
          "properties": {
            "document": "v2:td2",
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
          "id": "a5",
          "properties": {
            "source": "tf3",
            "target": "t3" }
        },
        {
          "@type": "http://mmif.clams.ai/0.1.0/Alignment",
          "id": "a5",
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
        "app": "http://mmif.clams.ai/apps/stanford-ner/0.2.1"
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
