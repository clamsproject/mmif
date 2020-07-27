from typing import Dict, Union, Optional

from .model import MmifObject


class Annotation(MmifObject):
    """
    MmifObject that represents an annotation in a MMIF view.
    """

    properties: 'AnnotationProperties'
    _type: str

    @property
    def id(self):
        return self.properties.id

    @id.setter
    def id(self, aid):
        self.properties.id = aid

    def _deserialize(self, input_dict: dict) -> None:
        """
        Maps a plain python dict object to an Annotation object.

        Represents the "properties" sub-dictionary with an
        AnnotationProperties object.

        :param input_dict: an annotation dict from a MMIF file
        :return: None
        """
        self._type = input_dict['_type']
        self.properties = AnnotationProperties(input_dict['properties'])

    def __init__(self, anno_obj: Union[str, dict] = None):
        """
        Constructs a MMIF Annotation object.
        :param anno_obj: the JSON-LD data
        """
        self._type = ''
        self.properties = AnnotationProperties()
        super().__init__(anno_obj)

    def add_property(self, name: str, value: str) -> None:
        """
        Adds a property to the annotation's properties.
        :param name: the name of the property
        :param value: the property's desired value
        :return: None
        """
        self.properties[name] = value


class AnnotationProperties(MmifObject):
    id: str
    start: Optional[int] = -1
    end: Optional[int] = -1
