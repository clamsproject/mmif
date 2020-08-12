import json
from deepdiff import DeepDiff as ddiff
from typing import Union, Any, Dict, Optional, TypeVar, Generic


T = TypeVar('T')
__all__ = ['MmifObject', 'MmifObjectEncoder', 'DataList']


class MmifObject(object):
    """
    Abstract superclass for MMIF related key-value pair objects.
    """

    def __init__(self, mmif_obj: Union[str, dict] = None):
        """
        Any MMIF object can be initialized as an empty placeholder or
        an actual representation with a JSON formatted string or equivalent
        `dict` object argument.

        :param mmif_obj: JSON string or `dict` to initialize an object.
         If not given, an empty object will be initialized, sometimes with
         an ID value automatically generated, based on its parent object.
        """
        if mmif_obj is not None:
            self.deserialize(mmif_obj)

    def serialize(self, pretty: bool = False) -> str:
        """
        Generates JSON-LD representation of an object.

        :param pretty: If True, returns string representation with indentation.
        :return: JSON-LD string of the object.
        """
        return json.dumps(self._serialize(), indent=2 if pretty else None, cls=MmifObjectEncoder)

    def _serialize(self) -> dict:
        d = {}
        for k, v in list(self.__dict__.items()):
            # ignore all "null" values including empty dicts and zero strings
            if v is not None and len(v) if hasattr(v, '__len__') else len(str(v)) > 0:
                if k.startswith('_'): # _ as a placeholder ``@`` in json-ld
                    d[f'@{k[1:]}'] = v
                else:
                    d[k] = v
        return d

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
        def to_atsign(d: Dict[str, Any]) -> dict:
            for k in list(d.keys()):
                if k.startswith('@'):
                    d[f'_{k[1:]}'] = d.pop(k)
            return d

        def traverse_to_atsign(d: dict) -> dict:
            new_d = d.copy()
            to_atsign(new_d)
            for key, value in new_d.items():
                if type(value) is dict:
                    new_d[key] = traverse_to_atsign(value)
            return new_d

        if type(json_obj) is dict:
            return traverse_to_atsign(json_obj)
        elif type(json_obj) is str:
            return json.loads(json_obj, object_hook=to_atsign)
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
        :param input_dict:
        :return:
        """
        self.__dict__ = input_dict

    def __str__(self):
        return self.serialize(False)

    def pretty(self) -> str:
        """
        Call :func: .serialize() with indentation.
        """
        return self.serialize(True)

    def __eq__(self, other):
        return isinstance(other, type(self)) and len(ddiff(self, other, ignore_order=True, report_repetition=True)) ==0

    def __len__(self):
        return len(self.__dict__)


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
        elif hasattr(obj, 'isoformat'): # for datetime objects
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
