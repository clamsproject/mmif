from datetime import datetime
from typing import Dict, Union, Optional
import dateutil.parser

from .annotation import Annotation
from .model import MmifObject, DataList
from mmif.vocabulary import AnnotationTypesBase


__all__ = ['View', 'ViewMetadata', 'Contain']


class View(MmifObject):

    def __init__(self, view_obj: Union[str, dict] = None) -> None:
        self._context: str = ''
        self.id: str = ''
        self.metadata: ViewMetadata = ViewMetadata()
        self.annotations: AnnotationsList = AnnotationsList()
        self.disallow_additional_properties()
        self._attribute_classes = {
            'metadata': ViewMetadata,
            'annotations': AnnotationsList
        }
        super().__init__(view_obj)

    def new_contain(self, at_type: Union[str, AnnotationTypesBase], contain_dict: dict = None) -> Optional['Contain']:
        return self.metadata.new_contain(at_type, contain_dict)

    def new_annotation(self, aid: str, at_type: Union[str, AnnotationTypesBase], overwrite=False) -> 'Annotation':
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
        if key in self._named_attributes():
            return self.__dict__[key]
        anno_result = self.annotations.get(key)
        if not anno_result:
            raise KeyError("Annotation ID not found: %s" % key)
        return anno_result


class ViewMetadata(MmifObject):

    def __init__(self, viewmetadata_obj: Union[str, dict] = None) -> None:
        self.medium: str = ''
        self.timestamp: Optional[datetime] = None
        self.app: str = ''
        self.contains: Dict[str, Contain] = {}
        super().__init__(viewmetadata_obj)

    def _deserialize(self, input_dict: dict) -> None:
        try:
            self.contains = {at_type: Contain(contain_obj)
                             for at_type, contain_obj in input_dict.pop('contains').items()}
        except KeyError:
            # means input_dict don't have `contains`, so we'll leave it empty
            pass
        super()._deserialize(input_dict)

    def find_match_hotfix(self, key: str) -> bool:
        exists = False
        for existing_type in self.contains.keys():
            if key.split('/')[-1] == existing_type.split('/')[-1]:
                exists = True
                break
        return exists

    def new_contain(self, at_type: Union[str, AnnotationTypesBase], contain_dict: dict = None) -> Optional['Contain']:
        if isinstance(at_type, AnnotationTypesBase):
            exists = self.find_match_hotfix(at_type.name) or self.find_match_hotfix(at_type.value)
            final_key = at_type.value
        else:
            exists = self.find_match_hotfix(at_type)
            final_key = at_type

        if not exists:
            new_contain = Contain(contain_dict)
            new_contain.gen_time = datetime.now()
            self.contains[final_key] = new_contain
            return new_contain


class Contain(MmifObject):

    def __init__(self, contain_obj: Union[str, dict] = None) -> None:
        # TODO (krim @ 8/19/20): rename `producer` to `app` maybe?
        self.producer: str = ''
        self.gen_time: Optional[datetime] = None
        super().__init__(contain_obj)

    def _deserialize(self, input_dict: dict) -> None:
        super()._deserialize(input_dict)
        if 'gen_time' in self.__dict__ and isinstance(self.gen_time, str):
            self.gen_time = dateutil.parser.isoparse(self.gen_time)


class AnnotationsList(DataList[Annotation]):
    items: Dict[str, Annotation]

    def _deserialize(self, input_list: list) -> None:
        self.items = {item['properties']['id']: Annotation(item) for item in input_list}

    def append(self, value: Annotation, overwrite=False) -> None:
        super()._append_with_key(value.id, value, overwrite)
