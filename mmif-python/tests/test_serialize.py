import unittest
import json

import mmif
from hypothesis import given, strategies as st, settings, HealthCheck
import hypothesis_jsonschema

import pytest
from jsonschema import ValidationError
from mmif.serialize import Mmif, Annotation, View
from pkg_resources import resource_stream

from tests.mmif_examples import *


class TestMmif(unittest.TestCase):

    def setUp(self) -> None:
        self.mmif_json: dict = json.loads(example1)

    def test_mmif_deserialize(self):
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = Mmif(json_str)
        except ValidationError as ve:
            self.fail(ve.message)
        self.assertEqual(mmif_obj, Mmif(mmif_obj.serialize()))

    def test_bad_mmif_deserialize_no_context(self):
        self.mmif_json.pop('@context')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_metadata(self):
        self.mmif_json.pop('metadata')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_media(self):
        self.mmif_json.pop('media')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_views(self):
        self.mmif_json.pop('views')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_medium_cannot_have_text_and_location(self):
        mmif = Mmif(json.dumps(self.mmif_json))
        m1 = mmif.get_medium_by_id('m1')
        m2 = mmif.get_medium_by_id('m2')
        m1.text = m2.text
        with pytest.raises(ValidationError) as ve:
            Mmif(mmif.serialize())
            assert "validating 'oneOf'" in ve.value

    def test___getitem__(self):
        pass


class TestView(unittest.TestCase):

    def setUp(self) -> None:
        self.view_json = json.loads(view1)
        self.view_obj = View(view1)
        self.maxDiff = None

    def test_init(self):
        try:
            _ = View(view1)
        except Exception as ex:
            self.fail(ex.message)

    def test_annotation_order_preserved(self):
        view_serial = self.view_obj.serialize()
        for original, new in zip(self.view_json['annotations'],
                                 json.loads(view_serial)['annotations']):
            assert original['properties']['id'] == new['properties']['id'], \
                f"{original['properties']['id']} is not {new['properties']['id']}"

    def test_props_preserved(self):
        view_serial = self.view_obj.serialize()

        def id_func(a):
            return a['properties']['id']

        for original, new in zip(sorted(self.view_json['annotations'], key=id_func),
                                 sorted(json.loads(view_serial)['annotations'], key=id_func)):
            assert original == new

    def test___getitem__(self):
        pass


class TestSchema(unittest.TestCase):

    schema_res = resource_stream(f'{mmif.__name__}.{mmif._res_pkg}', mmif._schema_res_name)
    schema = json.load(schema_res)
    schema_res.close()

    def setUp(self) -> None:
        if DEBUG:
            self.hypos = []

    def tearDown(self) -> None:
        if DEBUG:
            with open('hypotheses.json', 'w') as dump:
                json.dump(self.hypos, dump, indent=2)

    @given(hypothesis_jsonschema.from_schema(schema))
    @settings(suppress_health_check=HealthCheck.all())
    def test_accepts_valid_schema(self, data):
        if DEBUG:
            self.hypos.append(data)
        try:
            _ = Mmif(json.dumps(data))
        except ValidationError as ve:
            self.fail("didn't accept valid data")


if __name__ == '__main__':
    DEBUG = False
    unittest.main()
