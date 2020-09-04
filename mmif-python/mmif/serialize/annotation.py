"""
The :mod:`annotation` module contains the classes used to represent a
MMIF annotation as a live Python object.

In MMIF, annotations are created by apps in a pipeline as a part
of a view. For documentation on how views are represented, see
:mod:`mmif.serialize.view`.
"""

from typing import Union

from .model import MmifObject
from mmif.vocabulary import AnnotationTypesBase

__all__ = ['Annotation', 'AnnotationProperties']


class Annotation(MmifObject):
    """
    MmifObject that represents an annotation in a MMIF view.
    """

    def __init__(self, anno_obj: Union[str, dict] = None) -> None:
        self._type: Union[str, AnnotationTypesBase] = ''
        self.properties: AnnotationProperties = AnnotationProperties()
        self.disallow_additional_properties()
        self._attribute_classes = {'properties': AnnotationProperties}
        super().__init__(anno_obj)

    @property
    def at_type(self) -> Union[str, AnnotationTypesBase]:
        # TODO (krim @ 8/19/20): should we always return string? leaving this to return
        # different types can be confusing for sdk users.
        return self._type

    @at_type.setter
    def at_type(self, at_type: Union[str, AnnotationTypesBase]) -> None:
        self._type = at_type

    @property
    def id(self) -> str:
        return self.properties.id

    @id.setter
    def id(self, aid: str) -> None:
        self.properties.id = aid

    def add_property(self, name: str, value: str) -> None:
        """
        Adds a property to the annotation's properties.
        :param name: the name of the property
        :param value: the property's desired value
        :return: None
        """
        self.properties[name] = value


class AnnotationProperties(MmifObject):

    def __init__(self, mmif_obj: Union[str, dict] = None) -> None:
        self.id: str = ''
        super().__init__(mmif_obj)
