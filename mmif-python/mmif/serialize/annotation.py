from typing import Dict, Union

from .model import MmifObject


class Annotation(MmifObject):
    properties: Dict[str, str]
    at_type: str

    @property
    def id(self):
        return self.properties['id']

    @id.setter
    def id(self, aid):
        self.properties['id'] = aid

    def __init__(self, anno_obj: Union[str, dict] = None):
        self.id = ''
        self.at_type = ''
        self.properties = {}
        super().__init__(anno_obj)

    def add_property(self, name: str, value: str):
        self.properties[name] = value
