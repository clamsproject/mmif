import datetime
import json
import mmif

from jsonschema import validate


class MmifObject(object):
    def __init__(self, mmif_json=None):
        if mmif_json is not None:
            self.deserialize(mmif_json)

    def serialize(self):
        return self.__dict__

    def deserialize(self, mmif):
        raise NotImplementedError()

    def __str__(self):
        return json.dumps(self.serialize(), cls=MmifObjectEncoder)

    def pretty(self):
        return json.dumps(self, indent=2, cls=MmifObjectEncoder)


class MmifObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'serialize'):
            return obj.serialize()
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class Mmif(MmifObject):
    context: str
    metadata: dict
    media: list
    contains: dict
    views: list

    def __init__(self, mmif_json=None, validate=True):
        self.context = ''
        self.metadata = {}
        self.media = []
        self.views = []
        if validate:
            self.validate(mmif_json)
        super().__init__(mmif_json)

    def serialize(self):
        d = self.__dict__.copy()
        d['@context'] = d.pop('context')
        return d

    def deserialize(self, mmif):
        in_json = json.loads(mmif)

        # TODO (krim @ 10/3/2018): more robust json parsing
        self.context = in_json["@context"]
        self.metadata = in_json["metadata"]
        self.media = in_json["media"]
        self.views = in_json["views"]

    @staticmethod
    def validate(json_str):
        # NOTE that schema file first needs to be copied to resources directory
        # this is automatically done via setup.py, so for users this shouldn't be a matter

        from pkg_resources import resource_stream
        schema = json.load(resource_stream(f'{mmif.__name__}.{mmif._res_pkg}', mmif._schema_res_name))
        validate(json.loads(json_str), schema)

    def new_view_id(self):
        return 'v_' + str(len(self.views))

    def new_view(self):
        new_view = View(self.new_view_id())
        self.views.append(new_view)
        return new_view

    def add_media(self, medium):
        try:
            self.get_medium_location(medium)
        # TODO (krim @ 10/7/2018): if get_m_location returns, raise "already exists" error
        except Exception:
            self.media.append(medium)

    def get_medium_location(self, md_type):
        for medium in self.media:
            if medium["type"] == md_type:
                return medium["location"]
        raise Exception("{} type media not found".format(md_type))

    def get_view_by_id(self, id):
        for view in self.views:
            if view.id == id:
                return view
        raise Exception("{} view not found".format(id))

    def get_view_contains(self, attype):
        return self.get_view_by_id(self.contains[attype])


class Medium(MmifObject):
    id: str
    type: str
    location: str
    metadata: dict

    def __init__(self, id, md_type='', uri=''):
        self.id = id
        self.type = md_type
        self.location = uri
        self.metadata = {}

    def deserialize(self, mmif):
        pass

    def add_metadata(self, name, value):
        self.metadata[name] = value


class Annotation(MmifObject):
    start: int
    end: int
    feature: dict
    id: str
    attype: str

    def __init__(self, id, at_type=''):
        # TODO (krim @ 10/4/2018): try deserialize "id", then if fails defaults to 0s
        super().__init__()
        self.start = 0
        self.end = 0
        self.feature = {}
        self.id = id
        self.attype = at_type

    def deserialize(self, mmif):
        pass

    def add_feature(self, name, value):
        self.feature[name] = value


class View(MmifObject):
    id: str
    contains: dict
    annotation: list

    def __init__(self, id="UNIDENTIFIED"):
        super().__init__()
        self.id = id
        self.contains = {}
        self.annotations = []

    def deserialize(self, view):
        pass

    def new_contain(self, at_type, producer=""):
        new_contain = Contain()
        new_contain.gen_time = datetime.datetime.utcnow().isoformat()
        self.contains[at_type] = new_contain
        return new_contain

    def new_annotation(self, aid):
        new_annotation = Annotation(aid)
        self.annotations.append(new_annotation)
        return new_annotation


class Contain(MmifObject):
    producer: str
    gen_time: str

    def __init__(self):
        super().__init__()
        self.producer = ''
        self.gen_time = None     # datetime.datetime

    def deserialize(self, mmif):
        pass
