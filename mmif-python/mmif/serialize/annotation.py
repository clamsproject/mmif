from typing import Union

from .model import MmifObject
from mmif.vocabulary import AnnotationTypesBase

__all__ = ['Annotation', 'AnnotationProperties']


class Annotation(MmifObject):
    properties: 'AnnotationProperties'
    _type: Union[str, AnnotationTypesBase]

    def __init__(self, anno_obj: Union[str, dict] = None):
        self._type = ''
        self.properties = AnnotationProperties()
        self.disallow_additional_properties()
        self._attribute_classes = {'properties': AnnotationProperties}
        super().__init__(anno_obj)

    @property
    def at_type(self):
        return self._type

    @at_type.setter
    def at_type(self, at_type: Union[str, AnnotationTypesBase]):
        self._type = at_type

    @property
    def id(self) -> str:
        return self.properties.id

    @id.setter
    def id(self, aid: str) -> None:
        self.properties.id = aid

    def add_property(self, name: str, value: str) -> None:
        self.properties[name] = value


class AnnotationProperties(MmifObject):
    id: str

    def __init__(self, mmif_obj: Union[str, dict] = None):
        self.id = ''
        super().__init__(mmif_obj)
