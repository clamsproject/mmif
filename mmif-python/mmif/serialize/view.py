from datetime import datetime
from typing import Dict, List, Union, Optional

from .annotation import Annotation
from .model import MmifObject, DataList
from mmif.vocab import AnnotationTypes


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
        _context = view_dict.get('_context')
        if _context is not None:
            self._context = _context
        self.id = view_dict['id']
        self.metadata = ViewMetadata(view_dict['metadata'])
        self.annotations = AnnotationsList(view_dict['annotations'])

    def new_contain(self, at_type: Union[str, AnnotationTypes], contain_dict: dict = None) -> Optional['Contain']:
        return self.metadata.new_contain(at_type, contain_dict)

    def new_annotation(self, aid: str, at_type: Union[str, AnnotationTypes], overwrite=False) -> 'Annotation':
        new_annotation = Annotation()
        new_annotation.at_type = at_type
        new_annotation.id = aid
        return self.add_annotation(new_annotation, overwrite)

    def add_annotation(self, annotation: 'Annotation', overwrite=False) -> 'Annotation':
        self.annotations.append(annotation, overwrite)
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
    app: str
    contains: Dict[str, 'Contain']

    def __init__(self, viewmetadata_obj: Union[str, dict] = None):
        # need to set instance variables for ``_named_attributes()`` to work
        self.medium = ''
        self.timestamp = datetime.now()
        self.app = ''
        self.contains = {}
        super().__init__(viewmetadata_obj)

    def _deserialize(self, input_dict: dict) -> None:
        # TODO (angus-lherrou @ 8/4/2020): using __dict__ with potentially non-identifier
        #  keys "works" but is not pythonic so better to wrap a dict property.
        #  Unify implementations of this and MediumMetadata
        # super()._deserialize(input_dict)
        self.__dict__ = input_dict
        self.contains = {at_type: Contain(contain_obj) for at_type, contain_obj in input_dict.get('contains', {}).items()}

    def new_contain(self, at_type: Union[str, AnnotationTypes], contain_dict: dict = None) -> Optional['Contain']:
        def find_match_hotfix(key: str) -> bool:
            absent = True
            for existing_type in self.contains.keys():
                if key.split('/')[-1] == existing_type.split('/')[-1]:
                    absent = False
            return absent

        if isinstance(at_type, AnnotationTypes):
            exists = find_match_hotfix(at_type.name) or find_match_hotfix(at_type.value)
            final_key = at_type.value
        else:
            exists = find_match_hotfix(at_type)
            final_key = at_type

        if not exists:
            new_contain = Contain(contain_dict)
            self.contains[final_key] = new_contain
            return new_contain


class Contain(MmifObject):
    producer: str
    gen_time: datetime

    def __init__(self, contain_obj: Union[str, dict] = None):
        self.producer = ''
        self.gen_time = datetime.now()     # datetime.datetime
        super().__init__(contain_obj)

    def _deserialize(self, input_dict: dict) -> None:
        super()._deserialize(input_dict)
        if 'gen_time' in self.__dict__ and isinstance(self.gen_time, str):
            self.gen_time = datetime.fromisoformat(self.gen_time)

class AnnotationsList(DataList[Annotation]):
    items: Dict[str, Annotation]

    def _deserialize(self, input_list: list) -> None:
        self.items = {item['properties']['id']: Annotation(item) for item in input_list}

    def append(self, value: Annotation, overwrite=False):
        super()._append_with_key(value.id, value, overwrite)
