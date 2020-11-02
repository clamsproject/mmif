"""
The :mod:`model` module contains the classes used to represent an
abstract MMIF object as a live Python object.

The :class:`MmifObject` class or one of its derivatives is subclassed by
all other classes defined in this SDK, except for :class:`MmifObjectEncoder`.

These objects are generally instantiated from JSON, either as a string
or as an already-loaded Python dictionary. This base class provides the
core functionality for deserializing MMIF JSON data into live objects
and serializing live objects into MMIF JSON data. Specialized behavior
for the different components of MMIF is added in the subclasses.
"""

import logging
import json
from pyrsistent import pvector, m, pmap, s, PVector, PMap, PSet, thaw
from datetime import datetime

from deepdiff import DeepDiff
from typing import Union, Any, Dict, Optional, TypeVar, Generic, Type, Generator, Iterator, List

T = TypeVar('T')

__all__ = [
    'MmifObject',
    'FreezableMmifObject',
    'MmifObjectEncoder',
    'DataList',
    'DataDict',
    'FreezableDataList',
    'FreezableDataDict'
]


class MmifObject(object):
    """
    Abstract superclass for MMIF related key-value pair objects.

    Any MMIF object can be initialized as an empty placeholder or
    an actual representation with a JSON formatted string or equivalent
    `dict` object argument.

    This superclass has three specially designed instance variables, and these
    variable names cannot be used as attribute names for MMIF objects.

    1. _unnamed_attributes:
       Only can be either None or an empty dictionary. If it's set to None,
       it means the class won't take any ``Additional Attributes`` in the JSON
       schema sense. If it's a dict, users can throw any k-v pairs to the
       class, EXCEPT for the reserved two key names.
    2. _attribute_classes:
       This is a dict from a key name to a specific python class to use for
       deserialize the value. Note that a key name in this dict does NOT
       have to be a *named* attribute, but is recommended to be one.
    3. _required_attributes:
       This is a simple list of names of attributes that are required in the object.
       When serialize, an object will skip its *empty* (e.g. zero-length, or None)
       attributes unless they are in this list. Otherwise, the serialized JSON
       string would have empty representations (e.g. ``""``, ``[]``).

    # TODO (krim @ 8/17/20): this dict is however, a duplicate with the type hints in the class definition.
    Maybe there is a better way to utilize type hints (e.g. getting them as a programmatically), but for now
    developers should be careful to add types to hints as well as to this dict.

    Also note that those two special attributes MUST be set in the __init__()
    before calling super method, otherwise deserialization will not work.

    And also, a subclass that has one or more *named* attributes, it must
    set those attributes in the __init__() before calling super method. When
    serializing a MmifObject, all *empty* attributes will be ignored, so for
    optional named attributes, you must leave leave the values empty, but
    NOT None. Any None-valued named attributes will cause issues with current
    implementation.

    :param mmif_obj: JSON string or `dict` to initialize an object.
     If not given, an empty object will be initialized, sometimes with
     an ID value automatically generated, based on its parent object.
    """
    
    reserved_names: PSet = s('reserved_names',
                             '_unnamed_attributes',
                             '_attribute_classes',
                             '_required_attributes',
                             # used in freezable subclasses
                             '_frozen',
                             # used in Document class to store parent view id
                             '_parent_view_id')
    _unnamed_attributes: Optional[dict]
    _attribute_classes: PMap = m()  # Mapping: str -> Type
    _required_attributes: PVector

    def __init__(self, mmif_obj: Union[bytes, str, dict] = None) -> None:
        if isinstance(mmif_obj, bytes):
            mmif_obj = mmif_obj.decode('utf8')
        if not hasattr(self, '_required_attributes'):
            self._required_attributes = pvector()
        if not hasattr(self, '_unnamed_attributes'):
            self._unnamed_attributes = {}
        if mmif_obj is not None:
            self.deserialize(mmif_obj)

    def disallow_additional_properties(self) -> None:
        """
        Call this method in :func:`__init__` to prevent the insertion
        of unnamed attributes after initialization.
        """
        self._unnamed_attributes = None

    def set_additional_property(self, key: str, value: Any) -> None:
        """
        Method to set values in _unnamed_attributes.
        :param key: the attribute name
        :param value: the desired value
        :return: None
        :raise: AttributeError if additional properties are disallowed
                by :func:`disallow_additional_properties`
        """
        if self._unnamed_attributes is None:
            raise AttributeError(f"Additional properties are disallowed by {self.__class__}")
        self._unnamed_attributes[key] = value # pytype: disable=unsupported-operands

    def _named_attributes(self) -> Generator[str, None, None]:
        """
        Returns a generator of the names of all of this object's named attributes.

        :return: generator of names of all named attributes
        """
        return (n for n in self.__dict__.keys() if n not in self.reserved_names)

    def serialize(self, pretty: bool = False) -> str:
        """
        Generates JSON representation of an object.

        :param pretty: If True, returns string representation with indentation.
        :return: JSON string of the object.
        """
        return json.dumps(self._serialize(), indent=2 if pretty else None, cls=MmifObjectEncoder)

    def _serialize(self, alt_container: Dict = None) -> dict:
        """
        Maps a MMIF object to a plain python dict object,
        rewriting internal keys that start with '_' to
        start with '@' per the JSON-LD schema.

        If a subclass needs special treatment during the mapping, it needs to
        override this method.

        :return: the prepared dictionary
        """
        container = alt_container if alt_container is not None else self._unnamed_attributes
        serializing_obj = {}
        try:
            for k, v in container.items():   # pytype: disable=attribute-error
                if v is None:
                    continue
                if isinstance(v, (PSet, PVector, PMap)):
                    v = thaw(v)
                if k.startswith('_'):   # _ as a placeholder ``@`` in json-ld
                    k = f'@{k[1:]}'
                serializing_obj[k] = v
        except AttributeError as e:
            # means _unnamed_attributes is None, so nothing unnamed would be serialized
            pass
        for k, v in self.__dict__.items():
            if k in self.reserved_names:
                continue
            if k not in self._required_attributes and self.is_empty(v):
                continue
            if isinstance(v, (PSet, PVector, PMap)):
                v = thaw(v)
            if k.startswith('_'):       # _ as a placeholder ``@`` in json-ld
                k = f'@{k[1:]}'
            serializing_obj[k] = v
        return serializing_obj

    @staticmethod
    def is_empty(obj) -> bool:
        """
        return True if the obj is None or "emtpy". The emptiness first defined as
        having zero length. But for objects that lack __len__ method, we need
        additional check.
        """
        if obj is None:
            return True
        if hasattr(obj, '__len__') and len(obj) == 0:
            return True
        return False

    @staticmethod
    def _load_json(json_obj: Union[dict, str]) -> dict:
        """
        Maps JSON-format MMIF strings and dicts into Python dicts
        with identifier-compliant keys. To do this, it replaces "@"
        signs in JSON-LD field names with "_" to be python-compliant.

        >>> "_type" in MmifObject._load_json('{ "@type": "some_type", "@value": "some_value"}').keys()
        True
        >>> "_value" in MmifObject._load_json('{ "@type": "some_type", "@value": "some_value"}').keys()
        True

        :param json_str: the JSON data to load and process
        :return: the mapped data as a dict
        """
        def from_atsign(d: Dict[str, Any]) -> dict:
            for k in list(d.keys()):
                if k.startswith('@'):
                    d[f'_{k[1:]}'] = d.pop(k)
            return d

        def deep_from_atsign(d: dict) -> dict:
            new_d = d.copy()
            from_atsign(new_d)
            for key, value in new_d.items():
                if type(value) is dict:
                    new_d[key] = deep_from_atsign(value)
            return new_d

        if type(json_obj) is dict:
            return deep_from_atsign(json_obj)
        elif type(json_obj) is str:
            return json.loads(json_obj, object_hook=from_atsign)
        else:
            raise TypeError(f"tried to load MMIF JSON in a format other than str or dict: {type(json_obj)}")

    def deserialize(self, mmif_json: Union[str, dict]) -> None:
        """
        Takes a JSON-formatted string or a simple `dict` that's json-loaded from
        such a string as an input and populates object's fields with the values
        specified in the input.

        :param mmif_json: JSON-formatted string or dict from such a string
         that represents a MMIF object
        """
        mmif_json = self._load_json(mmif_json)
        self._deserialize(mmif_json)

    def _deserialize(self, input_dict: dict) -> None:
        """
        Maps a plain python dict object to a MMIF object.
        If a subclass needs a special treatment during the mapping, it needs to
        override this method.

        This default method won't work for generic types (e.g. List[X], Dict[X, Y]).
        For now, lists are abstracted as DataList and dicts are abstracted as XXXMedata classes.
        However, if an attribute uses a generic type (e.g. view_metadata.contains: Dict[str, Contain])
        that class should override _deserialize of its own.

        :param input_dict: the prepared JSON data that defines the object
        """
        for k, v in input_dict.items():
            if self._attribute_classes and k in self._attribute_classes:
                self[k] = self._attribute_classes[k](v)
            else:
                self[k] = v

    def __str__(self) -> str:
        return self.serialize(False)

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and \
               len(DeepDiff(self, other, ignore_order=True, report_repetition=True, exclude_types=[datetime])) == 0

    def __len__(self) -> int:
        return sum([not self.is_empty(self[named]) for named in self._named_attributes()]) \
               + (len(self._unnamed_attributes) if self._unnamed_attributes else 0)

    def __setitem__(self, key, value) -> None:
        if key in self.reserved_names:
            raise KeyError("can't set item on a reserved name")
        if key in self._named_attributes():
            if self._attribute_classes and key in self._attribute_classes \
                    and not isinstance(value, (self._attribute_classes[key])):
                self.__dict__[key] = self._attribute_classes[key](value)
            else:
                self.__dict__[key] = value
        else:
            if self._attribute_classes and key in self._attribute_classes \
                    and not isinstance(value, (self._attribute_classes[key])):
                self.set_additional_property(key, self._attribute_classes[key](value))
            else:
                self.set_additional_property(key, value)

    def __getitem__(self, key) -> Union['MmifObject', str, datetime]:
        if key in self._named_attributes():
            return self.__dict__[key]
        if self._unnamed_attributes is None:
            raise AttributeError(f"Additional properties are disallowed by {self.__class__}")
        return self._unnamed_attributes[key]


