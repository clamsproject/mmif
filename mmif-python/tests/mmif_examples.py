examples = dict(example1="""{
  "@context": "http://mmif.clams.ai/0.1.0/context/mmif.json",
  "metadata": {
    "mmif": "http://mmif.clams.ai/0.1.0"
  },
  "media": [
    {
      "id": "m1",
      "type": "image",
      "mime": "image/jpeg",
      "location": "/var/archive/image-0012.jpg"
    },
    {
      "id": "m2",
      "type": "text",
      "text": {
        "@value": "yelp",
        "@language": "en"
      },
      "metadata": {
        "source": "v1:bb1",
        "app": "http://apps.clams.io/tesseract/1.2.1"
      }
    }
  ],
  "views": [
    {
      "id": "v1",
      "metadata": {
        "contains": {
          "BoundingBox": {"unit": "pixels"}
        },
        "medium": "m1",
        "app": "http://apps.clams.io/east/1.0.4"
      },
      "annotations": [
        {
          "@type": "BoundingBox",
          "properties": {
            "id": "bb1",
            "coordinates": [[90,40], [110,40], [90,50], [110,50]] }
        }
      ]
    }
  ]
}""",

                example2="""{
  "@context": "http://mmif.clams.ai/0.1.0/context/mmif.json",

  "metadata": {
    "mmif": "http://mmif.clams.ai/0.1.0",
    "contains": {
      "http://mmif.clams.ai/1.0/vocabulary/Segment": ["v1"],
      "http://vocab.lappsgrid.org/NamedEntity": ["v2"]
    }
  },

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
  ],

  "views": [
    {
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",
      "id": "v1",
      "metadata": {
        "medium": "m1",
        "timestamp": "2020-05-27T12:23:45",
        "app": "http://apps.clams.ai/bars-and-tones/1.0.5",
        "contains": {
          "Segment": { "unit": "seconds" }
        }
      },

      "annotations": [
        {
          "@type": "Segment",
          "properties": {
            "id": "s1",
            "start": 87,
            "end": 145,
            "segmentType": "bars-and-tones",
            "undefinedProperty": "howdy" 
          }
        }
      ]
    },

    {
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-lapps.json",
      "id": "v2",
      "metadata": {
        "medium": "m2",
        "timestamp": "2020-05-27T12:23:45",
        "app": "http://apps.clams.ai/lapps/stanford-ner/1.3.2",
        "contains": {
          "NamedEntity": { "namedEntityCategorySet": "Stanford" }
        }
      },

      "annotations": [
        {
          "@type": "NamedEntity",
          "properties": {
            "id": "ne1",
            "start": 12,
            "end": 45,
            "type": "location" 
          }
        }
      ]
    }
  ]
}
""",

                example3="""{
  "@context": "http://mmif.clams.ai/0.1.0/context/mmif.json",

  "metadata": {
    "mmif": "http://mmif.clams.ai/0.1.0",
    "contains": {
      "http://mmif.clams.ai/1.0/vocabulary/Segment": ["v1"],
      "http://mmif.clams.ai/0.1.0/vocabulary/TimePoint": ["v1"],
      "http://vocab.lappsgrid.org/NamedEntity": ["v2"]
    }
  },

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
  ],

  "views": [
    {
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",
      "id": "v1",
      "metadata": {
        "medium": "m1",
        "timestamp": "2020-05-27T12:23:45",
        "app": "http://apps.clams.ai/bars-and-tones/1.0.5",
        "contains": {
          "Segment": { "unit": "seconds" },
          "TimePoint": { "unit": "seconds" }
        }
      },

      "annotations": [
        {
          "@type": "Segment",
          "properties": {
            "id": "s1",
            "start": 87,
            "end": 145,
            "segmentType": "bars-and-tones",
            "undefinedProperty": "howdy" 
          }
        },
        {
          "@type": "TimePoint",
          "properties": {
            "id": "t1",
            "point": 5
          }
        }
      ]
    },

    {
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-lapps.json",
      "id": "v2",
      "metadata": {
        "medium": "m2",
        "timestamp": "2020-05-27T12:23:45",
        "app": "http://apps.clams.ai/lapps/stanford-ner/1.3.2",
        "contains": {
          "NamedEntity": { "namedEntityCategorySet": "Stanford" }
        }
      },

      "annotations": [
        {
          "@type": "NamedEntity",
          "properties": {
            "id": "ne1",
            "start": 12,
            "end": 45,
            "type": "location" 
          }
        }
      ]
    }
  ]
}
""",

                example4="""{
  "@context": "http://mmif.clams.ai/0.1.0/context/miff.json",

  "metadata": {
    "mmif": "http://miff.clams.ai/0.1.0",
    "contains": {
      "http://mmif.clams.ai/vocabulary/0.1.0/TimeFrame": ["v1", "v2"],
      "http://vocab.lappsgrid.org/Token": ["v3"]
    }
  },

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
  ],

  "views": [

    {
      "id": "v1",
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",

      "metadata": {
        "contains": {
          "http://mmif.clams.ai/0.1.0/vocabulary/TimeFrame": {
            "unit": "seconds"
          }
        },
        "medium": "m1",
        "timestamp": "2020-05-27T12:23:45",
        "app": "http://apps.clams.ai/bars-and-tones/1.0.5"
      },

      "annotations": [
        {
          "@type": "TimeFrame",
          "properties": {
            "id": "s1",
            "start": 0,
            "end": 5,
            "frameType": "bars-and-tones"
          }
        }
      ]
    },

    {
      "id": "v2",
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",

      "metadata": {
        "contains": {
          "http://mmif.clams.ai/0.1.0/vocabulary/TimeFrame": {
            "unit": "seconds"
          }
        },
        "medium": "m1",
        "timestamp": "2020-05-27T12:23:45",
        "app": "http://apps.clams.ai/slates/1.0.3"
      },

      "annotations": [
        {
          "@type": "TimeFrame",
          "properties": {
            "id": "s1",
            "start": 25,
            "end": 38,
            "frameType": "slate"
          }
        }
      ]
    },

    {
      "id": "v3",
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-lapps.json",

      "metadata": {
        "contains": {
          "http://vocab.lappsgrid.org/Token": {}
        },
        "medium": "m2",
        "timestamp": "2020-05-27T12:25:15",
        "app": "http://apps.clams.ai/slates/1.0.3"
      },

      "annotations": [
        {
          "@type": "Token",
          "properties": {
            "id": "s1",
            "start": 0,
            "end": 3,
            "word": "The"
          }
        }
      ]
    }

  ]
}
""")

