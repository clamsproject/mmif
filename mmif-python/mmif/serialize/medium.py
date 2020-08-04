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
        super().__init__(medium_obj)

    def _deserialize(self, medium_dict: dict):
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

    def add_metadata(self, name: str, value: str):
        self.metadata[name] = value


class Text(MmifObject):
    _value: str
    _language: Optional[str]

    def __init__(self, text_obj: Union[str, dict]):
        super().__init__(text_obj)


class MediumMetadata(MmifObject):
    source: str
    tool: str
    metadata: dict

    def _deserialize(self, input_dict: dict) -> None:
        self.metadata = input_dict

    def _serialize(self):
        return MmifObject(self.metadata)._serialize()

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def __getitem__(self, key):
        return self.metadata[key]


class Submedia(MmifObject):
    id: str
    annotation: str
    text: 'Text'
