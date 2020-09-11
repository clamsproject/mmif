"""
The :mod:`mmif` module contains the classes used to represent a full MMIF
file as a live Python object.

See the specification docs and the JSON Schema file for more information.
"""

import json
from datetime import datetime
from typing import List, Union, Optional, Dict, ClassVar

import jsonschema.validators
from pkg_resources import resource_stream

import mmif
from pyrsistent import pmap

from .view import View
from .document import Document
from .annotation import Annotation
from .model import MmifObject, DataList, FreezableDataList

__all__ = ['Mmif']


class Mmif(MmifObject):
    """
    MmifObject that represents a full MMIF file.

    :param mmif_obj: the JSON data
    :param validate: whether to validate the data against the MMIF JSON schema.
    """

    view_prefix: ClassVar[str] = 'v_'

    def __init__(self, mmif_obj: Union[str, dict] = None, *, validate: bool = True, frozen: bool = True) -> None:
        # TODO (krim @ 7/6/20): maybe need IRI/URI as a python class for typing?
        self._context: str = ''
        self.metadata: MmifMetadata = MmifMetadata()
        self.documents: DocumentsList = DocumentsList()
        self.views: ViewsList = ViewsList()
        if validate:
            self.validate(mmif_obj)
        self.disallow_additional_properties()
        self._attribute_classes = pmap({
            'documents': DocumentsList,
            'views': ViewsList
        })
        super().__init__(mmif_obj)
        if frozen:
            self.freeze_documents()
            self.freeze_views()

    @staticmethod
    def validate(json_str: Union[str, dict]) -> None:
        """
        Validates a MMIF JSON object against the MMIF Schema.
        Note that this method operates before processing by MmifObject._load_str,
        so it expects @ and not _ for the JSON-LD @-keys.

        :raises jsonschema.exceptions.ValidationError: if the input fails validation
        :param json_str: a MMIF JSON dict or string
        :return: None
        """
        # NOTE that schema file first needs to be copied to resources directory
        # this is automatically done via setup.py, so for users this shouldn't be a matter

        schema_res = resource_stream(f'{mmif.__name__}.{mmif._res_pkg}', mmif._schema_res_name)
        schema = json.load(schema_res)
        schema_res.close()
        if type(json_str) == str:
            json_str = json.loads(json_str)
        jsonschema.validate(json_str, schema)

    def new_view_id(self) -> str:
        """
        Fetches an ID for a new view.

        :return: the ID
        """
        index = len(self.views)
        new_id = self.view_prefix + str(index)
        while new_id in self.views:
            index += 1
            new_id = self.view_prefix + str(index)
        return new_id

    def new_view(self) -> View:
        """
        Creates an empty view with a new ID and appends it to the views list.

        :return: a reference to the new View object
        """
        new_view = View()
        new_view.id = self.new_view_id()
        new_view.metadata.timestamp = datetime.now()
        self.views.append(new_view)
        return new_view

    def add_view(self, view: View, overwrite=False) -> None:
        """
        Appends a View object to the views list.

        Fails if there is already a view with the same ID in the MMIF object.

        :param view: the Document object to add
        :param overwrite: if set to True, will overwrite
                          an existing view with the same ID
        :return: None
        """
        self.views.append(view, overwrite)

    def add_document(self, document: Document, overwrite=False) -> None:
        """
        Appends a Document object to the documents list.

        Fails if there is already a document with the same ID in the MMIF object.

        :param document: the Document object to add
        :param overwrite: if set to True, will overwrite
                          an existing view with the same ID
        :return: None
        """
        if not self.documents.is_frozen():
            self.documents.append(document, overwrite)
        else:
            raise TypeError("MMIF object is frozen")

    def freeze_documents(self) -> bool:
        """
        Deeply freezes the list of documents. Returns the result of
        the deep_freeze() call, signifying whether everything
        was fully frozen or not.
        """
        return self.documents.deep_freeze()

    def freeze_views(self) -> bool:
        """
        Deeply freezes all of the existing views without freezing
        the list of views itself. Returns the conjunct of the returns
        of all of the deep_freeze() calls, signifying whether everything
        was fully frozen or not.
        """
        fully_frozen = True
        for view in self.views:
            fully_frozen &= view.deep_freeze()
        return fully_frozen

    def get_documents_by_source_view_id(self, source_vid: str = None) -> List[Document]:
        """
        Method to get all documents object queries by its originated view id.
        With current specification, a *source* of a document can be external or
        an annotation. The *source* field gets its value only in the latter.
        Also note that, depending on how subdocuments is represented, the value of
        ``source`` field can be either ``view_id`` or ``view_id``:``annotation_id``.
        In either case, this method will return all document objects that generated
        from a view.

        :param source_vid: the source view ID to search for
        :return: a list of documents matching the requested source view ID
        """
        return [document for document in self.documents
                if document.metadata.source is not None and document.metadata.source.split(':')[0] == source_vid]

    def get_documents_by_app(self, app_id: str) -> List[Document]:
        """
        Method to get all documents object queries by its originated app name.

        :param app_id: the app name to search for
        :return: a list of documents matching the requested app name
        """
        return [document for document in self.documents if document.metadata.app == app_id]

    def get_documents_by_metadata(self, metadata_key: str, metadata_value: str) -> List[Document]:
        """
        Method to retrieve documents by an arbitrary key-value pair in the document metadata objects.

        :param metadata_key: the metadata key to search for
        :param metadata_value: the metadata value to match
        :return: a list of documents matching the requested metadata key-value pair
        """
        return [document for document in self.documents if document.metadata[metadata_key] == metadata_value]

    def get_documents_locations(self, m_type: str) -> List[str]:
        """
        This method returns the file paths of documents of given type.

        :param m_type: the type to search for
        :return: a list of the values of the location fields in the corresponding documents
        """
        return [document.location for document in self.documents if document.type == m_type and len(document.location) > 0]

    def get_document_location(self, m_type: str) -> str:
        """
        Method to get the location of *first* document of given type.

        :param m_type: the type to search for
        :return: the value of the location field in the corresponding document
        """
        # TODO (krim @ 8/10/20): Is returning the first location desirable?
        locations = self.get_documents_locations(m_type)
        return locations[0] if len(locations) > 0 else None

    def get_document_by_id(self, req_med_id: str) -> Document:
        """
        Finds a Document object with the given ID.

        :param req_med_id: the ID to search for
        :return: a reference to the corresponding document, if it exists
        :raises Exception: if there is no corresponding document
        """
        result = self.documents.get(req_med_id)
        if result is None:
            raise KeyError("{} document not found".format(req_med_id))
        return result

    def get_view_by_id(self, req_view_id: str) -> View:
        """
        Finds a View object with the given ID.

        :param req_view_id: the ID to search for
        :return: a reference to the corresponding view, if it exists
        :raises Exception: if there is no corresponding view
        """
        result = self.views.get(req_view_id)
        if result is None:
            raise KeyError("{} view not found".format(req_view_id))
        return result

    def get_all_views_contain(self, at_type: str) -> List[View]:
        """
        Returns the list of all views in the MMIF if a given type
        type is present in that view's 'contains' metadata.

        :param at_type: the type to check for
        :return: the list of views that contain the type
        """
        return [view for view in self.views if at_type in view.metadata.contains]

    def get_view_contains(self, at_type: str) -> Optional[View]:
        """
        Returns the last view appended that contains the given
        type in its 'contains' metadata.

        :param at_type: the type to check for
        :return: the view, or None if the type is not found
        """
        # will return the *latest* view
        # works as of python 3.6+ (checked by setup.py) because dicts are deterministically ordered by insertion order
        for view in reversed(self.views):
            if at_type in view.metadata.contains:
                return view
        return None

    def __getitem__(self, item: str) -> Union[Document, View, Annotation]:
        """
        getitem implementation for Mmif.

        >>> obj = Mmif('''{"@context": "http://mmif.clams.ai/0.1.0/context/mmif.json","metadata": {"mmif": "http://mmif.clams.ai/0.1.0","contains": {"http://mmif.clams.ai/vocabulary/0.1.0/BoundingBox": ["v1"]}},"documents": [{"id": "m1","type": "image","mime": "image/jpeg","location": "/var/archive/image-0012.jpg"}],"views": [{"id": "v1","metadata": {"contains": {"BoundingBox": {"unit": "pixels"}},"document": "m1","tool": "http://tools.clams.io/east/1.0.4"},"annotations": [{"@type": "BoundingBox","properties": {"id": "bb1","coordinates": [[90,40], [110,40], [90,50], [110,50]] }}]}]}''')
        >>> type(obj['m1'])
        <class 'mmif.serialize.document.Document'>
        >>> type(obj['v1'])
        <class 'mmif.serialize.view.View'>
        >>> type(obj['v1:bb1'])
        <class 'mmif.serialize.annotation.Annotation'>
        >>> obj['asdf']
        Traceback (most recent call last):
            ...
        KeyError: 'ID not found: asdf'

        :raises KeyError: if the item is not found or if the search results are ambiguous
        :param item: the search string, a document ID, a view ID, or a view-scoped annotation ID
        :return: the object searched for
        """
        if item in self._named_attributes():
            return self.__dict__[item]
        split_attempt = item.split(':')

        document_result = self.documents.get(split_attempt[0])
        view_result = self.views.get(split_attempt[0])

        if len(split_attempt) == 1:
            anno_result = None
        elif view_result:
            anno_result = view_result[split_attempt[1]]
        else:
            raise KeyError("Tried to subscript into a view that doesn't exist")

        if view_result and document_result:
            raise KeyError("Ambiguous ID search result")
        if not (view_result or document_result):
            raise KeyError("ID not found: %s" % item)
        return anno_result or view_result or document_result


