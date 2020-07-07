import datetime
import json
from typing import List, Union, Dict
from pkg_resources import resource_stream
from jsonschema import validate

import mmif # pytype: disable=pyi-error


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
        return json.dumps(kv_obj, indent=2 if pretty else None, cls=MmifObjectEncoder)

    def deserialize(self, mmif_json: Union[str, dict]) -> None:
        """
        Takes a JSON-formatted string or a simple `dict` json-loaded from
        such a string as an input and populates object's fields with the values
        specified in the input.

        :param mmif_json: JSON-formatted string or dict from such a string
         that represents a MMIF object
        """
        if type(mmif_json) == str:
            mmif_json = json.loads(mmif_json)
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


class Mmif(MmifObject):
    # TODO (krim @ 7/6/20): maybe need IRI/URI as a python class for typing?
    context: str
    metadata: Dict[str, str]
    media: List['Medium']
    # this contains is different from contains field in view, in that this is only for sniffing purpose
    # and has view ids only
    # TODO (krim @ 7/7/20): should these lists be sorted? default behavior of `get_view_contains` would be
    # returning the latest view, so the list should sorted by generation timestamp, I guess.
    contains: Dict[str, List[str]]
    views: List['View']

    def __init__(self, mmif_obj: Union[str, dict] = None, validate: bool = True):
        self.context = ''
        self.metadata = {}
        self.media = []
        self.views = []
        if validate:
            self.validate(mmif_obj)
        super().__init__(mmif_obj)

    def serialize(self, pretty: bool =False) -> str:
        """
        Overrides the default `serialize` to add `@` sign to context field.
        """
        d = self.__dict__.copy()
        d['@context'] = d.pop('context')
        return self._serialize(d, pretty)

    def _deserialize(self, mmif_dict: dict):

        # TODO (krim @ 10/3/2018): more robust json parsing
        self.context = mmif_dict["@context"]
        self.metadata = mmif_dict["metadata"]
        self.media = mmif_dict["media"]
        self.views = mmif_dict["views"]

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

    def add_media(self, medium: 'Medium'):
        try:
            self.get_medium_location(medium.type)
        # TODO (krim @ 10/7/2018): if get_m_location returns, raise "already exists" error
        except Exception:
            self.media.append(medium)

    def get_medium_location(self, md_type: str):
        for medium in self.media:
            if medium["type"] == md_type:
                return medium["location"]
        raise Exception("{} type media not found".format(md_type))

    def get_view_by_id(self, id: str):
        for view in self.views:
            if view.id == id:
                return view
        raise Exception("{} view not found".format(id))

    def get_view_contains(self, at_type: str):
        return self.get_view_by_id(self.contains[at_type][-1])


class Medium(MmifObject):
    id: str
    type: str
    location: str
    metadata: Dict[str, str]

    def __init__(self, medium_obj: Union[str, dict] = None):
        self.id = ''
        self.type = ''
        self.location = ''
        self.metadata = {}
        super().__init__(medium_obj)

    def _deserialize(self, medium_dict: dict):
        # TODO (krim @ 7/7/20): implement this when `medium` specs are more concrete
        pass

    def add_metadata(self, name: str, value: str):
        self.metadata[name] = value


class Annotation(MmifObject):
    properties: Dict[str, str]
    id: str
    at_type: str

    def __init__(self, anno_obj: Union[str, dict] = None):
        self.id = ''
        self.at_type = ''
        self.properties = {}
        super().__init__(anno_obj)

    def _deserialize(self, anno_dict: dict):
        self.at_type = anno_dict['@type']
        self.properties.update(anno_dict['properties'])
        self.id = self.properties.pop('id')

    def serialize(self, pretty: bool = False) -> str:
        self.add_property('id', self.__dict__.pop('id'))
        return self._serialize(self.__dict__)

    def add_property(self, name: str, value: str):
        self.properties[name] = value


class View(MmifObject):
    id: str
    contains: Dict[str, 'Contain']
    annotations: List[Annotation]
    anno_ids = set()

    def __init__(self, view_obj: Union[str, dict] = None):
        self.id = ''
        self.contains = {}
        self.annotations = []
        super().__init__(view_obj)

    def _deserialize(self, view_dict: dict):
        self.id = view_dict['id']
        for at_type, contain in view_dict['metadata']['contains'].items():
            self.new_contain(at_type, contain['producer'])
        for anno_dict in view_dict['annotations']:
            self.add_annotation(Annotation(anno_dict))

    def new_contain(self, at_type: str, producer: str):
        new_contain = Contain()
        new_contain.producer = producer
        new_contain.gen_time = datetime.datetime.utcnow().isoformat()
        self.contains[at_type] = new_contain
        return new_contain

    def new_annotation(self, aid: str, at_type: str):
        new_annotation = Annotation()
        new_annotation.at_type = at_type
        new_annotation.id = aid
        return self.add_annotation(new_annotation)

    def add_annotation(self, annotation: 'Annotation') -> 'Annotation':
        self.annotations.append(annotation)
        self.anno_ids.add(annotation.id)
        return annotation


class Contain(MmifObject):
    producer: str
    gen_time: str

    def __init__(self, contain_obj: Union[str, dict] = None):
        self.producer = ''
        self.gen_time = None     # datetime.datetime
        super().__init__(contain_obj)

    def _deserialize(self, contain_dict: dict):
        pass