class FreezableMmifObject(MmifObject):

    def __init__(self, *args, **kwargs) -> None:
        self._frozen = False
        super().__init__(*args, **kwargs)

    def is_frozen(self):
        return self._frozen

    def freeze(self) -> None:
        """
        Shallowly freezes this FreezableMmifObject, preventing attribute assignments with `=`.
        Makes no promises about the mutability of state within the object, only the references
        to that state.

        :return: asdf
        """
        self._frozen = True

    def deep_freeze(self, *additional_containers: str) -> bool:
        """
        Deeply freezes this FreezableMmifObject, calling deep_freeze on all FreezableMmifObjects
        contained as attributes or members of iterable attributes.

        Note: in general, this makes no promises about the mutability of non-FreezableMmifObject
        state within the object. However, if all attributes and members of iterable attributes
        are either Freezable or hashable, this method will return True. Note that whether an object
        is hashable is not a contract of immutability but merely a suggestion, as anyone can
        implement __hash__.

        :param additional_containers: any names of attributes in the object that should have
                                      their contents frozen but not themselves. This is only
                                      used for FreezableDataList and FreezableDataDict classes
                                      to freeze their contents.
        :return: True if all state is either Freezable or Hashable
        """
        fully_frozen = True

        def _pyrsist(element):
            nonlocal fully_frozen

            if isinstance(element, (list, PVector)):
                return pvector(_pyrsist(item) for item in element)
            elif isinstance(element, (dict, PMap)):
                return pmap({key: _pyrsist(value) for key, value in element.items()})
            elif isinstance(element, FreezableMmifObject):
                fully_frozen &= element.deep_freeze()
                return element
            elif element is not None and (not hasattr(element, '__hash__')
                                          or element.__class__.__hash__ in {object.__hash__, None}):
                # element is most likely mutable and not freezable
                fully_frozen = False
                return element
            else:
                # element is most likely immutable
                return element

        # freeze unnamed attributes if there are any
        if hasattr(self, '_unnamed_attributes') and self._unnamed_attributes is not None:
            self._unnamed_attributes = _pyrsist(self._unnamed_attributes)

        # freeze named attributes
        for name in self._named_attributes():
            self.__setattr__(name, _pyrsist(self.__getattribute__(name)))

        # freeze additional containers passed in (currently only used for DataLists and DataDicts
        # to freeze contents of _items without destroying insertion order by converting to a PMap)
        for name in additional_containers:
            container = self.__getattribute__(name)
            if isinstance(container, dict):
                iter_pairs = container.items()
            elif isinstance(container, list):
                iter_pairs = enumerate(container)
            else:
                raise ValueError("additional_containers should only be of types dict or list")
            for key, value in iter_pairs:
                container[key] = _pyrsist(value)

        self.freeze()

        return fully_frozen

    def __setattr__(self, name, value) -> None:
        """
        Overrides object.__setattr__(self, name, value) to prevent
        attribute assignment if the object has been frozen.

        :param name: the attribute name
        :param value: the desired value
        """
        if '_frozen' not in self.__dict__ or not self._frozen:
            object.__setattr__(self, name, value)
        else:
            raise TypeError("frozen FreezableMmifObject should be immutable")

    def __setitem__(self, key, value):
        """
        Overrides the __setitem__ method of  to
        prevent item assignment if the object has been frozen.

        :param key: t
        :param value:
        :return:
        """
        if '_frozen' not in self.__dict__ or not self._frozen:
            setitem = super().__setitem__
            if logging.getLogger().level == logging.DEBUG:
                logging.debug(setitem)
            setitem(key, value)
        else:
            raise TypeError("frozen FreezableMmifObject should be immutable")


