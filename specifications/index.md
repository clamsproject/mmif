---
layout: page
title: MMIF Specification
subtitle: Version $VERSION
---

## 1. Overview

The Multi-Media Interchange Format (MMIF) is a JSON-LD serialization format for representing multimedia documents and annotations. MMIF transports data between CLAMS applications and is based on the LAPPS Interchange Format (LIF).

**Formal Components:**
- JSON Schema: [https://mmif.clams.ai/$VERSION/schema/mmif.json](schema/mmif.json)
- CLAMS Vocabulary: [https://mmif.clams.ai/$VERSION/vocabulary](vocabulary)
- LAPPS Vocabulary: [http://vocab.lappsgrid.org](http://vocab.lappsgrid.org)

**Versioning:** MMIF uses [semantic versioning](https://semver.org/) (`major.minor.patch`). See [versioning notes](../versioning) for compatibility requirements.

**Notation:** This specification uses RFC 2119 keywords: MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL.

## Table of Contents
{:.no_toc}

1. toc placeholder
{:toc}

## 2. Format Requirements

- **Encoding:** MMIF documents MUST be serialized as UTF-8 encoded Unicode text.
- **MIME Type:** `application/json` or `application/ld+json`
- **File Extension:** `.mmif` or `.json`

## 3. Root Object

A MMIF document is a JSON object with three required properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `metadata` | [MmifMetadata](#31-mmifmetadata) | Yes | Version and file-level metadata |
| `documents` | Array[[Document](#4-documents)] | Yes | Primary media objects (min: 1) |
| `views` | Array[[View](#5-views)] | Yes | Annotation views (min: 0) |

**Additional properties:** NOT allowed.

```json
{
  "metadata": { "mmif": "http://mmif.clams.ai/$VERSION" },
  "documents": [ ],
  "views": [ ]
}
```

### 3.1 MmifMetadata

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `mmif` | URI string | Yes | MMIF version URI |
| *(custom)* | any | No | User-defined metadata |

The `mmif` property MUST contain a URI identifying the MMIF specification version.

## 4. Documents

The `documents` array contains primary media objects. This array:
- MUST contain at least one document
- MUST NOT be modified after MMIF initialization
- MAY contain any number of documents of any supported types

### 4.1 Document Object

Each document is an [Annotation](#6-annotations) object with document-specific type constraints.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | URI string | Yes | Document type from vocabulary |
| `properties` | Object | Yes | Document properties (see below) |

### 4.2 Document Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique document identifier |
| `mime` | MIME type | No | Media type (required for external files) |
| `location` | URI string | Conditional | File location (external documents) |
| `text` | [TextValue](#43-inline-text) | Conditional | Inline text content (TextDocument only) |

**Constraints:**
- External documents MUST specify `location` with `file://` or `http(s)://` URI
- Inline text documents MUST use `text` property instead of `location`
- The `id` property MUST be unique across all documents in the MMIF

### 4.3 Inline Text

Inline text uses a JSON-LD value object:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@value` | string | Yes | Text content |
| `@language` | BCP47 code | No | Language identifier |

**Additional properties:** NOT allowed.

### 4.4 Document Types

Supported document types (from CLAMS vocabulary):

| Type | URI | Description |
|------|-----|-------------|
| VideoDocument | `http://mmif.clams.ai/vocabulary/VideoDocument/*` | Video media |
| AudioDocument | `http://mmif.clams.ai/vocabulary/AudioDocument/*` | Audio media |
| ImageDocument | `http://mmif.clams.ai/vocabulary/ImageDocument/*` | Image media |
| TextDocument | `http://mmif.clams.ai/vocabulary/TextDocument/*` | Text media |

**Example:**

```json
{
  "@type": "http://mmif.clams.ai/vocabulary/VideoDocument/$VideoDocument_VER",
  "properties": {
    "id": "m1",
    "mime": "video/mp4",
    "location": "file:///var/archive/video.mp4"
  }
}
```

## 5. Views

The `views` array contains annotation sets produced by CLAMS applications. Views:
- MUST be treated as read-only by applications
- MUST have unique identifiers
- MAY be ordered by `timestamp` property

### 5.1 View Object

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique view identifier |
| `metadata` | [ViewMetadata](#52-viewmetadata) | Yes | View metadata |
| `annotations` | Array[[Annotation](#6-annotations)] | Yes | Annotation objects (min: 0) |

**Additional properties:** NOT allowed.

### 5.2 ViewMetadata

View metadata describes the annotation set and its provenance.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `app` | URI string | Yes | Application identifier with version |
| `timestamp` | ISO 8601 | No | Creation timestamp |
| `contains` | Object | Conditional | Annotation type declarations |
| `error` | [ErrorObject](#53-error-object) | Conditional | Processing error |
| `warnings` | Array[string] | Conditional | Warning messages (min: 1) |
| `parameters` | Object | No | Runtime parameters (string values) |
| `appConfiguration` | Object | No | Refined parameters (typed values) |

**Constraints (oneOf):**
- Success views MUST have `app` + `contains`
- Error views MUST have `app` + `error`
- Warning views MUST have `app` + `warnings`

**Additional properties:** NOT allowed.

### 5.3 Contains Declaration

The `contains` object maps annotation type URIs to metadata objects:

```json
{
  "http://mmif.clams.ai/vocabulary/TimeFrame/$TimeFrame_VER": {
    "document": "m1",
    "timeUnit": "milliseconds"
  }
}
```

**Property keys:**
- MUST be HTTP(S) URIs matching pattern `^https?://`
- MUST correspond to annotation types in the view

**Property values:**
- MAY specify type-specific metadata (see vocabulary definitions)
- Common metadata properties: `document`, `timeUnit`

### 5.4 Error Object

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `message` | string | Yes | Error message |
| `stackTrace` | string | No | Stack trace information |

Error views MUST have empty `annotations` array.

### 5.5 Parameters vs AppConfiguration

- `parameters`: Raw runtime parameters as strings (for reproducibility)
- `appConfiguration`: Type-converted parameters with defaults applied

## 6. Annotations

Annotations represent structured information about documents or other annotations.

### 6.1 Annotation Object

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | URI string | Yes | Annotation type from vocabulary |
| `properties` | Object | Yes | Annotation properties |

**Additional properties:** NOT allowed.

### 6.2 Annotation Properties

All annotations MUST have an `id` property:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique annotation identifier |

**Additional properties:** Defined by annotation type in vocabulary.

Common properties include:
- `document`: Source document identifier
- `start`, `end`: Offsets or timestamps
- `coordinates`: Spatial coordinates
- `label`, `category`: Classification labels
- `text`: Text content

### 6.3 Annotation Types

Annotation types are defined in the CLAMS and LAPPS vocabularies. The type hierarchy:

- **Thing** (abstract base, do not use directly)
  - **Annotation**: Base type with `document` property
    - **Region**: Spatial/temporal regions
      - **Span**: Text regions (`start`, `end` as character offsets)
      - **TimeFrame**: Temporal regions (`start`, `end` in time units)
      - **BoundingBox**: Image regions (`coordinates` as pixel arrays)
    - **Relation**: Binary relations (`source`, `target`)
      - **Alignment**: Cross-modal alignments

See [vocabulary documentation](vocabulary) for complete type definitions.

## 7. Identifier Conventions

### 7.1 Document Identifiers

- MUST be unique within the MMIF document
- SHOULD use simple alphanumeric format (e.g., `m1`, `doc-0012`)
- MUST NOT contain colons (`:`)

### 7.2 View Identifiers

- MUST be unique within the MMIF document
- SHOULD use simple alphanumeric format (e.g., `v1`, `view-ocr`)
- MUST NOT contain colons (`:`)

### 7.3 Annotation Identifiers

- MUST be unique within the containing view
- RECOMMENDED format: `{viewId}:{localId}` (e.g., `v1:bb1`)
- Colon (`:`) is RESERVED for delimiter between view and local identifier
- When referenced, MUST use full prefixed form

**Example:**
```json
{
  "id": "v2",
  "annotations": [
    {
      "@type": "http://mmif.clams.ai/vocabulary/Alignment/$Alignment_VER",
      "properties": {
        "id": "v2:a1",
        "source": "v1:bb1",
        "target": "v2:td1"
      }
    }
  ]
}
```

## 8. Measurement Units

### 8.1 Time Measurements

For types measuring time (TimeFrame, TimePoint, VideoObject):
- The `timeUnit` metadata property MUST be specified in `contains`
- Valid units: `milliseconds`, `seconds`, `frames`
- Default (if omitted): `milliseconds`

### 8.2 Spatial Measurements

For types measuring image regions (BoundingBox):
- Coordinates MUST be in pixels
- Origin (0,0) is the top-left corner
- Format: `[[x1,y1], [x2,y2], ...]`

### 8.3 Text Measurements

For types measuring text spans (Span, Token):
- Offsets MUST be Unicode code point counts
- Zero-indexed, end-exclusive intervals: `[start, end)`

## 9. Documents in Views

Applications MAY create document-type annotations within views (e.g., OCR generating TextDocument). These:
- Use the same structure as top-level documents
- MUST have prefixed identifiers (e.g., `v2:td1`)
- MAY be referenced by subsequent annotations via `document` property
- SHOULD be aligned to source data via Alignment annotations

**Example:**
```json
{
  "id": "v2",
  "metadata": {
    "app": "http://apps.clams.ai/tesseract/0.2.2",
    "contains": {
      "http://mmif.clams.ai/vocabulary/TextDocument/$TextDocument_VER": {},
      "http://mmif.clams.ai/vocabulary/Alignment/$Alignment_VER": {}
    }
  },
  "annotations": [
    {
      "@type": "http://mmif.clams.ai/vocabulary/TextDocument/$TextDocument_VER",
      "properties": {
        "id": "v2:td1",
        "text": { "@value": "yelp" }
      }
    },
    {
      "@type": "http://mmif.clams.ai/vocabulary/Alignment/$Alignment_VER",
      "properties": {
        "id": "v2:a1",
        "source": "v1:bb1",
        "target": "v2:td1"
      }
    }
  ]
}
```

## 10. Multiple Source Documents

When annotations in a view reference multiple documents:
- The `document` metadata property in `contains` MAY be omitted
- Each annotation MUST specify its `document` property individually

**Example:**
```json
{
  "metadata": {
    "contains": {
      "http://vocab.lappsgrid.org/SemanticTag": {}
    }
  },
  "annotations": [
    {
      "@type": "http://vocab.lappsgrid.org/SemanticTag",
      "properties": {
        "id": "v3:st1",
        "document": "v2:td1",
        "category": "dog-sound",
        "start": 0,
        "end": 4
      }
    },
    {
      "@type": "http://vocab.lappsgrid.org/SemanticTag",
      "properties": {
        "id": "v3:st2",
        "document": "v2:td2",
        "category": "dog-sound",
        "start": 0,
        "end": 4
      }
    }
  ]
}
```

## 11. Custom and External Types

### 11.1 Custom Types

The `@type` property MAY reference any IRI, not limited to CLAMS/LAPPS vocabularies. When using custom types:
- The IRI SHOULD resolve to documentation defining the type
- Properties MUST include `id`
- Other properties SHOULD be documented at the IRI location

**Example:**
```json
{
  "@type": "https://schema.org/Clip",
  "properties": {
    "id": "clip-29",
    "actor": "Geena Davis"
  }
}
```

### 11.2 LAPPS Vocabulary Types

MMIF annotations MAY use types from [http://vocab.lappsgrid.org](http://vocab.lappsgrid.org). These types follow the same conventions as CLAMS types.

## 12. Vocabulary Integration

Annotation types in vocabularies define two property sets:

1. **metadata**: Properties set in view's `contains` declaration (shared by all instances)
2. **properties**: Properties set on individual annotation objects

The vocabulary documentation specifies:
- Required vs. optional properties
- Value types and constraints
- Inheritance hierarchy
- Semantic definitions

Individual annotation properties MAY override metadata values for specific instances, but this is NOT RECOMMENDED without justification.

## 13. Complete Examples

### 13.1 Minimal MMIF

```json
{
  "metadata": {
    "mmif": "http://mmif.clams.ai/$VERSION"
  },
  "documents": [
    {
      "@type": "http://mmif.clams.ai/vocabulary/VideoDocument/$VideoDocument_VER",
      "properties": {
        "id": "m1",
        "mime": "video/mp4",
        "location": "file:///data/video.mp4"
      }
    }
  ],
  "views": []
}
```

### 13.2 Additional Examples

Complete workflow examples demonstrating multi-modal processing:

| Example | Description |
|---------|-------------|
| [bars-tones-slates](samples/bars-tones-slates) | Time frame segmentation with text processing |
| [east-tesseract-typing](samples/east-tesseract-typing) | Image text detection, OCR, and semantic typing |
| [segmenter-kaldi-ner](samples/segmenter-kaldi-ner) | Audio segmentation, ASR, and NER |
| [everything](samples/everything) | Comprehensive multi-modal pipeline |

## 14. Validation

MMIF documents:
- MUST conform to [schema/mmif.json](schema/mmif.json)
- MUST use types defined in referenced vocabularies
- SHOULD be validated against JSON Schema before processing
- SHOULD validate identifier uniqueness constraints

## 15. References

- **MMIF Python SDK:** [https://github.com/clamsproject/mmif-python](https://github.com/clamsproject/mmif-python)
- **JSON-LD 1.0:** [https://www.w3.org/TR/json-ld/](https://www.w3.org/TR/json-ld/)
- **JSON Schema Draft 04:** [http://json-schema.org/draft-04/schema](http://json-schema.org/draft-04/schema)
- **BCP47 Language Tags:** [https://tools.ietf.org/html/bcp47](https://tools.ietf.org/html/bcp47)
- **RFC 2119 Keywords:** [https://tools.ietf.org/html/rfc2119](https://tools.ietf.org/html/rfc2119)
