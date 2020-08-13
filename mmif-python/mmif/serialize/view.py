from datetime import datetime
from typing import Dict, List, Union, Optional

from .annotation import Annotation
from .model import MmifObject, DataList


__all__ = ['View', 'ViewMetadata', 'Contain']


class View(MmifObject):
    id: str
    metadata: 'ViewMetadata'
    annotations: 'AnnotationsList'

    def __init__(self, view_obj: Union[str, dict] = None):
        self.id = ''
        self.metadata = ViewMetadata()
        self.annotations = AnnotationsList()
        super().__init__(view_obj)

    def _deserialize(self, view_dict: dict) -> None:
        self.id = view_dict['id']
        self.metadata = ViewMetadata(view_dict['metadata'])
        self.annotations = AnnotationsList(view_dict['annotations'])

    def new_contain(self, at_type: str, contain_dict: dict = None) -> Optional['Contain']:
        return self.metadata.new_contain(at_type, contain_dict)

    def new_annotation(self, aid: str, at_type: str) -> 'Annotation':
        new_annotation = Annotation()
        new_annotation.at_type = at_type
        new_annotation.id = aid
        return self.add_annotation(new_annotation)

    def add_annotation(self, annotation: 'Annotation') -> 'Annotation':
        self.annotations[annotation.id] = annotation
        self.new_contain(annotation.at_type)
        return annotation

    def __getitem__(self, key: str) -> 'Annotation':
        """
        getitem implementation for View.

        >>> obj = View('''{"id": "v1","metadata": {"contains": {"BoundingBox": {"unit": "pixels"}},"medium": "m1","tool": "http://tools.clams.io/east/1.0.4"},"annotations": [{"@type": "BoundingBox","properties": {"id": "bb1","coordinates": [[90,40], [110,40], [90,50], [110,50]] }}]}''')
        >>> type(obj['bb1'])
        <class 'mmif.serialize.annotation.Annotation'>
        >>> obj['asdf']
        Traceback (most recent call last):
            ...
        KeyError: 'Annotation ID not found: asdf'

        :raises KeyError: if the key is not found or if the search results are ambiguous
        :param key: the search string.
        :return: the object searched for
        """
        anno_result = self.annotations.get(key)
        if not anno_result:
            raise KeyError("Annotation ID not found: %s" % key)
        return anno_result


class ViewMetadata(MmifObject):
    medium: str
    timestamp: Optional[datetime] = None
    tool: str
    contains: Dict[str, 'Contain']

    def __init__(self, viewmetadata_obj: Union[str, dict] = None):
        self.medium = ''
        self.timestamp = datetime.now()
        self.tool = ''
        self.contains = {}
        super().__init__(viewmetadata_obj)

    def _deserialize(self, input_dict: dict) -> None:
        # TODO (angus-lherrou @ 8/4/2020): using __dict__ with potentially non-identifier
        #  keys "works" but is not pythonic so better to wrap a dict property.
        #  Unify implementations of this and MediumMetadata
        self.__dict__ = input_dict
        self.contains = {at_type: Contain(contain_obj) for at_type, contain_obj in input_dict.get('contains', {}).items()}

    def new_contain(self, at_type: str, contain_dict: dict = None) -> Optional['Contain']:
        if at_type not in self.contains:
            new_contain = Contain(contain_dict)
            self.contains[at_type] = new_contain
            return new_contain


class Contain(MmifObject):
    producer: str
    gen_time: datetime

    def __init__(self, contain_obj: Union[str, dict] = None):
        self.producer = ''
        self.gen_time = datetime.now()     # datetime.datetime
        super().__init__(contain_obj)


class AnnotationsList(DataList[Annotation]):
    items: Dict[str, Annotation]

    def _deserialize(self, input_list: list) -> None:
        self.items = {item['properties']['id']: Annotation(item) for item in input_list}

    def append(self, value: Annotation):
        super()._append_with_key(value.id, value)
