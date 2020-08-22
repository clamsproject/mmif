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


class TestMmif(unittest.TestCase):

    def setUp(self) -> None:
        self.examples_json = {i: json.loads(example) for i, example in examples.items() if i.startswith('mmif_')}

    def test_str_mmif_deserialize(self):
        for i, example in examples.items():
            if i.startswith('mmif_'):
                try:
                    mmif_obj = Mmif(example)
                except ValidationError:
                    self.fail(f"example {i}")
                except KeyError:
                    self.fail("didn't swap _ and @")
                self.assertEqual(mmif_obj.serialize(True), Mmif(mmif_obj.serialize()).serialize(True), f'Failed on {i}')

    def test_json_mmif_deserialize(self):
        for i, example in self.examples_json.items():
            try:
                mmif_obj = Mmif(example)
            except ValidationError as ve:
                self.fail(ve.message)
            except KeyError:
                self.fail("didn't swap _ and @")
            roundtrip = Mmif(mmif_obj.serialize())
            self.assertEqual(mmif_obj.serialize(True), roundtrip.serialize(True), f'Failed on {i}')

    def test_str_vs_json_deserialize(self):

        for i, example in examples.items():
            if not i.startswith('mmif_'):
                continue
            str_mmif_obj = Mmif(example)
            json_mmif_obj = Mmif(json.loads(example))
            self.assertEqual(str_mmif_obj.serialize(True), json_mmif_obj.serialize(True), f'Failed on {i}')

    def test_bad_mmif_deserialize_no_context(self):
        self.examples_json['mmif_example1'].pop('@context')
        json_str = json.dumps(self.examples_json['mmif_example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_metadata(self):
        self.examples_json['mmif_example1'].pop('metadata')
        json_str = json.dumps(self.examples_json['mmif_example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_media(self):
        self.examples_json['mmif_example1'].pop('media')
        json_str = json.dumps(self.examples_json['mmif_example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_views(self):
        self.examples_json['mmif_example1'].pop('views')
        json_str = json.dumps(self.examples_json['mmif_example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_medium_cannot_have_text_and_location(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        m1 = mmif_obj.get_medium_by_id('m1')
        m2 = mmif_obj.get_medium_by_id('m2')
        m1.text = m2.text
        with pytest.raises(ValidationError) as ve:
            Mmif(mmif_obj.serialize())
            assert "validating 'oneOf'" in ve.value

    def test_new_view(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        old_view_count = len(mmif_obj.views)
        mmif_obj.new_view()  # just raise exception if this fails
        self.assertEqual(old_view_count+1, len(mmif_obj.views))

    def test_medium_metadata(self):
        medium = Medium()
        medium.id = 'm999'
        medium.type = "text"
        medium.location = "random_location"
        medium.metadata['source'] = "v10"
        medium.metadata['app'] = "some_sentence_splitter"
        medium.metadata['random_key'] = "random_value"
        serialized = medium.serialize()
        deserialized = Medium(serialized)
        self.assertEqual(medium, deserialized)
        plain_json = json.loads(serialized)
        deserialized = Medium(plain_json)
        self.assertEqual(medium, deserialized)
        self.assertEqual({'id', 'type', 'location', 'metadata'}, plain_json.keys())
        self.assertEqual({'source', 'app', 'random_key'}, plain_json['metadata'].keys())

    def test_medium_text(self):
        text = "Karen flew to New York."
        en = 'en'
        medium = Medium()
        medium.id = 'm998'
        medium.type = "text"
        medium.text_value = text
        self.assertEqual(medium.text_value, text)
        medium.text_language = en
        serialized = medium.serialize()
        plain_json = json.loads(serialized)
        deserialized = Medium(serialized)
        self.assertEqual(deserialized.text_value, text)
        self.assertEqual(deserialized.text_language, en)
        self.assertEqual({'@value', '@language'}, plain_json['text'].keys())

    def test_medium_empty_text(self):
        medium = Medium()
        medium.id = 'm997'
        medium.type = "text"
        serialized = medium.serialize()
        deserialized = Medium(serialized)
        self.assertEqual(deserialized.text_value, '')
        self.assertEqual(deserialized.text_language, '')

    def test_medium(self):
        medium = Medium(examples['medium_ext_video_example'])
        serialized = medium.serialize()
        plain_json = json.loads(serialized)
        self.assertEqual({'id', 'type', 'location', 'mime'}, plain_json.keys())

    def test_add_media(self):
        medium_json = json.loads(examples['medium_ext_video_example'])
        # TODO (angus-lherrou @ 8/5/2020): check for ID uniqueness once implemented, e.g. in PR #60
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        old_media_count = len(mmif_obj.media)
        mmif_obj.add_medium(Medium(medium_json))  # just raise exception if this fails
        self.assertEqual(old_media_count+1, len(mmif_obj.media))

    def test_get_medium_by_id(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        try:
            # should succeed
            mmif_obj.get_medium_by_id('m1')
        except KeyError:
            self.fail("didn't get m1")
        try:
            # should fail
            mmif_obj.get_medium_by_id('m55')
            self.fail("didn't raise exception on getting m55")
        except KeyError:
            pass

    def test_get_media_by_view_id(self):
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        self.assertEqual(len(mmif_obj.get_media_by_source_view_id('v1')), 1)
        self.assertEqual(mmif_obj.get_media_by_source_view_id('v1')[0],
                         mmif_obj.get_medium_by_id('m2'))
        self.assertEqual(len(mmif_obj.get_media_by_source_view_id('xxx')), 0)
        new_medium = Medium()
        new_medium.metadata.source = 'v1:bb2'
        mmif_obj.add_medium(new_medium)
        self.assertEqual(len(mmif_obj.get_media_by_source_view_id('v1')), 2)

    def test_get_medium_by_metadata(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        self.assertEqual(len(mmif_obj.get_media_by_metadata("source", "v1:bb1")), 1)
        self.assertEqual(len(mmif_obj.get_media_by_metadata("source", "v3")), 0)

    def test_get_medium_by_appid(self):
        tesseract_appid = 'http://apps.clams.io/tesseract/1.2.1'
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        self.assertEqual(len(mmif_obj.get_media_by_app(tesseract_appid)), 1)
        self.assertEqual(len(mmif_obj.get_media_by_app('xxx')), 0)
        new_medium = Medium()
        new_medium.metadata.source = 'v1:bb2'
        new_medium.metadata.app = tesseract_appid
        mmif_obj.add_medium(new_medium)
        self.assertEqual(len(mmif_obj.get_media_by_app(tesseract_appid)), 2)

    def test_get_media_locations(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        self.assertEqual(len(mmif_obj.get_media_locations('image')), 1)
        self.assertEqual(mmif_obj.get_medium_location('image'), "/var/archive/image-0012.jpg")
        # text medium is there but no location is specified
        self.assertEqual(len(mmif_obj.get_media_locations('text')), 0)
        self.assertEqual(mmif_obj.get_medium_location('text'), None)
        # audio medium is not there
        self.assertEqual(len(mmif_obj.get_media_locations('audio')), 0)

    def test_get_view_by_id(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        try:
            _ = mmif_obj.get_view_by_id('v1')
        except KeyError:
            self.fail("didn't get v1")

        try:
            _ = mmif_obj.get_view_by_id('v55')
            self.fail("didn't raise exception on getting v55")
        except KeyError:
            pass

    def test_get_all_views_contain(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        views_len = len(mmif_obj.views)
        views = mmif_obj.get_all_views_contain('BoundingBox')
        self.assertEqual(len(views), views_len)

    def test_get_view_contains(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        view = mmif_obj.get_view_contains('BoundingBox')
        self.assertIsNotNone(view)
        self.assertEqual('v1', view.id)
        view = mmif_obj.get_view_contains('NonExistingType')
        self.assertIsNone(view)

    def test_new_view_id(self):
        p = Mmif.view_prefix
        mmif_obj = Mmif(validate=False)
        a_view = mmif_obj.new_view()
        self.assertEqual(a_view.id, f'{p}0')
        b_view = View()
        b_view.id = f'{p}2'
        mmif_obj.add_view(b_view)
        self.assertEqual({f'{p}0', f'{p}2'}, set(mmif_obj.views.items.keys()))
        c_view = mmif_obj.new_view()
        self.assertEqual(c_view.id, f'{p}3')
        d_view = View()
        d_view.id = 'v4'
        mmif_obj.add_view(d_view)
        e_view = mmif_obj.new_view()
        self.assertEqual(e_view.id, f'{p}4')
        self.assertEqual(len(mmif_obj.views), 5)

    def test_add_medium(self):
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        med_obj = Medium(examples['medium_ext_video_example'])
        mmif_obj.add_medium(med_obj)
        try:
            mmif_obj.add_medium(med_obj)
            self.fail("didn't raise exception on duplicate ID add")
        except KeyError:
            ...
        try:
            mmif_obj.add_medium(med_obj, overwrite=True)
        except KeyError:
            self.fail("raised exception on duplicate ID add when overwrite was set to True")

    def test_add_view(self):
        mmif_obj = Mmif(examples['mmif_example3'], validate=False)  # TODO: remove validate=False once 56 is done
        view_obj = View(examples['view_example1'])
        view_obj.id = 'v4'
        mmif_obj.add_view(view_obj)
        try:
            mmif_obj.add_view(view_obj)
            self.fail("didn't raise exception on duplicate ID add")
        except KeyError:
            ...
        try:
            mmif_obj.add_view(view_obj, overwrite=True)
        except KeyError:
            self.fail("raised exception on duplicate ID add when overwrite was set to True")

    def test___getitem__(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        self.assertIsInstance(mmif_obj['m1'], Medium)
        self.assertIsInstance(mmif_obj['v1'], View)
        self.assertIsInstance(mmif_obj['v1:bb1'], Annotation)
        with self.assertRaises(KeyError):
            mmif_obj['asdf']
        a_view = View()
        a_view.id = 'm1'
        mmif_obj.add_view(a_view)
        with self.assertRaises(KeyError):
            mmif_obj['m1']
        medium = Medium()
        medium.add_metadata('random_key', 'random_value')
        self.assertEqual(medium.metadata['random_key'], 'random_value')


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

    def test_under_at_swap(self):
        text = Text()
        text.value = "asdf"
        text.lang = "en"
        self.assertTrue(hasattr(text, '_value'))
        self.assertTrue(hasattr(text, '_language'))
        plain_json = json.loads(text.serialize())
        self.assertIn('@value', plain_json.keys())
        self.assertIn('@language', plain_json.keys())

    def test_print_mmif(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mmif_obj = Mmif(examples['mmif_example1'])
            print(mmif_obj)
            self.assertEqual(json.loads(examples['mmif_example1']), json.loads(fake_out.getvalue()))


class TestGetItem(unittest.TestCase):

    def setUp(self) -> None:
        self.mmif_obj = Mmif(examples['mmif_example1'])
        self.view_obj = View(examples['view_example1'])

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

    def test_mmif_fail_getitem_annotation_no_view(self):
        try:
            _ = self.mmif_obj['v5:s1']
            self.fail("didn't except on annotation getitem on bad view")
        except KeyError:
            pass

    def test_mmif_fail_getitem_no_annotation(self):
        try:
            _ = self.mmif_obj['v1:s1']
            self.fail("didn't except on bad annotation getitem")
        except KeyError:
            pass

    def test_view_getitem(self):
        try:
            s1 = self.view_obj['s1']
            self.assertIs(s1, self.view_obj.annotations.get('s1'))
        except TypeError:
            self.fail("__getitem__ not implemented")
        except KeyError:
            self.fail("didn't get annotation 's1'")


class TestView(unittest.TestCase):

    def setUp(self) -> None:
        self.view_json = json.loads(examples['view_example1'])
        self.view_obj = View(examples['view_example1'])
        self.maxDiff = None

    def test_init(self):
        _ = View(examples['view_example1'])  # just raise exception

    def test_annotation_order_preserved(self):
        view_serial = self.view_obj.serialize()
        for original, new in zip(self.view_json['annotations'],
                                 json.loads(view_serial)['annotations']):

            o = original['properties']['id']
            n = new['properties']['id']
            assert o == n, f"{o} is not {n}"

    def test_view_metadata(self):
        vmeta = ViewMetadata()
        vmeta['tool'] = 'fdsa'
        vmeta['random_key'] = 'random_value'
        serialized = vmeta.serialize()
        deserialized = ViewMetadata(serialized)
        self.assertEqual(vmeta, deserialized)

    def test_props_preserved(self):
        view_serial = self.view_obj.serialize()

        def id_func(a):
            return a['properties']['id']

        for original, new in zip(sorted(self.view_json['annotations'], key=id_func),
                                 sorted(json.loads(view_serial)['annotations'], key=id_func)):
            self.assertEqual(original, new)

    def test_add_annotation(self):
        anno_obj = Annotation(json.loads(examples['annotation_example1']))
        old_len = len(self.view_obj.annotations)
        self.view_obj.add_annotation(anno_obj)  # raise exception if this fails
        self.assertEqual(old_len+1, len(self.view_obj.annotations))
        self.assertIn('Token', self.view_obj.metadata.contains)
        _ = self.view_obj.serialize()  # raise exception if this fails
    
    def test_new_annotation(self):
        self.view_obj.new_annotation('relation1', 'Relation')  # raise exception if this fails
        self.assertIn('Relation', self.view_obj.metadata.contains)


class TestAnnotation(unittest.TestCase):
    # TODO (angus-lherrou @ 7/27/2020): testing should include validation for required attrs
    #  once that is implemented (issue #23)
    def setUp(self) -> None:
        self.examples = {}
        for i, example in examples.items():
            if not i.startswith('mmif_'):
                continue
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
        props_json = self.data['mmif_example1']['annotations'][0]['properties']
        props_obj = MediumMetadata(props_json)
        self.assertEqual(props_json, json.loads(props_obj.serialize()))

    def test_add_property(self):
        for i, datum in self.data.items():
            for j in range(len(datum['json']['views'])):
                view_id = datum['json']['views'][j]['id']
                anno_id = datum['json']['views'][j]['annotations'][0]['properties']['id']
                props = datum['json']['views'][j]['annotations'][0]['properties']
                removed_prop_key, removed_prop_value = list(props.items())[-1]
                props.pop(removed_prop_key)
                try:
                    new_mmif = Mmif(datum['json'])
                    new_mmif.get_view_by_id(view_id).annotations[anno_id].add_property(removed_prop_key, removed_prop_value)
                    self.assertEqual(json.loads(datum['string'])['views'][j],
                                     json.loads(new_mmif.serialize())['views'][j],
                                     f'Failed on {i}, {view_id}')
                except ValidationError:
                    continue

    def test_id(self):
        anno_obj: Annotation = self.data['mmif_example1']['mmif']['v1:bb1']

        old_id = anno_obj.id
        self.assertEqual('bb1', old_id)

    def test_change_id(self):
        anno_obj: Annotation = self.data['mmif_example1']['mmif']['v1:bb1']

        anno_obj.id = 'bb2'
        self.assertEqual('bb2', anno_obj.id)

        serialized = json.loads(anno_obj.serialize())
        new_id = serialized['properties']['id']
        self.assertEqual('bb2', new_id)

        serialized_mmif = json.loads(self.data['mmif_example1']['mmif'].serialize())
        new_id_from_mmif = serialized_mmif['views'][0]['annotations'][0]['properties']['id']
        self.assertEqual('bb2', new_id_from_mmif)


class TestMedium(unittest.TestCase):

    def setUp(self) -> None:
        self.examples = {}
        for i, example in examples.items():
            if not i.startswith('mmif_'):
                continue
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
                    self.fail(f"{type(ex)}: {str(ex)}: {i} {medium['id']}")

    def test_medium_metadata(self):
        metadata_json = self.data['mmif_example1']['media'][1]['metadata']
        metadata_obj = MediumMetadata(metadata_json)
        self.assertEqual(metadata_json, json.loads(metadata_obj.serialize()))

    def test_deserialize_with_whole_mmif(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['media']):
                try:
                    medium_obj = datum['mmif'].get_medium_by_id(medium['id'])
                except KeyError:
                    self.fail(f"Medium {medium['id']} not found in MMIF")
                self.assertIsInstance(medium_obj, Medium)
                if 'metadata' in medium:
                    self.assertIsInstance(medium_obj.metadata, MediumMetadata)
                if 'submedia' in medium:
                    self.assertIsInstance(medium_obj.submedia, list)
                    for submedium in medium_obj.submedia:
                        self.assertIsInstance(submedium, Submedium)

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
                        self.assertIsInstance(submedium, Submedium)

    def test_serialize_to_medium_str(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['media']):
                medium_obj = Medium(medium)
                serialized = json.loads(medium_obj.serialize())
                self.assertEqual(medium, serialized, f'Failed on {i}, {medium["id"]}')

    def test_serialize_with_whole_mmif(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['media']):
                medium_serialized = json.loads(datum['mmif'].serialize())['media'][j]
                self.assertEqual(medium, medium_serialized, f'Failed on {i}, {medium["id"]}')

    def test_add_metadata(self):
        for i, datum in self.data.items():
            for j in range(len(datum['json']['media'])):
                medium_id = datum['json']['media'][j]['id']
                metadata = datum['json']['media'][j].get('metadata')
                if metadata:
                    removed_metadatum_key, removed_metadatum_value = list(metadata.items())[-1]
                    metadata.pop(removed_metadatum_key)
                    try:
                        new_mmif = Mmif(datum['json'])
                        new_mmif.get_medium_by_id(medium_id).add_metadata(removed_metadatum_key, removed_metadatum_value)
                        self.assertEqual(json.loads(datum['string']), json.loads(new_mmif.serialize()), f'Failed on {i}, {medium_id}')
                    except ValidationError:
                        continue


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
