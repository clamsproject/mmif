import json
from typing import Dict, List, Union

import jsonschema.validators
from pkg_resources import resource_stream

import mmif
from .view import View
from .medium import Medium
from .model import MmifObject


__all__ = ['Mmif']


class Mmif(MmifObject):
    # TODO (krim @ 7/6/20): maybe need IRI/URI as a python class for typing?
    _context: str
    metadata: Dict[str, str]
    media: Dict[str, 'Medium']
    views: Dict[str, 'View']

    def __init__(self, mmif_obj: Union[str, dict] = None, validate: bool = True):
        self._context = ''
        self.metadata = {}
        self.media: Dict[str, Medium] = {}
        self.views: Dict[str, View] = {}
        if validate:
            self.validate(mmif_obj)
        super().__init__(mmif_obj)

    def _serialize(self) -> dict:
        intermediate = super()._serialize()
        intermediate.update(media=list(self.media.values()), views=list(self.views.values()))
        return intermediate

    def _deserialize(self, input_dict: dict) -> None:
        self._context = input_dict['_context']
        self.metadata = input_dict['metadata']
        self.media = {m['id']: Medium(m) for m in input_dict['media']}
        self.views = {v['id']: View(v) for v in input_dict['views']}

    @staticmethod
    def validate(json_str: Union[str, dict]):
        # NOTE that schema file first needs to be copied to resources directory
        # this is automatically done via setup.py, so for users this shouldn't be a matter

        schema_res = resource_stream(f'{mmif.__name__}.{mmif._res_pkg}', mmif._schema_res_name)
        schema = json.load(schema_res)
        schema_res.close()
        if type(json_str) == str:
            json_str = json.loads(json_str)
        jsonschema.validate(json_str, schema)

    def new_view_id(self):
        return 'v_' + str(len(self.views))

    def new_view(self):
        new_view = View()
        new_view.id = self.new_view_id()
        self.views[new_view.id] = new_view
        return new_view

    def add_media(self, medium: Medium):
        try:
            self.get_medium_location(medium.type)
        # TODO (krim @ 10/7/2018): if get_m_location returns, raise "already exists" error
        except Exception:
            self.media[medium.id] = medium

    def get_medium_location(self, md_type: str):
        for medium in self.media.values():
            if medium.type == md_type:
                return medium.location
        raise Exception("{} type media not found".format(md_type))

    def get_medium_by_id(self, req_med_id: str):
        for med_id, medium in self.media.items():
            if med_id == req_med_id:
                return medium
        raise Exception("{} medium not found".format(req_med_id))

    def get_view_by_id(self, req_view_id: str):
        for view_id, view in self.views.items():
            if view_id == req_view_id:
                return view
        raise Exception("{} view not found".format(req_view_id))

    def get_view_contains(self, at_type: str):
        # will return the *latest* view
        # works as of python 3.6+ because dicts are deterministically ordered by insertion order
        from sys import version_info
        if version_info < (3, 6):
            print("Warning: get_view_contains requires Python 3.6+ for correct behavior")
        for view_id, view in reversed(self.views.items()):
            return view
        return None

    def __getitem__(self, item: str):
        split_attempt = item.split(':')

        medium_result = self.media.get(split_attempt[0])
        view_result = self.views.get(split_attempt[0])

        if len(split_attempt) == 1 or not view_result:
            anno_result = None
        elif view_result:
            anno_result = view_result[split_attempt[1]]
        else:
            raise KeyError("Tried to subscript into a view that doesn't exist")

        if view_result and medium_result:
            raise KeyError("Ambiguous ID search result")
        if not (view_result or medium_result):
            raise KeyError("ID not found: %s" % item)
        return anno_result or view_result or medium_result
