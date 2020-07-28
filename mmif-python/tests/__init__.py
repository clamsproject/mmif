import unittest
import json

import mmif
from hypothesis import given, settings, HealthCheck  # pip install hypothesis
import hypothesis_jsonschema  # pip install hypothesis-jsonschema

import pytest
from jsonschema import ValidationError
from mmif.serialize import Mmif, View, MmifObject, Medium
from pkg_resources import resource_stream

from tests.mmif_examples import *


DEBUG = False
SKIP_SCHEMA = True
SKIP_DICT_DESERIALIZE = None  # formerly "model can't process dicts yet"
SKIP_FOR_56 = "Skipping issue #56 bug"
NOT_MERGED_40 = "Skipping until #40 is merged"


class TestMmif(unittest.TestCase):

    def setUp(self) -> None:
        self.examples = examples.copy()
        self.examples_json = {i: json.loads(example) for i, example in self.examples.items()}

    @unittest.skipIf(SKIP_FOR_56, SKIP_FOR_56)
    def test_str_mmif_deserialize(self):
        for i, example in self.examples.items():
            try:
                mmif_obj = Mmif(example)
            except ValidationError as ve:
                self.fail(f"example {i}")
            except KeyError as ke:
                self.fail("didn't swap _ and @")
            self.assertEqual(mmif_obj, Mmif(mmif_obj.serialize()))

    @unittest.skipIf(SKIP_FOR_56, SKIP_FOR_56)
    @unittest.skipIf(SKIP_DICT_DESERIALIZE, SKIP_DICT_DESERIALIZE)
    def test_json_mmif_deserialize(self):
        for i, example in self.examples_json.items():
            try:
                mmif_obj = Mmif(example)
            except ValidationError as ve:
                self.fail(ve.message)
            except KeyError as ke:
                self.fail("didn't swap _ and @")
            self.assertEqual(mmif_obj, Mmif(json.loads(mmif_obj.serialize())))

    @unittest.skipIf(SKIP_FOR_56, SKIP_FOR_56)
    @unittest.skipIf(SKIP_DICT_DESERIALIZE, SKIP_DICT_DESERIALIZE)
    def test_str_vs_json_deserialize(self):
        for i, example in self.examples.items():
            str_mmif_obj = Mmif(example)
            json_mmif_obj = Mmif(json.loads(example))
            self.assertEqual(json.loads(str_mmif_obj.serialize()), json.loads(json_mmif_obj.serialize()))

    def test_bad_mmif_deserialize_no_context(self):
        self.examples_json['example1'].pop('@context')
        json_str = json.dumps(self.examples_json['example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_metadata(self):
        self.examples_json['example1'].pop('metadata')
        json_str = json.dumps(self.examples_json['example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_media(self):
        self.examples_json['example1'].pop('media')
        json_str = json.dumps(self.examples_json['example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_views(self):
        self.examples_json['example1'].pop('views')
        json_str = json.dumps(self.examples_json['example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_medium_cannot_have_text_and_location(self):
        mmif_obj = Mmif(self.examples['example1'])
        m1 = mmif_obj.get_medium_by_id('m1')
        m2 = mmif_obj.get_medium_by_id('m2')
        m1.text = m2.text
        with pytest.raises(ValidationError) as ve:
            Mmif(mmif_obj.serialize())
            assert "validating 'oneOf'" in ve.value


class TestMmifObject(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_load_json_on_str(self):
        self.assertTrue("_type" in MmifObject._load_json('{ "@type": "some_type", "@value": "some_value"}').keys())
        self.assertTrue("_value" in MmifObject._load_json('{ "@type": "some_type", "@value": "some_value"}').keys())

    @unittest.skipIf(SKIP_DICT_DESERIALIZE, SKIP_DICT_DESERIALIZE)
    def test_load_json_on_dict(self):
        json_dict = json.loads('{ "@type": "some_type", "@value": "some_value"}')
        self.assertTrue("_type" in MmifObject._load_json(json_dict.copy()).keys())
        self.assertTrue("_value" in MmifObject._load_json(json_dict.copy()).keys())


@unittest.skipIf(NOT_MERGED_40, NOT_MERGED_40)
class TestGetItem(unittest.TestCase):

    def setUp(self) -> None:
        self.mmif_obj = Mmif(examples['example1'])
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


class TestAnnotation(unittest.TestCase):
    # TODO (angus-lherrou @ 7/27/2020): testing should include validation for required attrs
    #  once that is implemented (issue #23)
    ...


class TestMedium(unittest.TestCase):

    def setUp(self) -> None:
        self.example1 = json.loads(examples['example1'])
        self.example2 = json.loads(examples['example2'])

    def test_init(self):
        try:
            _ = Medium(self.example1['media'][0])
            _ = Medium(self.example1['media'][1])
            _ = Medium(self.example2['media'][0])
            _ = Medium(self.example2['media'][1])
        except Exception as ex:
            self.fail(str(type(ex)) + str(ex.message))
    ...


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
