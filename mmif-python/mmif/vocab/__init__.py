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


class VocabularyItem(Enum):
    pass


class MmifVocabularyItem(VocabularyItem):
    def __new__(cls, atype: AnnotationType):
        obj = object.__new__(cls)
        obj._value_ = atype.uri
        obj.atype = atype
        return obj

    def _generate_next_value_(name, start, count, last_values):
        return AnnotationType(namespace='MMIF',
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


class NamespaceType(Enum):
    MMIF = MmifVocabularyItem


def get(*, uri: str = None, name: str = None) -> AnnotationType:
    if not ((uri is None) ^ (name is None)):
        raise ValueError("Either pass a URI or a namespace")
    if uri is not None:
        shortname = None
        try:
            prefix, shortname = uri.rsplit('/')
            if prefix[-2:] == ':/':  # so sad
                raise ValueError
            namespace = URI(prefix).name
        except ValueError:  # either couldn't split on '/' or namespace not in URI enum
            return AnnotationType(namespace='custom',
                                  shortname=shortname if shortname else uri,
                                  uri=uri)
    else:
        assert name is not None  # for PyCharm, with love
        try:
            namespace, shortname = name.split(':')
        except ValueError:
            namespace, shortname = 'MMIF', name
        try:
            uri = f'{URI[namespace.upper()].value}/{shortname}'
        except KeyError:
            raise VocabularyException(f"Namespace '{namespace}' not found. "
                                      f"If you are using a custom vocabulary, please use full URIs.")
    try:
        enum_class = NamespaceType[namespace.upper()].value
        return enum_class(uri).atype
    except KeyError:
        return AnnotationType(namespace='custom',
                              shortname=shortname if shortname else uri,
                              uri=uri)


if __name__ == '__main__':
    x = MmifVocabularyItem.Span
    y = MmifVocabularyItem('https://mmif.clams.ai/0.1.0/vocabulary/Annotation')
    print(get(name='Annotation'))
    print(get(uri='https://mmif.clams.ai/0.1.0/vocabulary/Annotation'))
    print(get(uri='https://a.com'))
    print(get(name='mmif:BoundingBox'))