class MmifObjectEncoder(json.JSONEncoder):
    """
    Encoder class to define behaviors of de-/serialization
    """

    def default(self, obj: 'MmifObject'):
        """
        Overrides default encoding behavior to prioritize :func:`MmifObject.serialize()`.
        """
        if hasattr(obj, '_serialize'):
            return obj._serialize()
        elif hasattr(obj, 'isoformat'):         # for datetime objects
            return obj.isoformat()
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class DataList(MmifObject, Generic[T]):
    """
    The DataList class is an abstraction that represents the
    various lists found in a MMIF file, such as documents, subdocuments,
    views, and annotations.

    :param Union[str, list] mmif_obj: the data that the list contains
    """
    def __init__(self, mmif_obj: Union[bytes, str, list] = None):
        self.reserved_names = self.reserved_names.add('_items')
        self._items: Dict[str, T] = dict()
        self.disallow_additional_properties()
        if mmif_obj is None:
            mmif_obj = []
        super().__init__(mmif_obj)

    def _serialize(self, *args, **kwargs) -> list:
        """
        Internal serialization method. Returns a list.

        :return: list of the values of the internal dictionary.
        """
        return list(super()._serialize(self._items).values())

    def deserialize(self, mmif_json: Union[str, list]) -> None:
        """
        Passes the input data into the internal deserializer.
        """
        super().deserialize(mmif_json)  # pytype: disable=unsupported-operands

    @staticmethod
    def _load_json(json_list: Union[list, str]) -> list:
        if type(json_list) is str:
            json_list = json.loads(json_list)
        return [MmifObject._load_json(obj) for obj in json_list]
    
    def _deserialize(self, input_list: dict) -> None:
        raise NotImplementedError()

    def get(self, key: str) -> Optional[T]:
        """
        Standard dictionary-style get() method, albeit with no ``default``
        parameter. Relies on the implementation of __getitem__.

        Will return ``None`` if the key is not found.

        :param key: the key to search for
        :return: the value matching that key
        """
        try:
            return self[key]
        except KeyError:
            return None

    def _append_with_key(self, key: str, value: T, overwrite=False) -> None:
        """
        Internal method for appending a key-value pair. Subclasses should
        implement an append() method that extracts a key from the list data
        or generates a key programmatically (such as an index), depending
        on the data type.

        :param key: the desired key to append
        :param value: the value associated with the key
        :param overwrite: if set to True, will overwrite an existing K-V pair
         if the key already exists. Otherwise, raises a KeyError.
        :raise KeyError: if ``overwrite`` is False and the ``key`` is already
         present in the DataList.
        :return: None
        """
        if not overwrite and key in self._items:
            raise KeyError(f"Key {key} already exists")
        else:
            self[key] = value

    def append(self, value, overwrite):
        raise NotImplementedError()

    def __getitem__(self, key: str) -> T:
        if key not in self.reserved_names:
            return self._items.__getitem__(key)
        else:
            raise KeyError("Don't use __getitem__ to access a reserved name")

    def __setitem__(self, key: str, value: T):
        if key not in self.reserved_names:
            self._items.__setitem__(key, value)
        else:
            super().__setitem__(key, value)

    def __iter__(self) -> Iterator[T]:
        return self._items.values().__iter__()

    def __len__(self) -> int:
        return self._items.__len__()

    def __reversed__(self) -> Iterator[T]:
        return reversed(list(self._items.values()))

    def __contains__(self, item) -> bool:
        return item in self._items


