import datetime
import json
from pkg_resources import resource_stream
from jsonschema import validate

import mmif


class MmifObject(object):
    def __init__(self, mmif_json=None):
        if mmif_json is not None:
            self.deserialize(json.loads(mmif_json))

    def serialize(self):
        return self.__dict__

    def deserialize(self, mmif_obj_dict):
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

    def deserialize(self, mmif_dict):

        # TODO (krim @ 10/3/2018): more robust json parsing
        self.context = mmif_dict["@context"]
        self.metadata = mmif_dict["metadata"]
        self.media = mmif_dict["media"]
        self.views = mmif_dict["views"]

    @staticmethod
    def validate(json_str):
        # NOTE that schema file first needs to be copied to resources directory
        # this is automatically done via setup.py, so for users this shouldn't be a matter

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

    def deserialize(self, medium_dict):
        pass

    def add_metadata(self, name, value):
        self.metadata[name] = value


class Annotation(MmifObject):
    feature: dict
    id: str
    at_type: str

    def __init__(self, anno_dict):
        super().__init__(anno_dict)
        self.feature = {}

    def deserialize(self, anno_dict):
        """
        "annotations": [
          {
            "@type": "BoundingBox",
            "properties": {
              "id": "bb1",
              "coordinates": [[90,40], [110,40], [90,50], [110,50]] }
          }
        ]
        """
        self.at_type = anno_dict['@type']
        self.feature.update(anno_dict['properties'])
        self.id = self.feature.pop('id')

    def add_feature(self, name, value):
        self.feature[name] = value


class View(MmifObject):
    id: str
    contains: dict
    annotations: list
    anno_ids = set()

    def __init__(self, id="UNIDENTIFIED"):
        super().__init__()
        self.id = id
        self.contains = {}
        self.annotations = []

    def deserialize(self, view_dict):
        self.id = view_dict['id']
        for contain, metadata in view_dict['metadata']['contains'].items():
            self.new_contain(contain)
        for anno_dict in view_dict['annotations']:
            self.add_annotation(anno_dict)

    def new_contain(self, at_type, producer=""):
        new_contain = Contain()
        new_contain.gen_time = datetime.datetime.utcnow().isoformat()
        self.contains[at_type] = new_contain
        return new_contain

    def new_annotation(self, aid, at_type='Annotation'):
        new_annotation = Annotation('{ "@type" = "%s", "properties": { "id": "%s" }}' % (at_type, aid))
        self.annotations.append(new_annotation)
        self.anno_ids.add(aid)
        return new_annotation

    def add_annotation(self, anno_dict):
        new_annotation = Annotation(anno_dict)
        self.annotations.append(new_annotation)
        self.anno_ids.add(new_annotation.id)
        return new_annotation


class Contain(MmifObject):
    producer: str
    gen_time: str

    def __init__(self):
        super().__init__()
        self.producer = ''
        self.gen_time = None     # datetime.datetime

    def deserialize(self, contain_dict):
        pass
