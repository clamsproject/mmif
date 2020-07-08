import json
from typing import Dict, List, Union

from jsonschema import validate
from pkg_resources import resource_stream

import mmif
from .view import View
from .medium import Medium
from .model import MmifObject


class Mmif(MmifObject):
    # TODO (krim @ 7/6/20): maybe need IRI/URI as a python class for typing?
    context: str
    metadata: Dict[str, str]
    media: List[Medium]
    # this contains is different from contains field in view, in that this is only for sniffing purpose
    # and has view ids only
    # TODO (krim @ 7/7/20): should these lists be sorted? default behavior of `get_view_contains` would be
    # returning the latest view, so the list should sorted by generation timestamp, I guess.
    contains: Dict[str, List[str]]
    views: List['View']

    def __init__(self, mmif_obj: Union[str, dict] = None, validate: bool = True):
        self.context = ''
        self.metadata = {}
        self.media = []
        self.views = []
        if validate:
            self.validate(mmif_obj)
        super().__init__(mmif_obj)

    def serialize(self, pretty: bool =False) -> str:
        """
        Overrides the default `serialize` to add `@` sign to context field.
        """
        d = self.__dict__.copy()
        d['@context'] = d.pop('context')
        return self._serialize(d, pretty)

    def _deserialize(self, mmif_dict: dict):

        # TODO (krim @ 10/3/2018): more robust json parsing
        self.context = mmif_dict["@context"]
        self.metadata = mmif_dict["metadata"]
        self.media = mmif_dict["media"]
        self.views = mmif_dict["views"]

    @staticmethod
    def validate(json_str: Union[str, dict]):
        # NOTE that schema file first needs to be copied to resources directory
        # this is automatically done via setup.py, so for users this shouldn't be a matter

        schema_res = resource_stream(f'{mmif.__name__}.{mmif._res_pkg}', mmif._schema_res_name)
        schema = json.load(schema_res)
        schema_res.close()
        if type(json_str) == str:
            json_str = json.loads(json_str)
        validate(json_str, schema)

    def new_view_id(self):
        return 'v_' + str(len(self.views))

    def new_view(self):
        new_view = View()
        new_view.id = self.new_view_id()
        self.views.append(new_view)
        return new_view

    def add_media(self, medium: Medium):
        try:
            self.get_medium_location(medium.type)
        # TODO (krim @ 10/7/2018): if get_m_location returns, raise "already exists" error
        except Exception:
            self.media.append(medium)

    def get_medium_location(self, md_type: str):
        for medium in self.media:
            if medium["type"] == md_type:
                return medium["location"]
        raise Exception("{} type media not found".format(md_type))

    def get_view_by_id(self, id: str):
        for view in self.views:
            if view.id == id:
                return view
        raise Exception("{} view not found".format(id))

    def get_view_contains(self, at_type: str):
        return self.get_view_by_id(self.contains[at_type][-1])
