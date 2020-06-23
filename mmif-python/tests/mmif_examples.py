example1 = """{
  "@context": "http://mmif.clams.ai/0.1.0/context/miff.json",
  "metadata": { },
  "contains": "???",
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
        "tool": "http://tools.clams.io/tesseract/1.2.1"
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
        "tool": "http://tools.clams.io/east/1.0.4"
      },
      "annotations": [
        {
          "@type": "BoundingBox",
          "id": "bb1",
          "properties": {
            "coordinates": [[90,40], [110,40], [90,50], [110,50]] }
        }
      ]
    }
  ]
}"""
