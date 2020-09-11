"""
The :mod:`document` module contains the classes used to represent a
MMIF document as a live Python object.

In MMIF, documents are objects that either point to a file containing
the document being described, or contain the document directly in some
text document cases.
"""

from typing import Union, Optional, Dict
from pyrsistent import pmap

from .model import FreezableMmifObject, FreezableDataList


__all__ = ['Document', 'DocumentMetadata', 'Subdocument', 'Text']


class Document(FreezableMmifObject):
    """
    Document object that represents a single document in a MMIF file.

    A document is identified by an ID, and contains certain attributes
    and potentially contains the contents of the document itself,
    metadata about how the document was created, and/or a list of
    subdocuments grouped together logically.

    If ``document_obj`` is not provided, an empty Document will be generated.

    :param document_obj: the JSON data that defines the document
    """

    def __init__(self, document_obj: Union[str, dict] = None) -> None:
        self.id: str = ''
        self.type: str = ''
        self.mime: str = ''
        self.location: str = ''
        self.text: Text = Text()
        self.metadata: DocumentMetadata = DocumentMetadata()
        self.subdocuments: SubdocumentsList = SubdocumentsList()
        self.disallow_additional_properties()
        self._attribute_classes = pmap({
            'text': Text,
            'metadata': DocumentMetadata,
            'subdocuments': SubdocumentsList
        })
        super().__init__(document_obj)

    def add_metadata(self, name: str, value: str) -> None:
        self.metadata[name] = value

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

    def __init__(self, text_obj: Union[str, dict] = None) -> None:
        self._value: str = ''
        self._language: str = ''
        self.disallow_additional_properties()
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


class DocumentMetadata(FreezableMmifObject):
    source: Optional[str]
    app: Optional[str]

    def __init__(self, mmeta_obj: Union[str, dict] = None) -> None:
        # need to set instance variables for ``_named_attributes()`` to work
        self.source = None
        self.app = None
        super().__init__(mmeta_obj)


class Subdocument(FreezableMmifObject):

    def __init__(self, subdocument: Union[str, dict] = None):
        # need to set instance variables for ``_named_attributes()`` to work
        self.id: str = ''
        self.annotation: str = ''
        self.text: Text = Text()
        self._attribute_classes = pmap({'text': Text})
        super().__init__(subdocument)


class SubdocumentsList(FreezableDataList[Subdocument]):
    _items: Dict[str, Subdocument]

    def _deserialize(self, input_list: list) -> None:
        self.items = {item['id']: Subdocument(item) for item in input_list}

    def append(self, value: Subdocument, overwrite=False) -> None:
        super()._append_with_key(value.id, value, overwrite)
