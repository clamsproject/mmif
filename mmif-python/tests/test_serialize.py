import unittest
import json

import mmif
from hypothesis import given, settings, HealthCheck
import hypothesis_jsonschema

import pytest
from jsonschema import ValidationError
from mmif.serialize import Mmif, View
from pkg_resources import resource_stream

from tests.mmif_examples import *


DEBUG = False
SKIP_SCHEMA = True


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
        mmif_obj = Mmif(json.dumps(self.mmif_json))
        m1 = mmif_obj.get_medium_by_id('m1')
        m2 = mmif_obj.get_medium_by_id('m2')
        m1.text = m2.text
        with pytest.raises(ValidationError) as ve:
            Mmif(mmif_obj.serialize())
            assert "validating 'oneOf'" in ve.value


@unittest.skip("Skipping until #40 is merged")
class TestGetItem(unittest.TestCase):

    def setUp(self) -> None:
        self.mmif_obj = Mmif(example1)
        self.view_obj = View(view1)

    def test_mmif_getitem_medium(self):
        try:
            m1 = self.mmif_obj['m1']
            self.assertIs(m1, self.mmif_obj.media.get('m1'))
        except TypeError:
            self.fail("__getitem__ not implemented")
        except KeyError:
            self.fail("didn't get medium 'm1'")

    def test_mmif_getitem_view(self):
        try:
            v1 = self.mmif_obj['v1']
            self.assertIs(v1, self.mmif_obj.views.get('v1'))
        except TypeError:
            self.fail("__getitem__ not implemented")
        except KeyError:
            self.fail("didn't get view 'v1'")

    def test_mmif_getitem_annotation(self):
        try:
            v1_bb1 = self.mmif_obj['v1:bb1']
            self.assertIs(v1_bb1, self.mmif_obj.views.get('v1').annotations.get('bb1'))
        except TypeError:
            self.fail("__getitem__ not implemented")
        except KeyError:
            self.fail("didn't get annotation 'v1:bb1'")

    def test_view_getitem(self):
        try:
            bb1 = self.view_obj['bb1']
            self.assertIs(bb1, self.view_obj.annotations.get('bb1'))
        except TypeError:
            self.fail("__getitem__ not implemented")
        except KeyError:
            self.fail("didn't get annotation 'bb1'")


class TestView(unittest.TestCase):

    def setUp(self) -> None:
        self.view_json = json.loads(view1)
        self.view_obj = View(view1)
        self.maxDiff = None

    def test_init(self):
        try:
            _ = View(view1)
        except Exception as ex:
            self.fail(str(type(ex)) + str(ex.message))

    # largely useless until #40 is merged
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


@unittest.skipIf(SKIP_SCHEMA, "Skipping TestSchema by default")
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
    unittest.main()
