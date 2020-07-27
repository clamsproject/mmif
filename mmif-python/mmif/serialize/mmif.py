import json
from typing import Dict, List, Union

from jsonschema import validate
from pkg_resources import resource_stream

import mmif
from .view import View
from .medium import Medium
from .model import MmifObject


class Mmif(MmifObject):
    """
    MmifObject that represents a full MMIF file.
    """

    # TODO (krim @ 7/6/20): maybe need IRI/URI as a python class for typing?
    _context: str
    metadata: Dict[str, str]
    media: List['Medium']
    views: List['View']

    def __init__(self, mmif_obj: Union[str, dict] = None, validate: bool = True):
        """
        Constructs a MMIF object.
        :param mmif_obj: the JSON-LD data
        :param validate: whether to validate the data against the MMIF JSON-LD schema.
        """
        self._context = ''
        self.metadata = {}
        self.media = []
        self.views = []
        if validate:
            self.validate(mmif_obj)
        super().__init__(mmif_obj)

    def _deserialize(self, input_dict: dict) -> None:
        """
        Maps a plain python dict object to a MMIF object.

        Extracts _context and metadata fields and processes media and views lists
        into lists of Medium and View objects.

        :param input_dict: the preprocessed MMIF dict
        :return: None
        """
        self._context = input_dict['_context']
        self.metadata = input_dict['metadata']
        self.media = [Medium(m) for m in input_dict['media']]
        self.views = [View(v) for v in input_dict['views']]

    @staticmethod
    def validate(json_str: Union[str, dict]) -> None:
        """
        Validates a MMIF JSON-LD object against the MMIF Schema.

        Note that this method operates before processing by MmifObject._load_str,
        so it expects @ and not _ for the JSON-LD @-keys.

        :raises ValidationError: if the input fails validation
        :param json_str: a MMIF JSON-LD dict or string
        :return: None
        """
        # NOTE that schema file first needs to be copied to resources directory
        # this is automatically done via setup.py, so for users this shouldn't be a matter

        schema_res = resource_stream(f'{mmif.__name__}.{mmif._res_pkg}', mmif._schema_res_name)
        schema = json.load(schema_res)
        schema_res.close()
        if type(json_str) == str:
            json_str = json.loads(json_str)
        validate(json_str, schema)

    def new_view_id(self):
        """
        Fetches an ID for a new view.
        :return: the ID
        """
        return 'v_' + str(len(self.views))

    def new_view(self) -> View:
        """
        Creates an empty view with a new ID and appends it to the views list.
        :return: a reference to the new View object
        """
        new_view = View()
        new_view.id = self.new_view_id()
        self.views.append(new_view)
        return new_view

    def add_media(self, medium: Medium) -> None:
        """
        Appends a Medium object to the media list.

        Fails if there is already a medium of the same type in the MMIF object.

        :param medium: the Medium object to add
        :return: None
        """
        try:
            self.get_medium_location(medium.type)
        # TODO (krim @ 10/7/2018): if get_m_location returns, raise "already exists" error
        except Exception:
            self.media.append(medium)

    def get_medium_location(self, md_type: str) -> str:
        """
        Finds the location of the medium in the MMIF object of the given type.
        :param md_type: the type to search for
        :return: the value of the location field in the corresponding medium
        """
        for medium in self.media:
            if medium["type"] == md_type:
                return medium["location"]
        raise Exception("{} type media not found".format(md_type))

    def get_medium_by_id(self, id: str) -> 'Medium':
        """
        Finds a Medium object with the given ID.
        :param id: the ID to search for
        :return: a reference to the corresponding medium, if it exists
        :raises Exception: if there is no corresponding medium
        """
        for medium in self.media:
            if medium.id == id:
                return medium
        raise Exception("{} medium not found".format(id))

    def get_view_by_id(self, id: str) -> 'View':
        """
        Finds a View object with the given ID.
        :param id: the ID to search for
        :return: a reference to the corresponding view, if it exists
        :raises Exception: if there is no corresponding view
        """
        for view in self.views:
            if view.id == id:
                return view
        raise Exception("{} view not found".format(id))

    def get_all_views_contain(self, at_type: str) -> List[View]:
        """
        DEPRECATED:
        Returns the list of all views in the MMIF if a given type
        type is present in the top-level 'contains' field.
        :param at_type: the type to check for
        :return: the list of views, or an empty list if the type is not found
        """
        return [view for view in self.views if at_type in view.metadata.contains]

    def get_view_contains(self, at_type: str):
        """
        Returns the last view appended if the given type is
        present in the top-level 'contains' field.
        :param at_type: the type to check for
        :return: the view, or None if the type is not found
        """
        # will return the *latest* view
        for view in reversed(self.views):
            if at_type in view.metadata.contains:
                return view
        return None
