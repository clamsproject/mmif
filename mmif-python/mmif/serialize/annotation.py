from typing import Dict, Union, Optional

from .model import MmifObject


__all__ = ['Annotation', 'AnnotationProperties']


class Annotation(MmifObject):
    properties: 'AnnotationProperties'
    _type: str

    @property
    def id(self):
        return self.properties.id

    @id.setter
    def id(self, aid):
        self.properties.id = aid

    def _deserialize(self, input_dict: dict) -> None:
        self._type = input_dict['_type']
        self.properties = AnnotationProperties(input_dict['properties'])

    def __init__(self, anno_obj: Union[str, dict] = None):
        self._type = ''
        self.properties = AnnotationProperties()
        super().__init__(anno_obj)

    def add_property(self, name: str, value: str):
        self.properties[name] = value


class AnnotationProperties(MmifObject):
    id: str
    start: Optional[int] = -1
    end: Optional[int] = -1
    properties: dict

    def _deserialize(self, input_dict: dict) -> None:
        self.properties = input_dict
        self.id = input_dict['id']

    def _serialize(self):
        return MmifObject(self.properties)._serialize()

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __getitem__(self, key):
        return self.properties[key]
