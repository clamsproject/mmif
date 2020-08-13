from typing import Union, Optional

from .model import MmifObject

__all__ = ['Annotation', 'AnnotationProperties']


class Annotation(MmifObject):
    properties: 'AnnotationProperties'
    _type: str

    def __init__(self, anno_obj: Union[str, dict] = None):
        self._type = ''
        self.properties = AnnotationProperties()
        super().__init__(anno_obj)

    @property
    def at_type(self):
        return self._type

    @at_type.setter
    def at_type(self, at_type: str):
        self._type = at_type

    @property
    def id(self) -> str:
        return self.properties.id

    @id.setter
    def id(self, aid: str) -> None:
        self.properties.id = aid

    def _deserialize(self, input_dict: dict) -> None:
        self._type = input_dict['_type']
        self.properties = AnnotationProperties(input_dict['properties'])
        
    def _serialize(self) -> dict:
        intermediate = super()._serialize()
        intermediate.update(properties=self.properties._serialize())
        return intermediate

    def add_property(self, name: str, value: str) -> None:
        self.properties[name] = value


class AnnotationProperties(MmifObject):
    properties: dict

    def __init__(self, mmif_obj: Union[str, dict] = None):
        self.properties = {}
        super().__init__(mmif_obj)

    @property
    def id(self):
        return self.properties['id']

    @id.setter
    def id(self, aid):
        self.properties['id'] = aid

    def _deserialize(self, input_dict: dict) -> None:
        self.properties = input_dict

    def _serialize(self):
        return MmifObject(self.properties)._serialize()

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __getitem__(self, key):
        return self.properties[key]
