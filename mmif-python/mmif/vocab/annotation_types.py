# Spec version 0.1.0

from enum import Enum


class AnnotationTypes(Enum):
    """
    This enum contains the URIs for the MMIF annotation types defined in the spec version 0.1.0.
    Use this to quickly get the correct URIs for those types, or use the objects themselves in your
    code and they will serialize to the strings.
    """
    def _serialize(self):
        return self.value
    # Auto-generated code below this line
    Annotation = 'http://mmif.clams.ai/0.1.0/vocabulary/Annotation'
    Region = 'http://mmif.clams.ai/0.1.0/vocabulary/Region'
    TimePoint = 'http://mmif.clams.ai/0.1.0/vocabulary/TimePoint'
    Interval = 'http://mmif.clams.ai/0.1.0/vocabulary/Interval'
    Span = 'http://mmif.clams.ai/0.1.0/vocabulary/Span'
    TimeFrame = 'http://mmif.clams.ai/0.1.0/vocabulary/TimeFrame'
    Chapter = 'http://mmif.clams.ai/0.1.0/vocabulary/Chapter'
    Polygon = 'http://mmif.clams.ai/0.1.0/vocabulary/Polygon'
    BoundingBox = 'http://mmif.clams.ai/0.1.0/vocabulary/BoundingBox'
    VideoObject = 'http://mmif.clams.ai/0.1.0/vocabulary/VideoObject'
    Relation = 'http://mmif.clams.ai/0.1.0/vocabulary/Relation'
    Alignment = 'http://mmif.clams.ai/0.1.0/vocabulary/Alignment'
