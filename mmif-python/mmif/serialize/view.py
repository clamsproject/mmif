"""
The :mod:`view` module contains the classes used to represent a MMIF view
as a live Python object.

In MMIF, views are created by apps in a pipeline that are annotating
data that was previously present in the MMIF file.
"""

from datetime import datetime
from typing import Dict, Union, Optional
import dateutil.parser
from pyrsistent import pmap, pvector

from .annotation import Annotation, Document
from .model import FreezableMmifObject, FreezableDataList, FreezableDataDict
from mmif.vocabulary import ThingTypesBase


__all__ = ['View', 'ViewMetadata', 'Contain']


class View(FreezableMmifObject):
    """
    View object that represents a single view in a MMIF file.

    A view is identified by an ID, and contains certain metadata,
    a list of annotations, and potentially a JSON-LD ``@context``
    IRI.

    If ``view_obj`` is not provided, an empty View will be generated.

    :param view_obj: the JSON data that defines the view
    """

    def __init__(self, view_obj: Union[bytes, str, dict] = None) -> None:
        self.id: str = ''
        self.metadata: ViewMetadata = ViewMetadata()
        self.annotations: AnnotationsList = AnnotationsList()
        self.disallow_additional_properties()
        self._attribute_classes = pmap({
            'metadata': ViewMetadata,
            'annotations': AnnotationsList
        })
        self._required_attributes = pvector(["id", "metadata", "annotations"])
        super().__init__(view_obj)

    def new_contain(self, at_type: Union[str, ThingTypesBase], contain_dict: dict = None) -> Optional['Contain']:
        """
        Adds a new element to the ``contains`` metadata.

        :param at_type: the ``@type`` of the annotation type being added
        :param contain_dict: any metadata associated with the annotation type
        :return: the generated :class:`Contain` object
        """
        return self.metadata.new_contain(at_type, contain_dict)

    def new_annotation(self, aid: str, at_type: Union[str, ThingTypesBase], overwrite=False) -> 'Annotation':
        """
        Generates a new :class:`mmif.serialize.annotation.Annotation`
        object and adds it to the current view.

        Fails if there is already an annotation with the same ID
        in the view, unless ``overwrite`` is set to True.

        :param aid: the desired ID of the annotation
        :param at_type: the desired ``@type`` of the annotation
        :param overwrite: if set to True, will overwrite an
                          existing annotation with the same ID
        :raises KeyError: if ``overwrite`` is set to False and
                          an annotation with the same ID exists
                          in the view
        :return: the generated :class:`mmif.serialize.annotation.Annotation`
        """
        new_annotation = Annotation()
        new_annotation.at_type = at_type
        new_annotation.id = aid
        return self.add_annotation(new_annotation, overwrite)

    def add_annotation(self, annotation: 'Annotation', overwrite=False) -> 'Annotation':
        """
        Adds an annotation to the current view.

        Fails if there is already an annotation with the same ID
        in the view, unless ``overwrite`` is set to True.

        :param annotation: the :class:`mmif.serialize.annotation.Annotation`
                           object to add
        :param overwrite: if set to True, will overwrite an
                          existing annotation with the same ID
        :raises KeyError: if ``overwrite`` is set to False and
                          an annotation with the same ID exists
                          in the view
        :return: the same Annotation object passed in as ``annotation``
        """
        self.annotations.append(annotation, overwrite)
        self.new_contain(annotation.at_type)
        return annotation

    def add_document(self, document: Document, overwrite=False) -> Annotation:
        """
        Appends a Document object to the annotations list.

        Fails if there is already a document with the same ID in the annotations list.

        :param document: the Document object to add
        :param overwrite: if set to True, will overwrite
                          an existing view with the same ID
        :return: None
        """
        document.parent = self.id
        return self.add_annotation(document, overwrite)

    def get_documents(self):
        return [annotation for annotation in self.annotations if annotation.is_document()]

    def get_document_by_id(self, doc_id) -> Document:
        doc_found = self.annotations.get(doc_id)
        if doc_found is None or not isinstance(doc_found, Document):
            raise KeyError(f"{doc_id} not found in view {self.id}.")
        else:
            return doc_found

    def __getitem__(self, key: str) -> 'Annotation':
        """
        getitem implementation for View.

        >>> obj = View('''{"id": "v1","metadata": {"contains": {"BoundingBox": {"unit": "pixels"}},"document": "m1","tool": "http://tools.clams.io/east/1.0.4"},"annotations": [{"@type": "BoundingBox","properties": {"id": "bb1","coordinates": [[90,40], [110,40], [90,50], [110,50]] }}]}''')
        >>> type(obj['bb1'])
        <class 'mmif.serialize.annotation.Annotation'>
        >>> obj['asdf']
        Traceback (most recent call last):
            ...
        KeyError: 'Annotation ID not found: asdf'

        :raises KeyError: if the key is not found
        :param key: the search string.
        :return: the :class:`mmif.serialize.annotation.Annotation` object searched for
        """
        if key in self._named_attributes():
            return self.__dict__[key]
        anno_result = self.annotations.get(key)
        if not anno_result:
            raise KeyError("Annotation ID not found: %s" % key)
        return anno_result


