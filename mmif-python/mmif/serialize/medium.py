from typing import Union, Optional, List

from .model import MmifObject


__all__ = ['Medium', 'MediumMetadata', 'Submedia']


class Medium(MmifObject):
    id: str
    type: str
    mime: Optional[str] = None
    location: Optional[str] = None
    text: Optional['Text'] = None
    metadata: Optional['MediumMetadata'] = None
    submedia: Optional[List['Submedia']] = None

    def __init__(self, medium_obj: Union[str, dict] = None):
        self.id = ''
        self.type = ''
        self.mime = ''
        self.location = ''
        self.text = Text()
        self.metadata = MediumMetadata()
        self.submedia = []
        self.disallow_additional_properties()
        self._attribute_classes = {
            'text': Text,
            'metadata': MediumMetadata,
            'submedia': List[Submedia]
        }
        super().__init__(medium_obj)

    def add_metadata(self, name: str, value: str) -> None:
        self.metadata[name] = value

    @property
    def text_language(self):
        return self.text.lang

    @text_language.setter
    def text_language(self, lang_code: str):
        if self.text is None:
            self.text = Text()
        self.text.lang = lang_code

    @property
    def text_value(self):
        return self.text.value

    @text_value.setter
    def text_value(self, s: str):
        if self.text is None:
            self.text = Text()
        self.text.value = s


class Text(MmifObject):
    _value: str
    _language: Optional[str]

    def __init__(self, text_obj: Union[str, dict] = None):
        self._value = ''
        self._language = ''
        self.disallow_additional_properties()
        super().__init__(text_obj)

    @property
    def lang(self):
        return self._language

    @lang.setter
    def lang(self, lang_code: str):
        # TODO (krim @ 8/11/20): add validation for language code (ISO 639)
        self._language = lang_code

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, s: str):
        self._value = s


class MediumMetadata(MmifObject):
    source: Optional[str]
    app: Optional[str]

    def __init__(self, mmeta_obj: Union[str, dict] = None):
        # need to set instance variables for ``_named_attributes()`` to work
        self.source = None
        self.app = None
        super().__init__(mmeta_obj)


class Submedia(MmifObject):
    id: str
    annotation: str
    text: 'Text'

    def __init__(self, submedium: Union[str, dict] = None):
        # need to set instance variables for ``_named_attributes()`` to work
        self.id = ""
        self.annotation = ""
        self._attribute_classes = {'text': Text}
        super().__init__(submedium)
