import json
from typing import Dict, List, Union, Optional

import jsonschema.validators
from pkg_resources import resource_stream

import mmif
from .view import View
from .medium import Medium
from .annotation import Annotation
from .model import MmifObject, DataList


__all__ = ['Mmif']


class Mmif(MmifObject):
    # TODO (krim @ 7/6/20): maybe need IRI/URI as a python class for typing?
    _context: str
    metadata: Dict[str, str]
    media: 'MediaList'
    views: 'ViewsList'

    def __init__(self, mmif_obj: Union[str, dict] = None, validate: bool = True):
        self._context = ''
        self.metadata = {}
        self.media = MediaList()
        self.views = ViewsList()
        if validate:
            self.validate(mmif_obj)
        super().__init__(mmif_obj)

    def _deserialize(self, input_dict: dict) -> None:
        self._context = input_dict['_context']
        self.metadata = input_dict['metadata']
        self.media = MediaList(input_dict['media'])
        self.views = ViewsList(input_dict['views'])

    @staticmethod
    def validate(json_str: Union[str, dict]) -> None:
        # NOTE that schema file first needs to be copied to resources directory
        # this is automatically done via setup.py, so for users this shouldn't be a matter

        schema_res = resource_stream(f'{mmif.__name__}.{mmif._res_pkg}', mmif._schema_res_name)
        schema = json.load(schema_res)
        schema_res.close()
        if type(json_str) == str:
            json_str = json.loads(json_str)
        jsonschema.validate(json_str, schema)

    def new_view_id(self) -> str:
        return 'v_' + str(len(self.views))

    def new_view(self) -> View:
        new_view = View()
        new_view.id = self.new_view_id()
        self.views[new_view.id] = new_view
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

    def get_medium_by_id(self, req_med_id: str) -> Medium:
        result = self.media.get(req_med_id)
        if result is None:
            raise KeyError("{} medium not found".format(req_med_id))
        return result

    def get_view_by_id(self, req_view_id: str) -> View:
        result = self.views.get(req_view_id)
        if result is None:
            raise KeyError("{} view not found".format(req_view_id))
        return result

    def get_all_views_contain(self, at_type: str):
        return [view for view in self.views if at_type in view.metadata.contains]

    def get_view_contains(self, at_type: str) -> Optional[View]:
        # will return the *latest* view
        # works as of python 3.6+ because dicts are deterministically ordered by insertion order
        from sys import version_info
        if version_info < (3, 6):
            print("Warning: get_view_contains requires Python 3.6+ for correct behavior")
        for view in reversed(self.views):
            if at_type in view.metadata.contains:
                return view
        return None

    def __getitem__(self, item: str) -> Union[Medium, View, Annotation]:
        """
        getitem implementation for Mmif.

        >>> obj = Mmif('''{"@context": "http://mmif.clams.ai/0.1.0/context/mmif.json","metadata": {"mmif": "http://mmif.clams.ai/0.1.0","contains": {"http://mmif.clams.ai/vocabulary/0.1.0/BoundingBox": ["v1"]}},"media": [{"id": "m1","type": "image","mime": "image/jpeg","location": "/var/archive/image-0012.jpg"}],"views": [{"id": "v1","metadata": {"contains": {"BoundingBox": {"unit": "pixels"}},"medium": "m1","tool": "http://tools.clams.io/east/1.0.4"},"annotations": [{"@type": "BoundingBox","properties": {"id": "bb1","coordinates": [[90,40], [110,40], [90,50], [110,50]] }}]}]}''')
        >>> type(obj['m1'])
        <class 'mmif.serialize.medium.Medium'>
        >>> type(obj['v1'])
        <class 'mmif.serialize.view.View'>
        >>> type(obj['v1:bb1'])
        <class 'mmif.serialize.annotation.Annotation'>
        >>> obj['asdf']
        Traceback (most recent call last):
            ...
        KeyError: 'ID not found: asdf'

        :raises KeyError: if the item is not found or if the search results are ambiguous
        :param item: the search string, a medium ID, a view ID, or a view-scoped annotation ID
        :return: the object searched for
        """
        split_attempt = item.split(':')

        medium_result = self.media.get(split_attempt[0])
        view_result = self.views.get(split_attempt[0])

        if len(split_attempt) == 1:
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


class MediaList(DataList[Medium]):

    def _deserialize(self, input_list: list) -> None:
        self.items = {item['id']: Medium(item) for item in input_list}


class ViewsList(DataList[View]):

    def _deserialize(self, input_list: list) -> None:
        self.items = {item['id']: View(item) for item in input_list}