class ViewMetadata(FreezableMmifObject):
    """
    ViewMetadata object that represents the ``metadata`` object within a MMIF view.

    :param viewmetadata_obj: the JSON data that defines the metadata
    """

    def __init__(self, viewmetadata_obj: Union[bytes, str, dict] = None) -> None:
        self.document: str = ''
        self.timestamp: Optional[datetime] = None
        self.app: str = ''
        self.contains: ContainsDict = ContainsDict()
        self._required_attributes = pvector(["app", "contains"])
        super().__init__(viewmetadata_obj)

    def _deserialize(self, input_dict: dict) -> None:
        """
        Extends base ``_deserialize`` method to initialize
        ``contains`` as a dict of Contain objects.

        :param input_dict: the JSON data that defines the metadata
        :return: None
        """
        try:
            self.contains = ContainsDict(input_dict.pop('contains'))
        except KeyError:
            # means input_dict don't have `contains`, so we'll leave it empty
            pass
        super()._deserialize(input_dict)

    def _find_match_hotfix(self, key: str) -> bool:
        """
        Checks the existing types in the contains dict to see if
        the type passed in as ``key`` has the same shortname.

        FIXME: this will produce undesired results if there is a
         shortname conflict in the view.

        :param key: the type (shortname or IRI) to check
        :return: whether ``key`` already has a match in the ``contains`` dict
        """
        exists = False
        for existing_type in self.contains.keys():
            if key.split('/')[-1] == existing_type.split('/')[-1]:
                exists = True
                break
        return exists

    def new_contain(self, at_type: Union[str, ThingTypesBase], contain_dict: dict = None) -> Optional['Contain']:
        """
        Adds a new element to the ``contains`` dictionary.

        :param at_type: the ``@type`` of the annotation type being added
        :param contain_dict: any metadata associated with the annotation type
        :return: the generated :class:`Contain` object
        """
        if isinstance(at_type, ThingTypesBase):
            exists = self._find_match_hotfix(at_type.name) or self._find_match_hotfix(at_type.value)
            final_key = at_type.value
        else:
            exists = self._find_match_hotfix(at_type)
            final_key = at_type

        if not exists:
            new_contain = Contain(contain_dict)
            self.contains[final_key] = new_contain
            return new_contain


class Contain(FreezableMmifObject):
    """
    Contain object that represents the metadata of a single
    annotation type in the ``contains`` metadata of a MMIF view.

    :param contain_obj: the metadata that defines this object
    """

    def __init__(self, contain_obj: Union[bytes, str, dict] = None) -> None:
        # TODO (krim @ 8/19/20): rename `producer` to `app` maybe?
        self.producer: str = ''
        self.gen_time: Optional[datetime] = None
        super().__init__(contain_obj)

    def _deserialize(self, input_dict: dict) -> None:
        """
        Extends base ``_deserialize`` method to initialize the
        ``gen_time`` metadata as a :class:`datetime.datetime` object.

        :param input_dict: the metadata that defines this object
        :return: None
        """
        super()._deserialize(input_dict)
        if 'gen_time' in self.__dict__ and isinstance(self.gen_time, str):
            self.gen_time = dateutil.parser.isoparse(self.gen_time)


class AnnotationsList(FreezableDataList[Union[Annotation, Document]]):
    """
    AnnotationsList object that implements :class:`mmif.serialize.model.DataList`
    for :class:`mmif.serialize.annotation.Annotation`.
    """
    _items: Dict[str, Union[Annotation, Document]]

    def _deserialize(self, input_list: list) -> None:
        """
        Extends base ``_deserialize`` method to initialize ``items`` as a dict from
        annotation IDs to :class:`mmif.serialize.annotation.Annotation` objects.

        :param input_list: the JSON data that defines the list of annotations
        :return: None
        """
        self._items = {item['properties']['id']: Document(item)
                       if item['_type'].endswith("Document") else Annotation(item)
                       for item in input_list}

    def append(self, value: Union[Annotation, Document], overwrite=False) -> None:
        """
        Appends an annotation to the list.

        Fails if there is already an annotation with the same ID
        in the list, unless ``overwrite`` is set to True.

        :param value: the :class:`mmif.serialize.annotation.Annotation`
                      object to add
        :param overwrite: if set to True, will overwrite an
                          existing annotation with the same ID
        :raises KeyError: if ``overwrite`` is set to False and
                          an annotation with the same ID exists
                          in the list
        :return: None
        """
        super()._append_with_key(value.id, value, overwrite)


class ContainsDict(FreezableDataDict[Contain]):
    _items: Dict[str, Contain]

    def _deserialize(self, input_dict: dict) -> None:
        self._items = {key: Contain(value) for key, value in input_dict.items()}

    def update(self, other: Union[dict, 'ContainsDict'], overwrite=False):
        for k, v in other.items():
            self._append_with_key(k, v, overwrite=overwrite)