anno1 = """{
          "@type": "Token",
          "properties": {
            "id": "token1",
            "start": 0,
            "end": 3,
            "word": "The"
          }
        }"""

anno2 = """{
  "@type": "TimePoint",
  "properties": {
    "id": "t1",
    "point": 5
  }
}"""

view1 = """{
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",
      "id": "v1",
      "metadata": {
        "medium": "m1",
        "timestamp": "2020-05-27T12:23:45",
        "app": "http://apps.clams.ai/bars-and-tones/1.0.5",
        "contains": {
          "Segment": { "unit": "seconds" }
        }
      },

      "annotations": [
        {
          "@type": "Segment",
          "properties": {
            "id": "s1",
            "start": 87,
            "end": 145,
            "segmentType": "bars-and-tones",
            "undefinedProperty": "howdy" 
          }
        },
        {
          "@type": "TimePoint",
          "properties": {
            "id": "t1",
            "point": 5
          }
        }
      ]
    }"""

ext_video_medium = """{
      "id": "m3",
      "type": "video",
      "mime": "video/mp4",
      "location": "/var/archive/video-0012.mp4"
    }"""

ext_text_medium = """{
      "id": "m4",
      "type": "text",
      "mime": "text/plain",
      "location": "/var/archive/video-0012-transcript.txt"
    }"""