A well-formed LIF looks like this (scheme can change in the future). 
``` json
{
  "discriminator": "http://vocab.lappsgrid.org/ns/media/jsonld#lif",
                                                ## file type indicator
  "payload": {                                  ## actual data contents
    "@context": "http://vocab.lappsgrid.org/context-1.0.0.jsonld",  
                                                ## json scheme definition
    "metadata": {},
    "text": {                                   ## text shared across all views
      "@value": "SOME_TEXT",
      "@language": "en"
    },
    "views": [
      {
        "id": "v1",
        "metadata": {
          "contains": {                         ## what's in this individual view
            "http://vocab.lappsgrid.org/NamedEntity": {
              "producer": "edu.brandeis.cs.lappsgrid.stanford.corenlp.NamedEntityRecognizer:2.0.4",
              "type": "ner:stanford"
            }
          }
        },
        "annotations": [                        ## list of annotations
          {
            "id": "ne_0",
            "start": 0,
            "end": 3,
            "@type": "http://vocab.lappsgrid.org/Location",
            "features": {
              "word": "SOME",
              "another-feature": "another-value"
            }
          },
          {
            "id": "ne_1",
            "start": 5,
            "end": 8,
            "@type": "http://vocab.lappsgrid.org/Person",
            "features": {
              "word": "TEXT"
            }
          }
        ]                                       ## end of annotations
      },
      {
        "id":"v2", 
      "metadata": {},
      "annotations": []
      }
    ] 
  }                                             ## end of payload
}

```

Based on the LIF scheme, a draft of MMIF can be something like

```json
{
  "discriminator": "CLAMS-MIF",
                                                ## file type indicator
  "payload": {                                  ## actual data contents
    "@context": "SOME-MMIF-SCHEME-DEFINITION",  
    "metadata": {"first-generation-time": "YYYY/MM/DD:hh:MM:ss"},
    "input": [                                  ## input, instead of "text", needs to be a list
      {"id": "media-id", "type": "video", "@location": "SOME_URI", 
                                                ## location can be local (and should for now)
        "creation-date": "yyyy/mm/dd", 
        "OTHER_METADATA": "OTHER_VALUE"},   
        {"id": "transcript-id", "type": "text", "@location": "ANOTHER_URI", 
          "language": "en", 
          "MORE_METADATA": "MORE_VALUE"}
    ],
    "contains": ["bar-detection", "vanilla-forced-alignment"],
                                                ## "contains" at the top level 
                                                ## to enable workflow engines to 'sniff' 
    "views": [
      {
        "id": "v1",
        "metadata": {
          "contains": {                         ## what's in this individual view
            "bar-detection": {
              "producer": "some-bar-detector",
              "annotation_date": "yyyy/mm/dd",
              "@tagset": "TAGSET_DEFINITION_URI"
                                                ## actually, noise-detention does not have tagset
            }
          }
        },
        "annotations": [                        ## list of annotations
          {
            "id": "bar_0",
            "start": 0,                         ## can be timestamp (milisecond) or frame number
            "end": 9000,                        ## bar detected from 0 - 9 seconds
            "@type": "bar-detection"
          },
          {
            "id": "bar_1",
            "start": 25000,
            "end": 31000,                       ## another bar detected from 25 - 31 seconds
            "@type": "bar-detection"
          }
        ]                                       ## end of annotations
      },
      {
        "id":"v2", 
        "metadata": {
          "contains": {                         ## what's in this individual view
            "bar-detection": {
              "producer": "some-bar-detector",
              "annotation_date": "yyyy/mm/dd",
              "@tagset": "TAGSET_DEFINITION_URI"
                                                ## actually, noise-detention does not have tagset
            }
          }
        },
        "annotations": [
          {
            "id": "fa_1",
            "start": 9100,
            "end": 10000,   
            "@type": "vanilla-forced-align",
            "features": {
              "token": "first"
            }                                   ## "first" token aligned 00:09 - 00:10

          }, 
          { fa_2 aligning the second token to time interval }, 
          { and more tokens aligned }
        ]
      }
    ] 
  }                                             ## end of payload
}
```
