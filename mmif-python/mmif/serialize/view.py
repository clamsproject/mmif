"""
The :mod:`view` module contains the classes used to represent a MMIF view
as a live Python object.

In MMIF, views are created by apps in a pipeline that are annotating
data that was previously present in the MMIF file.
"""

from datetime import datetime
from typing import Dict, Union, Optional
import dateutil.parser

from .annotation import Annotation
from .model import MmifObject, DataList
from mmif.vocabulary import AnnotationTypesBase


__all__ = ['View', 'ViewMetadata', 'Contain']


class View(MmifObject):
    """
    View object that represents a single view in a MMIF file.

    A view is identified by an ID, and contains certain metadata,
    a list of annotations, and potentially a JSON-LD ``@context``
    IRI.

    If ``view_obj`` is not provided, an empty View will be generated.

    :param view_obj: the JSON data that defines the view
    """

    def __init__(self, view_obj: Union[str, dict] = None) -> None:
        self._context: str = ''
        self.id: str = ''
        self.metadata: ViewMetadata = ViewMetadata()
        self.annotations: AnnotationsList = AnnotationsList()
        self.disallow_additional_properties()
        self._attribute_classes = {
            'metadata': ViewMetadata,
            'annotations': AnnotationsList
        }
        super().__init__(view_obj)

    def new_contain(self, at_type: Union[str, AnnotationTypesBase], contain_dict: dict = None) -> Optional['Contain']:
        """
        Adds a new element to the ``contains`` metadata.

        :param at_type: the ``@type`` of the annotation type being added
        :param contain_dict: any metadata associated with the annotation type
        :return: the generated :class:`Contain` object
        """
        return self.metadata.new_contain(at_type, contain_dict)

    def new_annotation(self, aid: str, at_type: Union[str, AnnotationTypesBase], overwrite=False) -> 'Annotation':
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

    def __getitem__(self, key: str) -> 'Annotation':
        """
        getitem implementation for View.

        >>> obj = View('''{"id": "v1","metadata": {"contains": {"BoundingBox": {"unit": "pixels"}},"medium": "m1","tool": "http://tools.clams.io/east/1.0.4"},"annotations": [{"@type": "BoundingBox","properties": {"id": "bb1","coordinates": [[90,40], [110,40], [90,50], [110,50]] }}]}''')
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


class ViewMetadata(MmifObject):
    """
    ViewMetadata object that represents the ``metadata`` object within a MMIF view.

    :param viewmetadata_obj: the JSON data that defines the metadata
    """

    def __init__(self, viewmetadata_obj: Union[str, dict] = None) -> None:
        self.medium: str = ''
        self.timestamp: Optional[datetime] = None
        self.app: str = ''
        self.contains: Dict[str, Contain] = {}
        super().__init__(viewmetadata_obj)

    def _deserialize(self, input_dict: dict) -> None:
        """
        Extends base ``_deserialize`` method to initialize
        ``contains`` as a dict of Contain objects.

        :param input_dict: the JSON data that defines the metadata
        :return: None
        """
        try:
            self.contains = {at_type: Contain(contain_obj)
                             for at_type, contain_obj in input_dict.pop('contains').items()}
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

    def new_contain(self, at_type: Union[str, AnnotationTypesBase], contain_dict: dict = None) -> Optional['Contain']:
        """
        Adds a new element to the ``contains`` dictionary.

        :param at_type: the ``@type`` of the annotation type being added
        :param contain_dict: any metadata associated with the annotation type
        :return: the generated :class:`Contain` object
        """
        if isinstance(at_type, AnnotationTypesBase):
            exists = self._find_match_hotfix(at_type.name) or self._find_match_hotfix(at_type.value)
            final_key = at_type.value
        else:
            exists = self._find_match_hotfix(at_type)
            final_key = at_type

        if not exists:
            new_contain = Contain(contain_dict)
            new_contain.gen_time = datetime.now()
            self.contains[final_key] = new_contain
            return new_contain


class Contain(MmifObject):
    """
    Contain object that represents the metadata of a single
    annotation type in the ``contains`` metadata of a MMIF view.

    :param contain_obj: the metadata that defines this object
    """

    def __init__(self, contain_obj: Union[str, dict] = None) -> None:
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


class AnnotationsList(DataList[Annotation]):
    """
    AnnotationsList object that implements :class:`mmif.serialize.model.DataList`
    for :class:`mmif.serialize.annotation.Annotation`.
    """
    items: Dict[str, Annotation]

    def _deserialize(self, input_list: list) -> None:
        """
        Extends base ``_deserialize`` method to initialize ``items`` as a dict from
        annotation IDs to :class:`mmif.serialize.annotation.Annotation` objects.

        :param input_list: the JSON data that defines the list of annotations
        :return: None
        """
        self.items = {item['properties']['id']: Annotation(item) for item in input_list}

    def append(self, value: Annotation, overwrite=False) -> None:
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
