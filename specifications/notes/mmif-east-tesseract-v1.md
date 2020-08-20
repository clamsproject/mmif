# MMIF Example — EAST and Tesseract

This example contains:

- one image medium
- one view created by EAST
- one view created by Tesseract

Notice how the view created by Tesseract contains a text document.

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
    
    {
      "id": "v2",
      "@context": "http://mmif.clams.ai/0.1.0/context/vocab-clams.json",
      "metadata": {
        "contains": {
          "http://mmif.clams.ai/0.1.0/TextDocument": {} },
        "tool": "http://mmif.clams.ai/apps/tessearct/0.2.1"
      },
      "annotations": [
        { 
          "@type": "http://mmif.clams.ai/0.1.0/TextDocument",
          "properties": {
            "id": "td1",
            "text": {
              "@value": "Fido barks",
              "textSource": "v1:bb1" } }
        }
      ]
    }

  ]
}
```

