from mmif import __specver__
from string import Template

example_templates = dict(
    mmif_example1="""{
  "@context": "http://mmif.clams.ai/${specver}/context/mmif.json",
  "metadata": {
    "mmif": "http://mmif.clams.ai/${specver}"
  },
  "documents": [
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
        "document": "m1",
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
    mmif_example2="""{
  "@context": "http://mmif.clams.ai/${specver}/context/mmif.json",

  "metadata": {
    "mmif": "http://mmif.clams.ai/${specver}",
    "contains": {
      "http://mmif.clams.ai/1.0/vocabulary/Segment": ["v1"],
      "http://vocab.lappsgrid.org/NamedEntity": ["v2"]
    }
  },

  "documents": [
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
      "@context": "http://mmif.clams.ai/${specver}/context/vocab-clams.json",
      "id": "v1",
      "metadata": {
        "document": "m1",
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
      "@context": "http://mmif.clams.ai/${specver}/context/vocab-lapps.json",
      "id": "v2",
      "metadata": {
        "document": "m2",
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
    mmif_example3="""{
  "@context": "http://mmif.clams.ai/${specver}/context/mmif.json",

  "metadata": {
    "mmif": "http://mmif.clams.ai/${specver}",
    "contains": {
      "http://mmif.clams.ai/${specver}/vocabulary/Segment": ["v1"],
      "http://mmif.clams.ai/${specver}/vocabulary/TimePoint": ["v1"],
      "http://vocab.lappsgrid.org/NamedEntity": ["v2"]
    }
  },

  "documents": [
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
      "@context": "http://mmif.clams.ai/${specver}/context/vocab-clams.json",
      "id": "v1",
      "metadata": {
        "document": "m1",
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
      "@context": "http://mmif.clams.ai/${specver}/context/vocab-lapps.json",
      "id": "v2",
      "metadata": {
        "document": "m2",
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
    mmif_example4="""{
  "@context": "http://mmif.clams.ai/${specver}/context/mmif.json",

  "metadata": {
    "mmif": "http://mmif.clams.ai/${specver}",
    "contains": {
      "http://mmif.clams.ai/vocabulary/${specver}/TimeFrame": ["v1", "v2"],
      "http://vocab.lappsgrid.org/Token": ["v3"]
    }
  },

  "documents": [
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
      "@context": "http://mmif.clams.ai/${specver}/context/vocab-clams.json",

      "metadata": {
        "contains": {
          "http://mmif.clams.ai/${specver}/vocabulary/TimeFrame": {
            "unit": "seconds"
          }
        },
        "document": "m1",
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
      "@context": "http://mmif.clams.ai/${specver}/context/vocab-clams.json",

      "metadata": {
        "contains": {
          "http://mmif.clams.ai/${specver}/vocabulary/TimeFrame": {
            "unit": "seconds"
          }
        },
        "document": "m1",
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
      "@context": "http://mmif.clams.ai/${specver}/context/vocab-lapps.json",

      "metadata": {
        "contains": {
          "http://vocab.lappsgrid.org/Token": {}
        },
        "document": "m2",
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
""",
    annotation_example1 = """{
          "@type": "Token",
          "properties": {
            "id": "token1",
            "start": 0,
            "end": 3,
            "word": "The"
          }
        }""",
    annotation_example2 = """{
  "@type": "TimePoint",
  "properties": {
    "id": "t1",
    "point": 5
  }
}""",
    view_example1 = """{
      "@context": "http://mmif.clams.ai/${specver}/context/vocab-clams.json",
      "id": "v1",
      "metadata": {
        "document": "m1",
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
    }""",
    document_ext_video_example = """{
      "id": "m3",
      "type": "video",
      "mime": "video/mp4",
      "location": "/var/archive/video-0012.mp4"
    }""",
    document_text_document_example = """{
      "id": "m4",
      "type": "text",
      "mime": "text/plain",
      "location": "/var/archive/video-0012-transcript.txt"
    }""",
    mmif_example1_modified = """{
  "@context": "http://mmif.clams.ai/${specver}/context/mmif.json",
  "metadata": {
    "mmif": "http://mmif.clams.ai/${specver}"
  },
  "documents": [
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
          "BoundingBox": {"unit": "pixels"},
          "http://mmif.clams.ai/${specver}/vocabulary/Polygon": {"gen_time": "2020-05-27T12:23:45"}
        },
        "document": "m1",
        "app": "http://apps.clams.io/east/1.0.4"
      },
      "annotations": [
        {
          "@type": "BoundingBox",
          "properties": {
            "id": "bb1",
            "coordinates": [[90,40], [110,40], [90,50], [110,50]] 
          }
        },
        {
          "@type": "http://mmif.clams.ai/${specver}/vocabulary/Polygon",
          "properties": {
            "id": "p1",
            "coordinates": [[20, 30], [20, 40], [60, 30]]
          }
        }
      ]
    }
  ]
}""")

examples = dict((k, Template(v).substitute(specver=__specver__)) for k, v in example_templates.items())
