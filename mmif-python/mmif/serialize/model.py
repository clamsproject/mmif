import json
from typing import Union, Any, Dict


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
        if type(mmif_obj) == str:
            mmif_obj = json.loads(mmif_obj)
        if mmif_obj is not None:
            self.deserialize(mmif_obj)

    def serialize(self, pretty: bool = False) -> str:
        """
        Generates JSON-LD representation of an object.

        :param pretty: If True, returns string representation with indentation.
        :return: JSON-LD string of the object.
        """
        return self._serialize(self.__dict__, pretty)

    @staticmethod
    def _serialize(kv_obj: dict, pretty: bool = False) -> str:
        for k in list(kv_obj.keys()):
            if k.startswith('_'):
                kv_obj[f'@{k[1:]}'] = kv_obj.pop(k)
        return json.dumps(kv_obj, indent=2 if pretty else None, cls=MmifObjectEncoder)

    @staticmethod
    def _load_str(json_str: str):
        """
        Turns JSON-format string into python dict. In doing so, it replaces "@"
        signs in JSON-LD field names with "_" to be python-compliant.

        >>> "_type" in MmifObject._load_str('{ "@type": "some_type", "@value": "some_value"}').keys()
        True
        >>> "_value" in MmifObject._load_str('{ "@type": "some_type", "@value": "some_value"}').keys()
        True

        :param json_str:
        :return:
        """
        def to_atsign(d: Dict[str, Any]):
            for k in d:
                if k.startswith('@'):
                    d[f'_{k[1:]}'] = d.pop(k)
            return d
        return json.loads(json_str, object_hook=to_atsign)

    def deserialize(self, mmif_json: Union[str, dict]) -> None:
        """
        Takes a JSON-formatted string or a simple `dict` json-loaded from
        such a string as an input and populates object's fields with the values
        specified in the input.

        :param mmif_json: JSON-formatted string or dict from such a string
         that represents a MMIF object
        """
        if type(mmif_json) == str:
            mmif_json = self._load_str(mmif_json)
        self._deserialize(mmif_json)

    def _deserialize(self, input_dict: dict) -> None:
        raise NotImplementedError()

    def __str__(self):
        return self.serialize(False)

    def pretty(self) -> str:
        """
        Call :func: .serialize() with indentation.
        """
        return self.serialize(True)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class MmifObjectEncoder(json.JSONEncoder):
    """
    Encoder class to define behaviors of de-/serialization
    """

    def default(self, obj: MmifObject):
        """
        Overrides default encoding behavior to prioritize :func: MmifObject.serilize() .
        """
        if hasattr(obj, 'serialize'):
            return obj.serialize()
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)
