import unittest
import json
from io import StringIO
from unittest.mock import patch

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

    @unittest.skipUnless(*SKIP_FOR_56)
    def test_temp_str_mmif_deserialize(self):
        try:
            mmif_obj = Mmif(examples['example1'])
        except ValidationError as ve:
            self.fail("example 1")
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

    @unittest.skipUnless(*SKIP_FOR_56)
    def test_temp_json_mmif_deserialize(self):
        try:
            mmif_obj = Mmif(json.loads(examples['example1']))
        except ValidationError as ve:
            self.fail("example 1")
        except KeyError as ke:
            self.fail("didn't swap _ and @")
        self.assertEqual(mmif_obj, Mmif(mmif_obj.serialize()))

    @unittest.skipIf(*SKIP_FOR_56)
    def test_str_vs_json_deserialize(self):
        for i, example in examples.items():
            str_mmif_obj = Mmif(example)
            json_mmif_obj = Mmif(json.loads(example))
            self.assertEqual(json.loads(str_mmif_obj.serialize()), json.loads(json_mmif_obj.serialize()))

    @unittest.skipUnless(*SKIP_FOR_56)
    def test_temp_str_vs_json_deserialize(self):
        str_mmif_obj = Mmif(examples['example1'])
        json_mmif_obj = Mmif(json.loads(examples['example1']))
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

    def test_new_view(self):
        mmif_obj = Mmif(examples['example1'])
        old_view_count = len(mmif_obj.views)
        try:
            mmif_obj.new_view()
        except Exception as ex:
            self.fail("failed to create new view in Mmif: "+ex.message)
        self.assertEqual(len(mmif_obj.views), old_view_count+1)

    def test_medium_metadata(self):
        text = "Karen flew to New York."
        en = 'en'
        medium = Medium()
        medium.id = 'm999'
        medium.type = "text"
        medium.text_value = text
        self.assertEqual(medium.text_value, text)
        medium.text_language = en
        medium.metadata['source'] = "v10"
        medium.metadata['app'] = "some_sentence_splitter"
        medium.metadata['random_key'] = "random_value"
        serialized = medium.serialize()
        deserialized = Medium(serialized)
        self.assertEqual(medium, deserialized)
        plain_json = json.loads(serialized)
        deserialized = Medium(plain_json)
        self.assertEqual(medium, deserialized)
        self.assertEqual({'id', 'type', 'text', 'metadata'}, plain_json.keys())
        self.assertEqual({'@value', '@language'}, plain_json['text'].keys())
        self.assertEqual({'source', 'app', 'random_key'}, plain_json['metadata'].keys())

    def test_medium(self):
        medium = Medium(medium1)
        serialized = medium.serialize()
        plain_json = json.loads(serialized)
        self.assertEqual({'id', 'type', 'location', 'mime'}, plain_json.keys())

    def test_add_media(self):
        medium_json = json.loads(medium1)
        # TODO (angus-lherrou @ 8/5/2020): check for ID uniqueness once implemented, e.g. in PR #60
        mmif_obj = Mmif(examples['example1'])
        old_media_count = len(mmif_obj.media)
        try:
            mmif_obj.add_media(Medium(medium_json))
        except Exception as ex:
            self.fail("failed to add medium to Mmif: "+ex.message)
        self.assertEqual(len(mmif_obj.media), old_media_count+1)

    def test_fail_add_media(self):
        medium_json = json.loads(medium2)
        mmif_obj = Mmif(examples['example1'])
        # TODO (angus-lherrou @ 8/5/2020): deprecated as of #41
        try:
            mmif_obj.add_media(Medium(medium_json))
            self.fail("added medium of same type")
        except:
            pass

    def test_get_medium_by_id(self):
        mmif_obj = Mmif(examples['example1'])
        try:
            medium = mmif_obj.get_medium_by_id('m1')
        except:
            self.fail("didn't get m1")
        try:
            medium = mmif_obj.get_medium_by_id('m55')
            self.fail("didn't raise exception on getting m55")
        except:
            pass

    def test_get_view_by_id(self):
        mmif_obj = Mmif(examples['example1'])
        try:
            medium = mmif_obj.get_view_by_id('v1')
        except:
            self.fail("didn't get v1")
        try:
            medium = mmif_obj.get_view_by_id('v55')
            self.fail("didn't raise exception on getting v55")
        except:
            pass

    def test_get_all_views_contain(self):
        mmif_obj = Mmif(examples['example1'])
        views_len = len(mmif_obj.views)
        views = mmif_obj.get_all_views_contain('BoundingBox')
        self.assertEqual(views_len, len(views))

    def test_get_view_contains(self):
        # TODO (angus-lherrou @ 8/5/2020): expand to better examples once schema is fixed
        mmif_obj = Mmif(examples['example1'])
        view = mmif_obj.get_view_contains('BoundingBox')
        self.assertIsNotNone(view)
        self.assertEqual(view.id, 'v1')


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

    def test_load_json_on_other(self):
        try:
            MmifObject._load_json(123)
            self.fail()
        except TypeError:
            pass

    def test_print_mmif(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mmif_obj = Mmif(examples['example1'])
            print(mmif_obj)
            self.assertEqual(json.loads(examples['example1']), json.loads(fake_out.getvalue()))


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

    def test_mmif_fail_getitem_toplevel(self):
        try:
            _ = self.mmif_obj['v5']
            self.fail("didn't except on bad getitem")
        except KeyError:
            pass
        except:
            self.fail('wrong exception')

    def test_mmif_fail_getitem_annotation_no_view(self):
        try:
            _ = self.mmif_obj['v5:s1']
            self.fail("didn't except on annotation getitem on bad view")
        except KeyError:
            pass
        except:
            self.fail('wrong exception')

    def test_mmif_fail_getitem_no_annotation(self):
        try:
            _ = self.mmif_obj['v1:s1']
            self.fail("didn't except on bad annotation getitem")
        except KeyError:
            pass
        except:
            self.fail('wrong exception')

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
            self.assertEqual(original, new)

    def test_add_annotation(self):
        anno_obj = Annotation(json.loads(anno1))
        old_len = len(self.view_obj.annotations)
        try:
            self.view_obj.add_annotation(anno_obj)
        except Exception as ex:
            self.fail('failed to add annotation to view: '+ex.message)
        self.assertEqual(len(self.view_obj.annotations), old_len+1)
        self.assertIn('Token', self.view_obj.metadata.contains)
        try:
            _ = self.view_obj.serialize()
        except Exception as ex:
            self.fail(ex.message)
    
    def test_new_annotation(self):
        try:
            self.view_obj.new_annotation('relation1', 'Relation')
        except Exception as ex:
            self.fail('failed to create new annotation in view: '+ex.message)
        self.assertIn('Relation', self.view_obj.metadata.contains)


class TestAnnotation(unittest.TestCase):
    # TODO (angus-lherrou @ 7/27/2020): testing should include validation for required attrs
    #  once that is implemented (issue #23)
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
                         'annotations': [annotation
                                         for view in json.loads(example)['views']
                                         for annotation in view['annotations']]}
                     for i, example in self.examples.items()}

    def test_annotation_properties(self):
        props_json = self.data['example1']['annotations'][0]['properties']
        props_obj = MediumMetadata(props_json)
        self.assertEqual(json.loads(props_obj.serialize()), props_json)

    def test_add_property(self):
        for datum in self.data.values():
            view_id = datum['json']['views'][0]['id']
            anno_id = datum['json']['views'][0]['annotations'][0]['properties']['id']
            props = datum['json']['views'][0]['annotations'][0]['properties']
            removed_prop_key, removed_prop_value = list(props.items())[-1]
            props.pop(removed_prop_key)
            new_mmif = Mmif(datum['json'])
            new_mmif.get_view_by_id(view_id).annotations[0].add_property(removed_prop_key, removed_prop_value)
            self.assertEqual(json.loads(new_mmif.serialize()), json.loads(datum['string']))


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

    def test_medium_metadata(self):
        metadata_json = self.data['example1']['media'][1]['metadata']
        metadata_obj = MediumMetadata(metadata_json)
        self.assertEqual(json.loads(metadata_obj.serialize()), metadata_json)

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

    def test_add_metadata(self):
        for i, datum in self.data.items():
            medium_id = datum['json']['media'][0]['id']
            metadata = datum['json']['media'][0].get('metadata')
            if metadata:
                removed_metadatum_key, removed_metadatum_value = list(metadata.items())[-1]
                metadata.pop(removed_metadatum_key)
                new_mmif = Mmif(datum['json'])
                new_mmif[f'{medium_id}'].add_metadata(removed_metadatum_key, removed_metadatum_value)
                self.assertEqual(json.loads(new_mmif.serialize()), json.loads(datum['string']))


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
