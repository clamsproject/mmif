from typing import Dict, Union, Optional

from .model import MmifObject


class Medium(MmifObject):
    id: str
    type: str
    location: str
    metadata: Dict[str, str]

    def __init__(self, medium_obj: Union[str, dict] = None):
        self.id = ''
        self.type = ''
        self.location = ''
        self.metadata = {}
        super().__init__(medium_obj)

    def _deserialize(self, medium_dict: dict):
        # TODO (krim @ 7/7/20): implement this when `medium` specs are more concrete
        pass

    def add_metadata(self, name: str, value: str):
        self.metadata[name] = value


class Text(MmifObject):
    _value: str
    _language: Optional[str]


class MediumMetadata(MmifObject):
    source: str
    tool: str
