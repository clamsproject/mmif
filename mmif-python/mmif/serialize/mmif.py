import json
from typing import Dict, List, Union

from jsonschema import validate
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
    media: List['Medium']
    views: List['View']

    def __init__(self, mmif_obj: Union[str, dict] = None, validate: bool = True):
        self._context = ''
        self.metadata = {}
        self.media = []
        self.views = []
        if validate:
            self.validate(mmif_obj)
        super().__init__(mmif_obj)

    def _deserialize(self, input_dict: dict) -> None:
        self._context = input_dict['_context']
        self.metadata = input_dict['metadata']
        self.media = [Medium(m) for m in input_dict['media']]
        self.views = [View(v) for v in input_dict['views']]

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

    def add_medium(self, medium: Medium):
        self.media.append(medium)

    def get_media_by_source_view_id(self, source_vid: str = None) -> List[Medium]:
        """
        Method to get all media object queries by its originated view id.
        With current specification, a *source* of a medium can be external or
        an annotation. The *source* field gets its value only in the latter.
        Also note that, depending on how submedia is represented, the value of
        ``source`` field can be either ``view_id`` or ``view_id``:``annotation_id``.
        In either case, this method will return all medium objects that generated
        from a view.
        """
        return [medium for medium in self.media if medium.metadata.source is not None and medium.metadata.source.split(':')[0] == source_vid]

    def get_media_by_app(self, app_id: str) -> List[Medium]:
        return [medium for medium in self.media if medium.metadata.app == app_id]

    def get_media_by_metadata(self, metadata_key: str, metadata_value: str):
        """
        Method to retrieve media by an arbitrary key-value pair in the medium metadata objects
        """
        return [medium for medium in self.media if medium.metadata[metadata_key] == metadata_value]


    def get_media_locations(self, m_type: str) -> List[str]:
        """
        This method returns the file paths of media of given type.
        """
        return [medium.location for medium in self.media if medium.type == m_type and medium.location is not None]

    def get_medium_location(self, m_type: str) -> str:
        """
        Method to get the location of *first* medium of given type.
        """
        # TODO (krim @ 8/10/20): Is returning the first location desirable?
        locations = self.get_media_locations(m_type)
        return locations[0] if len(locations) > 0 else None

    def get_medium_by_id(self, id: str) -> 'Medium':
        for medium in self.media:
            if medium.id == id:
                return medium
        raise KeyError("{} medium not found".format(id))

    def get_view_by_id(self, id: str) -> 'View':
        for view in self.views:
            if view.id == id:
                return view
        raise Exception("{} view not found".format(id))

    def get_all_views_contain(self, at_type: str):
        return [view for view in self.views if at_type in view.metadata.contains]

    def get_view_contains(self, at_type: str):
        # will return the *latest* view
        for view in reversed(self.views):
            if at_type in view.metadata.contains:
                return view
        return None
