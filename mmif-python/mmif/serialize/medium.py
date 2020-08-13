from typing import Union, Optional, List

from .model import MmifObject


__all__ = ['Medium', 'MediumMetadata', 'Submedia']


class Medium(MmifObject):
    id: str
    type: str
    mime: Optional[str] = None
    location: Optional[str] = None
    text: Optional['Text'] = None # users don't need to directly access nested text object
    metadata: Optional['MediumMetadata'] = None
    submedia: Optional[List['Submedia']] = None

    def __init__(self, medium_obj: Union[str, dict] = None):
        self.id = ''
        self.type = ''
        self.metadata = MediumMetadata()
        super().__init__(medium_obj)

    def _deserialize(self, medium_dict: dict) -> None:
        self.id = medium_dict['id']
        self.type = medium_dict['type']
        if 'metadata' in medium_dict:
            self.metadata = MediumMetadata(medium_dict.get('metadata'))
        if 'mime' in medium_dict:
            self.mime = medium_dict['mime']
        if 'location' in medium_dict:
            self.location = medium_dict['location']
        if 'text' in medium_dict:
            self.text = Text(medium_dict['text'])

    def add_metadata(self, name: str, value: str) -> None:
        self.metadata[name] = value

    @property
    def text_language(self):
        return self.text.lang

    @text_language.setter
    def text_language(self, l: str):
        if self.text is None:
            self.text = Text()
        self.text.lang = l

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
        super().__init__(text_obj)

    @property
    def lang(self):
        return self._language

    @lang.setter
    def lang(self, l: str):
        # TODO (krim @ 8/11/20): add validation for language code (ISO 639)
        self._language = l

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, s: str):
        self._value = s


class MediumMetadata(MmifObject):
    source: Optional[str]
    app: Optional[str]
    _unnamed_attributes: dict

    def __init__(self, mmeta_obj: Union[str, dict] = None):
        # need to set instance variables for ``_named_attributes()`` to work
        self.source = None
        self.app = None
        self._unnamed_attributes: dict = {}
        super().__init__(mmeta_obj)

    def _named_attributes(self):
        return (n for n in self.__dict__.keys() if n != '_unnamed_attributes')

    def _deserialize(self, input_dict: dict) -> None:
        for k, v in input_dict.items():
            self[k] = v

    def _serialize(self):
        # TODO (krim @ 8/11/20): this logic can be used for other MMIF classes that have some mandatory, some optional, and a free-for-all map
        serializing_obj = {}
        serializing_obj.update(self._unnamed_attributes)
        for k, v in self.__dict__.items():
            if k != '_unnamed_attributes' and v is not None:
                serializing_obj[k] = v
        # this will override superclasses' __len__ logic because metadata object has two-tiered attributes
        # we can push this behavior up to the superclass.__len__ method
        return MmifObject(serializing_obj)._serialize() if len(serializing_obj) > 0 else None

    def __len__(self):
        return sum([self[named] is not None for named in self._named_attributes()]) + len(self._unnamed_attributes)

    def __setitem__(self, key, value):
        if key in self._named_attributes():
            self.__dict__[key] = value
        else:
            self._unnamed_attributes[key] = value

    def __getitem__(self, key):
        if key in self._named_attributes():
            return self.__dict__[key]
        else:
            return self._unnamed_attributes[key]


class Submedia(MmifObject):
    id: str
    annotation: str
    text: 'Text'
