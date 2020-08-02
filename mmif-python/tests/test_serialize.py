import unittest
import json

import mmif
from hypothesis import given, settings, HealthCheck  # pip install hypothesis
import hypothesis_jsonschema  # pip install hypothesis-jsonschema

import pytest
from jsonschema import ValidationError
from mmif.serialize import *
from mmif.serialize.model import *
from pkg_resources import resource_stream

from tests.mmif_examples import *


# Flags for skipping tests
DEBUG = False
SKIP_SCHEMA = True, "Skipping TestSchema by default"
SKIP_FOR_56 = True, "Skipping issue #56 bug"
NOT_MERGED_40 = True, "Skipping until #40 is merged"


class TestMmif(unittest.TestCase):

    def setUp(self) -> None:
        self.examples_json = {i: json.loads(example) for i, example in examples.items()}

    @unittest.skipIf(*SKIP_FOR_56)
    def test_str_mmif_deserialize(self):
        for i, example in examples.items():
            try:
                mmif_obj = Mmif(example)
            except ValidationError as ve:
                self.fail(f"example {i}")
            except KeyError as ke:
                self.fail("didn't swap _ and @")
            self.assertEqual(mmif_obj, Mmif(mmif_obj.serialize()))

    @unittest.skipIf(*SKIP_FOR_56)
    def test_json_mmif_deserialize(self):
        for i, example in self.examples_json.items():
            try:
                mmif_obj = Mmif(example)
            except ValidationError as ve:
                self.fail(ve.message)
            except KeyError as ke:
                self.fail("didn't swap _ and @")
            self.assertEqual(mmif_obj, Mmif(json.loads(mmif_obj.serialize())))

    @unittest.skipIf(*SKIP_FOR_56)
    def test_str_vs_json_deserialize(self):
        for i, example in examples.items():
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
        mmif_obj = Mmif(examples['example1'])
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

    def test_load_json_on_dict(self):
        json_dict = json.loads('{ "@type": "some_type", "@value": "some_value"}')
        self.assertTrue("_type" in MmifObject._load_json(json_dict.copy()).keys())
        self.assertTrue("_value" in MmifObject._load_json(json_dict.copy()).keys())


@unittest.skipIf(*NOT_MERGED_40)
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
        self.examples = {}
        for i, example in examples.items():
            try:
                Mmif(example)
                self.examples[i] = example
            except ValidationError:
                continue
        self.data = {i: {'string': example,
                         'json': json.loads(example),
                         'mmif': Mmif(example),
                         'media': json.loads(example)['media']}
                     for i, example in self.examples.items()}

    def test_init(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['media']):
                try:
                    _ = Medium(medium)
                except Exception as ex:
                    self.fail(f"{type(ex)}: {ex.message}: example {i}, medium {j}")

    def test_deserialize_with_whole_mmif(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['media']):
                try:
                    medium_obj = datum['mmif'].get_medium_by_id(medium['id'])
                except Exception:
                    self.fail(f"Medium {medium['id']} not found in MMIF")
                self.assertIsInstance(medium_obj, Medium)
                if 'metadata' in medium:
                    self.assertIsInstance(medium_obj.metadata, MediumMetadata)
                if 'submedia' in medium:
                    self.assertIsInstance(medium_obj.submedia, list)
                    for submedium in medium_obj.submedia:
                        self.assertIsInstance(submedium, Submedia)

    def test_deserialize_with_medium_str(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['media']):
                medium_obj = Medium(medium)
                self.assertIsInstance(medium_obj, Medium)
                if 'metadata' in medium:
                    self.assertIsInstance(medium_obj.metadata, MediumMetadata)
                if 'submedia' in medium:
                    self.assertIsInstance(medium_obj.submedia, list)
                    for submedium in medium_obj.submedia:
                        self.assertIsInstance(submedium, Submedia)

    def test_serialize_to_medium_str(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['media']):
                medium_obj = Medium(medium)
                serialized = json.loads(medium_obj.serialize())
                self.assertEqual(medium, serialized)

    def test_serialize_with_whole_mmif(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['media']):
                medium_serialized = json.loads(datum['mmif'].serialize())['media'][j]
                self.assertEqual(medium, medium_serialized)


@unittest.skipIf(*SKIP_SCHEMA)
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
