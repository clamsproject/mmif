"""
The :mod:`medium` module contains the classes used to represent a
MMIF medium as a live Python object.

In MMIF, media are objects that either point to a file containing
the medium being described, or contain the medium directly in some
text medium cases.
"""

from typing import Union, Optional, Dict
from pyrsistent import pmap

from .model import FreezableMmifObject, FreezableDataList


__all__ = ['Medium', 'MediumMetadata', 'Submedium', 'Text']


class Medium(FreezableMmifObject):
    """
    Medium object that represents a single medium in a MMIF file.

    A medium is identified by an ID, and contains certain attributes
    and potentially contains the contents of the medium itself,
    metadata about how the medium was created, and/or a list of
    submedia grouped together logically.

    If ``medium_obj`` is not provided, an empty Medium will be generated.

    :param medium_obj: the JSON data that defines the medium
    """

    def __init__(self, medium_obj: Union[str, dict] = None) -> None:
        self.id: str = ''
        self.type: str = ''
        self.mime: str = ''
        self.location: str = ''
        self.text: Text = Text()
        self.metadata: MediumMetadata = MediumMetadata()
        self.submedia: SubmediaList = SubmediaList()
        self.disallow_additional_properties()
        self._attribute_classes = pmap({
            'text': Text,
            'metadata': MediumMetadata,
            'submedia': SubmediaList
        })
        super().__init__(medium_obj)

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


class MediumMetadata(FreezableMmifObject):
    source: Optional[str]
    app: Optional[str]

    def __init__(self, mmeta_obj: Union[str, dict] = None) -> None:
        # need to set instance variables for ``_named_attributes()`` to work
        self.source = None
        self.app = None
        super().__init__(mmeta_obj)


class Submedium(FreezableMmifObject):

    def __init__(self, submedium: Union[str, dict] = None):
        # need to set instance variables for ``_named_attributes()`` to work
        self.id: str = ''
        self.annotation: str = ''
        self.text: Text = Text()
        self._attribute_classes = pmap({'text': Text})
        super().__init__(submedium)


class SubmediaList(FreezableDataList[Submedium]):
    _items: Dict[str, Submedium]

    def _deserialize(self, input_list: list) -> None:
        self.items = {item['id']: Submedium(item) for item in input_list}

    def append(self, value: Submedium, overwrite=False) -> None:
        super()._append_with_key(value.id, value, overwrite)
