from typing import Dict, Union

from .model import MmifObject


class Annotation(MmifObject):
    properties: Dict[str, str]
    id: str
    at_type: str

    def __init__(self, anno_obj: Union[str, dict] = None):
        self.id = ''
        self.at_type = ''
        self.properties = {}
        super().__init__(anno_obj)

    def _deserialize(self, anno_dict: dict):
        self.at_type = anno_dict['@type']
        self.properties.update(anno_dict['properties'])
        self.id = self.properties.pop('id')

    def serialize(self, pretty: bool = False) -> str:
        self.add_property('id', self.__dict__.pop('id'))
        return self._serialize(self.__dict__)

    def add_property(self, name: str, value: str):
        self.properties[name] = value
