import json
from typing import Dict, List, Union, Optional, Any

from jsonschema import validate
from pkg_resources import resource_stream

import mmif
from .view import View
from .medium import Medium
from .model import MmifObject


class Mmif(MmifObject):
    # TODO (krim @ 7/6/20): maybe need IRI/URI as a python class for typing?
    _context: str
    metadata: Dict[str, str]
    media: List[Medium]
    views: List['View']

    def __init__(self, mmif_obj: Union[str, dict] = None, validate: bool = True):
        self._context = ''
        self.metadata = {}
        self.media = []
        self.views = []
        if validate:
            self.validate(mmif_obj)
        super().__init__(mmif_obj)

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

    def get_all_views_contain(self, at_type: str):
        return [view for view in self.views if at_type in view.contains]

    def get_view_contains(self, at_type: str):
        # will return the *latest* view
        for view in reversed(self.views):
            if at_type in view.contains:
                return view
        return None
