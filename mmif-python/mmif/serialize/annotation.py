"""
The :mod:`annotation` module contains the classes used to represent a
MMIF annotation as a live Python object.

In MMIF, annotations are created by apps in a pipeline as a part
of a view. For documentation on how views are represented, see
:mod:`mmif.serialize.view`.
"""

from typing import Union
from pyrsistent import pmap, pvector
from .model import FreezableMmifObject
from mmif.vocabulary import ThingTypesBase, DocumentTypesBase

__all__ = ['Annotation', 'AnnotationProperties', 'Document', 'DocumentProperties', 'Text']


class Annotation(FreezableMmifObject):
    """
    MmifObject that represents an annotation in a MMIF view.
    """

    def __init__(self, anno_obj: Union[bytes, str, dict] = None) -> None:
        self._type: Union[str, ThingTypesBase] = ''
        if 'properties' not in self.__dict__:  # don't overwrite DocumentProperties on super() call
            self.properties: AnnotationProperties = AnnotationProperties()
        self.disallow_additional_properties()
        if 'properties' not in self._attribute_classes:
            self._attribute_classes = pmap({'properties': AnnotationProperties})
        self._required_attributes = pvector(["_type", "properties"])
        super().__init__(anno_obj)

    def is_type(self, type: Union[str, ThingTypesBase]) -> bool:
        """
        Check if the @type of this object matches.
        """
        return str(self.at_type) == str(type)

    @property
    def at_type(self) -> Union[str, ThingTypesBase]:
        # TODO (krim @ 8/19/20): should we always return string? leaving this to return
        #  different types can be confusing for sdk users.
        return self._type

    @at_type.setter
    def at_type(self, at_type: Union[str, ThingTypesBase]) -> None:
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

    def is_document(self):
        return self.at_type.endswith("Document")


class Document(Annotation):
    """
    Document object that represents a single document in a MMIF file.

    A document is identified by an ID, and contains certain attributes
    and potentially contains the contents of the document itself,
    metadata about how the document was created, and/or a list of
    subdocuments grouped together logically.

    If ``document_obj`` is not provided, an empty Document will be generated.

    :param document_obj: the JSON data that defines the document
    """
    def __init__(self, doc_obj: Union[bytes, str, dict] = None) -> None:
        self._parent_view_id = ''
        self._type: Union[str, DocumentTypesBase] = ''
        self.properties: DocumentProperties = DocumentProperties()
        self.disallow_additional_properties()
        self._attribute_classes = pmap({'properties': DocumentProperties})
        super().__init__(doc_obj)

    @property
    def parent(self) -> str:
        return self._parent_view_id

    @parent.setter
    def parent(self, parent_view_id: str) -> None:
        # I want to make this to accept `View` object as an input too,
        # but import `View` will break the code due to circular imports
        self._parent_view_id = parent_view_id

    @property
    def location(self) -> str:
        return self.properties.location

    @location.setter
    def location(self, location: str) -> None:
        self.properties.location = location


class AnnotationProperties(FreezableMmifObject):
    """
    AnnotationProperties object that represents the
    ``properties`` object within a MMIF annotation.

    :param mmif_obj: the JSON data that defines the properties
    """

    def __init__(self, mmif_obj: Union[bytes, str, dict] = None) -> None:
        self.id: str = ''
        self._required_attributes = pvector(["id"])
        super().__init__(mmif_obj)


class DocumentProperties(AnnotationProperties):
    """
    DocumentProperties object that represents the
    ``properties`` object within a MMIF document.

    :param mmif_obj: the JSON data that defines the properties
    """

    def __init__(self, mmif_obj: Union[bytes, str, dict] = None) -> None:
        self.mime: str = ''
        self.location: str = ''
        self.text: Text = Text()
        self._attribute_classes = pmap({'text': Text})
        super().__init__(mmif_obj)

    @property
    def text_language(self) -> str:
        return self.text.lang

    @text_language.setter
    def text_language(self, lang_code: str) -> None:
        self.text.lang = lang_code

    @property
    def text_value(self) -> str:
        return self.text.value

    @text_value.setter
    def text_value(self, s: str) -> None:
        self.text.value = s


class Text(FreezableMmifObject):

    def __init__(self, text_obj: Union[bytes, str, dict] = None) -> None:
        self._value: str = ''
        self._language: str = ''
        self.disallow_additional_properties()
        self._required_attributes = pvector(["_value"])
        super().__init__(text_obj)

    @property
    def lang(self) -> str:
        return self._language

    @lang.setter
    def lang(self, lang_code: str) -> None:
        # TODO (krim @ 8/11/20): add validation for language code (ISO 639)
        self._language = lang_code

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, s: str) -> None:
        self._value = s

