import logging
import json
from datetime import datetime

from deepdiff import DeepDiff
from typing import Union, Any, Dict, Optional, TypeVar, Generic, Type

T = TypeVar('T')
__all__ = ['MmifObject', 'FreezableMmifObject', 'MmifObjectEncoder', 'DataList']


class MmifObject(object):
    """
    Abstract superclass for MMIF related key-value pair objects.
    """
    reversed_names = ['_unnamed_attributes', '_attribute_classes']
    _unnamed_attributes: Optional[dict]
    _attribute_classes: Dict[str, Type] = {}

    def __init__(self, mmif_obj: Union[str, dict] = None) -> None:
        """
        Any MMIF object can be initialized as an empty placeholder or
        an actual representation with a JSON formatted string or equivalent
        `dict` object argument.

        This superclass has two specially designed instance variables, and these
        variable names cannot be used as attribute names for MMIF objects.
        1. _unnamed_attributes
          only can be either None or an empty dictionary. If it's set to None,
          it means the class won't take any ``Additional Attributes`` in the JSON
           schema sense. If it's a dict, users can throw any k-v pairs to the
           class, EXCEPT for the reserved two key names.
        2. _attribute_classes:
          this is a dict from a key name to a specific python class to use for
          deserialize the value. Note that a key name in this dict does NOT
          have to be a *named* attribute, but is recommended to be one.
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
        if not hasattr(self, '_unnamed_attributes'):
            self._unnamed_attributes = {}
        if mmif_obj is not None:
            self.deserialize(mmif_obj)

    def disallow_additional_properties(self) -> None:
        self._unnamed_attributes = None

    def _named_attributes(self):
        return (n for n in self.__dict__.keys() if n not in self.reversed_names)

    def serialize(self, pretty: bool = False) -> str:
        """
        Generates JSON-LD representation of an object.

        :param pretty: If True, returns string representation with indentation.
        :return: JSON-LD string of the object.
        """
        return json.dumps(self._serialize(), indent=2 if pretty else None, cls=MmifObjectEncoder)

    def _serialize(self) -> Union[None, dict]:
        serializing_obj = {}
        try:
            for k, v in self._unnamed_attributes.items():   # pytype: disable=attribute-error
                if v is None:
                    continue
                if k.startswith('_'):   # _ as a placeholder ``@`` in json-ld
                    k = f'@{k[1:]}'
                serializing_obj[k] = v
        except AttributeError as e:
            # means _unnamed_attributes is None, so nothing unnamed would be serialized
            pass
        for k, v in self.__dict__.items():
            if k in self.reversed_names or self.is_empty(v):
                continue
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
        Maps JSON-LD-format MMIF strings and dicts into Python dicts
        with identifier-compliant keys. To do this, it replaces "@"
        signs in JSON-LD field names with "_" to be python-compliant.

        >>> "_type" in MmifObject._load_json('{ "@type": "some_type", "@value": "some_value"}').keys()
        True
        >>> "_value" in MmifObject._load_json('{ "@type": "some_type", "@value": "some_value"}').keys()
        True

        :param json_str:
        :return:
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
            raise TypeError("tried to load MMIF JSON in a format other than str or dict")

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
        If a subclass needs special treatment during the mapping, it needs to
        override this method.
        This defalt method won't work for generic types (e.g. List[X], Dict[X, Y]).
        For now, lists are abstracted as DataList and dicts are abstracted as XXXMedata classes.
        However, if an attribute uses a generic type (e.g. view_metadata.contains: Dict[str, Contain])
        that class should override _deserialize of its own.
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
        if key in self._named_attributes():
            self.__dict__[key] = value
        else:
            self._unnamed_attributes[key] = value   # pytype: disable=unsupported-operands

    def __getitem__(self, key) -> Union['MmifObject', str, datetime]:
        if key in self._named_attributes():
            return self.__dict__[key]
        return self._unnamed_attributes[key]


class FreezableMmifObject(MmifObject):
    reversed_names = MmifObject.reversed_names + ['_frozen']

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

    def deep_freeze(self) -> bool:
        """
        Deeply freezes this FreezableMmifObject, calling deep_freeze on all FreezableMmifObjects
        contained as attributes or members of iterable attributes.

        Note: in general, this makes no promises about the mutability of non-FreezableMmifObject
        state within the object. However, if all attributes and members of iterable attributes
        are either Freezable or hashable, this method will return True. Note that whether an object
        is hashable is not a contract of immutability but merely a suggestion, as anyone can
        implement __hash__.

        :return: True if all state is either Freezable or Hashable
        """
        self.freeze()
        fully_frozen = True

        def _freeze(attribute):
            """
            Freezes an attribute if it is Freezable; else, sets fully_frozen to False if it is mutable.
            :param attribute: the attribute to freeze
            """
            nonlocal fully_frozen
            if isinstance(attribute, FreezableMmifObject):
                attribute.deep_freeze()
            elif not hasattr(attribute, '__hash__') or attribute.__hash__ is object.__hash__:
                fully_frozen = False

        for name, attr in self.__dict__.items():
            if name not in self.reversed_names:
                _freeze(attr)
        for name in self.reversed_names:
            item = getattr(self, name)
            if isinstance(item, (dict, list, DataList)):
                for attr in item:
                    _freeze(attr)
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
        Overrides default encoding behavior to prioritize :func: MmifObject.serilize() .
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
    def __init__(self, mmif_obj: Union[str, list] = None):
        self.items: Dict[str, T] = dict()
        if mmif_obj is None:
            mmif_obj = []
        super().__init__(mmif_obj)

    def _serialize(self) -> list:
        return list(self.items.values())

    def deserialize(self, mmif_json: Union[str, list]) -> None:
        if isinstance(mmif_json, str):
            mmif_json = json.loads(mmif_json)
        self._deserialize(mmif_json)

    def get(self, key: str) -> Optional[T]:
        try:
            return self[key]
        except KeyError:
            return None

    def _append_with_key(self, key: str, value: T, overwrite=False) -> None:
        if not overwrite and key in self.items:
            raise KeyError(f"Key {key} already exists")
        else:
            self[key] = value

    def __getitem__(self, key: str):
        return self.items.__getitem__(key)

    def __setitem__(self, key: str, value: T):
        self.items.__setitem__(key, value)

    def __iter__(self):
        return self.items.values().__iter__()

    def __len__(self):
        return self.items.__len__()

    def __reversed__(self):
        return reversed(list(self.items.values()))

    def __contains__(self, item):
        return item in self.items
