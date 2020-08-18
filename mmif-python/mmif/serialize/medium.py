from typing import Union, Optional, List

from .model import MmifObject


__all__ = ['Medium', 'MediumMetadata', 'Submedia']


class Medium(MmifObject):

    def __init__(self, medium_obj: Union[str, dict] = None) -> None:
        self.id: str = ''
        self.type: str = ''
        self.mime: str = ''
        self.location: str = ''
        self.text: Text = Text()
        self.metadata: MediumMetadata = MediumMetadata()
        self.submedia: List[Submedia] = []
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
    def text_language(self) -> str:
        return self.text.lang

    @text_language.setter
    def text_language(self, lang_code: str) -> None:
        if self.text is None:
            self.text = Text()
        self.text.lang = lang_code

    @property
    def text_value(self) -> str:
        return self.text.value

    @text_value.setter
    def text_value(self, s: str) -> None:
        if self.text is None:
            self.text = Text()
        self.text.value = s


class Text(MmifObject):

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


class MediumMetadata(MmifObject):
    source: Optional[str]
    app: Optional[str]

    def __init__(self, mmeta_obj: Union[str, dict] = None) -> None:
        # need to set instance variables for ``_named_attributes()`` to work
        self.source = None
        self.app = None
        super().__init__(mmeta_obj)


class Submedia(MmifObject):

    def __init__(self, submedium: Union[str, dict] = None):
        # need to set instance variables for ``_named_attributes()`` to work
        self.id: str = ''
        self.annotation: str = ''
        self.text: Text = Text()
        self._attribute_classes = {'text': Text}
        super().__init__(submedium)
