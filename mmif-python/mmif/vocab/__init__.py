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

    def canonical(self):
        if self.namespace.upper() == 'MMIF':
            return self.shortname
        elif self.namespace.upper() in URI:
            return f'{self.namespace.upper()}:{self.shortname}'
        else:
            return self.uri


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


def get(value: str, *, is_uri=False) -> AnnotationType:
    if is_uri or uri_validator(value):
        uri = value
    else:
        uri = None

    if uri is not None:
        shortname = None
        try:
            prefix, shortname = uri.rsplit('/', 1)
            if prefix[-2:] == ':/':  # so sad
                raise ValueError
            namespace = URI(prefix).name
        except ValueError:  # either couldn't split on '/' or namespace not in URI enum
            return AnnotationType(namespace='custom',
                                  shortname=shortname if shortname else uri,
                                  uri=uri)
    else:
        assert value is not None  # for PyCharm, with love
        try:
            namespace, shortname = value.split(':')
        except ValueError:
            namespace, shortname = 'MMIF', value
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
    print(get('Annotation'))
    print(get('https://mmif.clams.ai/0.1.0/vocabulary/Annotation'))
    print(get('https://a.com/Steve'))
    print(get('mmif:BoundingBox'))
    print(get("bad uri but we'll take it anyway", is_uri=True))
