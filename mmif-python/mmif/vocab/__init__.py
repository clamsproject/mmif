from enum import Enum, auto
from urllib.parse import urlparse
import attr
from mmif.ver import __version__


def uri_validator(uri: str):
    try:
        result = urlparse(uri)
        return all([result.scheme, result.netloc, result.path])
    except RecursionError:
        raise
    except:
        return False


class VocabularyException(Exception):
    pass


@attr.s
class AnnotationType:
    namespace = attr.ib()
    shortname = attr.ib()
    uri = attr.ib()


class URI(Enum):
    MMIF = f"https://mmif.clams.ai/{__version__}/vocabulary"


class MmifVocabulary(Enum):
    def __new__(cls, atype: AnnotationType):
        obj = object.__new__(cls)
        obj._value_ = atype.uri
        obj.__dict__.update(atype.__dict__)
        return obj

    @classmethod
    def _missing_(cls, value):
        if not uri_validator(value):
            try:
                namespace, shortname = value.split(':')
            except ValueError:
                namespace, shortname = 'MMIF', value
            try:
                value = f'{URI[namespace.upper()].value}/{shortname}'
            except KeyError:
                raise VocabularyException(f"Namespace '{namespace}' not found. "
                                          f"If you are using a custom vocabulary, please use full URIs.")
        elif value not in MmifVocabulary:
            raise Exception("This shouldn't ever get raised by client code")
        return MmifVocabulary(value)

    def _generate_next_value_(name, start, count, last_values):
        return AnnotationType(namespace='mmif',
                              shortname=name,
                              uri=f'{URI.MMIF.value}/{name}')
    Annotation = auto()
    Region = auto()
    TimePoint = auto()
    Interval = auto()
    Span = auto()
    TimeFrame = auto()
    Chapter = auto()
    Polygon = auto()
    BoundingBox = auto()
    VideoObject = auto()
    Relation = auto()
    Alignment = auto()


if __name__ == '__main__':
    x = MmifVocabulary.Span
    y = MmifVocabulary('https://mmif.clams.ai/0.1.0/vocabulary/Annotation')
    z = MmifVocabulary('Annotation')
    z2 = MmifVocabulary('mmif:Annotation')
    z3 = MmifVocabulary('lapps:Segment')