class FreezableDataList(FreezableMmifObject, DataList[T]):
    def _deserialize(self, input_dict: dict) -> None:
        raise NotImplementedError()

    def deep_freeze(self, *args, **kwargs) -> bool:
        return super().deep_freeze('_items')


class DataDict(MmifObject, Generic[T]):
    def __init__(self, mmif_obj: Union[bytes, str, dict] = None):
        self.reserved_names = self.reserved_names.add('_items')
        self._items: Dict[str, T] = dict()
        self.disallow_additional_properties()
        if mmif_obj is None:
            mmif_obj = {}
        super().__init__(mmif_obj)

    def _serialize(self, *args, **kwargs) -> dict:
        return super()._serialize(self._items)

    def _deserialize(self, input_dict: dict) -> None:
        raise NotImplementedError()

    def get(self, key: str) -> Optional[T]:
        return self._items.get(key)

    def _append_with_key(self, key: str, value: T, overwrite=False) -> None:
        if not overwrite and key in self._items:
            raise KeyError(f"Key {key} already exists")
        else:
            self[key] = value

    def update(self, other, overwrite):
        raise NotImplementedError()

    def items(self):
        return self._items.items()

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def __getitem__(self, key: str) -> T:
        if key not in self.reserved_names:
            return self._items.__getitem__(key)
        else:
            raise KeyError("Don't use __getitem__ to access a reserved name")

    def __setitem__(self, key: str, value: T):
        if key not in self.reserved_names:
            self._items.__setitem__(key, value)
        else:
            super().__setitem__(key, value)

    def __iter__(self):
        return self._items.__iter__()

    def __len__(self):
        return self._items.__len__()

    def __contains__(self, item):
        return item in self._items


class FreezableDataDict(FreezableMmifObject, DataDict[T]):
    def _deserialize(self, input_dict: dict) -> None:
        raise NotImplementedError()

    def deep_freeze(self, *args, **kwargs) -> bool:
        return super().deep_freeze('_items')
