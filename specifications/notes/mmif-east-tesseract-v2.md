# MMIF Example — EAST and Tesseract

This example contains 

- one image medium that was in the MMIF before any processing
- one view created by EAST
- one text medium created by Tesseract.

Notice how the medium created by Tesseract has metadata similar to what views have, albeit without the contains section. We may consider making media lists even more like views with a *contains* dictionary (which allows specification of *TextDocument* metadata if there are any) and a list of documents.

```json
{
	"@context": "http://mmif.clams.ai/0.1.0/context/miff.json",

  "metadata": {
    "mmif": "http://miff.clams.ai/0.1.0" },

  "media": [
    {
      "@type": "http://mmif.clams.ai/0.1.0/ImageDocument",
      "properties": {
        "id": "m1",
        "mime": "image/jpg",
        "location": "/var/archive/image-0012.jpg" }
    },
    { 
      "@type": "http://mmif.clams.ai/0.1.0/TextDocument",
      "metadata": {
        "tool": "http://mmif.clams.ai/apps/tessearct/0.2.1",
        "textSource": "v1:bb1"
      },
      "properties": {
        "id": "m1",
        "text": {
          "@value": "Fido barks" } }
    }
  ],

  "views": [

    {
      "id": "v1",
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",
      "metadata": {
        "contains": {
          "http://mmif.clams.ai/0.1.0/BoundingBox": {} },
        "tool": "http://mmif.clams.ai/apps/east/0.2.1",
        "medium": "m1"
      },
      "annotations": [
        { 
          "@type": "http://mmif.clams.ai/0.1.0/BoundingBox",
          "properties": {
            "id": "bb1",
            "coordinates": [[10,20], [40,20], [10,30], [40,30]],
            "boxType": "text" }
        }
      ]
    },

  ]
}
```