class MmifMetadata(MmifObject):
    """
    Basic MmifObject class to contain the top-level metadata of a MMIF file.

    :param metadata_obj: the JSON data
    """

    def __init__(self, metadata_obj: Union[str, dict] = None) -> None:
        super().__init__(metadata_obj)


class DocumentsList(FreezableDataList[Document]):
    """
    DocumentsList object that implements :class:`mmif.serialize.model.DataList`
    for :class:`mmif.serialize.document.Document`.
    """
    _items: Dict[str, Document]

    def _deserialize(self, input_list: list) -> None:
        """
        Extends base ``_deserialize`` method to initialize ``items`` as a dict from
        document IDs to :class:`mmif.serialize.document.Document` objects.

        :param input_list: the JSON data that defines the list of documents
        :return: None
        """
        self._items = {item['id']: Document(item) for item in input_list}

    def append(self, value: Document, overwrite=False) -> None:
        """
        Appends a document to the list.

        Fails if there is already a document with the same ID
        in the list, unless ``overwrite`` is set to True.

        :param value: the :class:`mmif.serialize.document.Document`
                      object to add
        :param overwrite: if set to True, will overwrite an
                          existing document with the same ID
        :raises KeyError: if ``overwrite`` is set to False and
                          a document with the same ID exists
                          in the list
        :return: None
        """
        super()._append_with_key(value.id, value, overwrite)


class ViewsList(DataList[View]):
    """
    ViewsList object that implements :class:`mmif.serialize.model.DataList`
    for :class:`mmif.serialize.view.View`.
    """
    _items: Dict[str, View]

    def _deserialize(self, input_list: list) -> None:
        """
        Extends base ``_deserialize`` method to initialize ``items`` as a dict from
        view IDs to :class:`mmif.serialize.view.View` objects.

        :param input_list: the JSON data that defines the list of views
        :return: None
        """
        self._items = {item['id']: View(item) for item in input_list}

    def append(self, value: View, overwrite=False) -> None:
        """
        Appends a view to the list.

        Fails if there is already a view with the same ID
        in the list, unless ``overwrite`` is set to True.

        :param value: the :class:`mmif.serialize.view.View`
                      object to add
        :param overwrite: if set to True, will overwrite an
                          existing view with the same ID
        :raises KeyError: if ``overwrite`` is set to False and
                          a view with the same ID exists
                          in the list
        :return: None
        """
        super()._append_with_key(value.id, value, overwrite)
