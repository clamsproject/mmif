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
from mmif.serialize.view import ContainsDict
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
                ...
            except ValidationError as ve:
                self.fail(ve.message)
            except KeyError:
                self.fail("didn't swap _ and @")
            self.assertTrue('id' in list(mmif_obj.views._items.values())[0].__dict__)
            roundtrip = Mmif(mmif_obj.serialize())
            self.assertEqual(mmif_obj.serialize(True), roundtrip.serialize(True), f'Failed on {i}')

    def test_str_vs_json_deserialize(self):

        for i, example in examples.items():
            if not i.startswith('mmif_'):
                continue
            str_mmif_obj = Mmif(example)
            json_mmif_obj = Mmif(json.loads(example))
            self.assertEqual(str_mmif_obj.serialize(True), json_mmif_obj.serialize(True), f'Failed on {i}')

    def test_bad_mmif_deserialize_no_metadata(self):
        self.examples_json['mmif_example1'].pop('metadata')
        json_str = json.dumps(self.examples_json['mmif_example1'])
        try:
            _ = Mmif(json_str)
            self.fail()
        except ValidationError:
            pass

    def test_bad_mmif_deserialize_no_documents(self):
        self.examples_json['mmif_example1'].pop('documents')
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

    def test_document_cannot_have_text_and_location(self):
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        m1 = mmif_obj.get_document_by_id('m1')
        m2 = mmif_obj.get_document_by_id('m2')
        m1.text = m2.text
        with pytest.raises(ValidationError) as ve:
            Mmif(mmif_obj.serialize())
            assert "validating 'oneOf'" in ve.value

    def test_new_view(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        old_view_count = len(mmif_obj.views)
        mmif_obj.new_view()  # just raise exception if this fails
        self.assertEqual(old_view_count+1, len(mmif_obj.views))

    def test_document_metadata(self):
        document = Document()
        document.id = 'm999'
        document.type = "text"
        document.location = "random_location"
        document.metadata['source'] = "v10"
        document.metadata['app'] = "some_sentence_splitter"
        document.metadata['random_key'] = "random_value"
        serialized = document.serialize()
        deserialized = Document(serialized)
        self.assertEqual(document, deserialized)
        plain_json = json.loads(serialized)
        deserialized = Document(plain_json)
        self.assertEqual(document, deserialized)
        self.assertEqual({'id', 'type', 'location', 'metadata'}, plain_json.keys())
        self.assertEqual({'source', 'app', 'random_key'}, plain_json['metadata'].keys())

    def test_document_text(self):
        text = "Karen flew to New York."
        en = 'en'
        document = Document()
        document.id = 'm998'
        document.type = "text"
        document.text_value = text
        self.assertEqual(document.text_value, text)
        document.text_language = en
        serialized = document.serialize()
        plain_json = json.loads(serialized)
        deserialized = Document(serialized)
        self.assertEqual(deserialized.text_value, text)
        self.assertEqual(deserialized.text_language, en)
        self.assertEqual({'@value', '@language'}, plain_json['text'].keys())

    def test_document_empty_text(self):
        document = Document()
        document.id = 'm997'
        document.type = "text"
        serialized = document.serialize()
        deserialized = Document(serialized)
        self.assertEqual(deserialized.text_value, '')
        self.assertEqual(deserialized.text_language, '')

    def test_document(self):
        document = Document(examples['document_ext_video_example'])
        serialized = document.serialize()
        plain_json = json.loads(serialized)
        self.assertEqual({'id', 'type', 'location', 'mime'}, plain_json.keys())

    def test_add_documents(self):
        document_json = json.loads(examples['document_ext_video_example'])
        # TODO (angus-lherrou @ 8/5/2020): check for ID uniqueness once implemented, e.g. in PR #60
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        old_documents_count = len(mmif_obj.documents)
        mmif_obj.add_document(Document(document_json))  # just raise exception if this fails
        self.assertEqual(old_documents_count+1, len(mmif_obj.documents))

    def test_get_document_by_id(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        try:
            # should succeed
            mmif_obj.get_document_by_id('m1')
        except KeyError:
            self.fail("didn't get m1")
        try:
            # should fail
            mmif_obj.get_document_by_id('m55')
            self.fail("didn't raise exception on getting m55")
        except KeyError:
            pass

    def test_get_documents_by_view_id(self):
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        self.assertEqual(len(mmif_obj.get_documents_by_source_view_id('v1')), 1)
        self.assertEqual(mmif_obj.get_documents_by_source_view_id('v1')[0],
                         mmif_obj.get_document_by_id('m2'))
        self.assertEqual(len(mmif_obj.get_documents_by_source_view_id('xxx')), 0)
        new_document = Document()
        new_document.metadata.source = 'v1:bb2'
        mmif_obj.add_document(new_document)
        self.assertEqual(len(mmif_obj.get_documents_by_source_view_id('v1')), 2)

    def test_get_document_by_metadata(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        self.assertEqual(len(mmif_obj.get_documents_by_metadata("source", "v1:bb1")), 1)
        self.assertEqual(len(mmif_obj.get_documents_by_metadata("source", "v3")), 0)

    def test_get_document_by_appid(self):
        tesseract_appid = 'http://apps.clams.io/tesseract/1.2.1'
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        self.assertEqual(len(mmif_obj.get_documents_by_app(tesseract_appid)), 1)
        self.assertEqual(len(mmif_obj.get_documents_by_app('xxx')), 0)
        new_document = Document()
        new_document.metadata.source = 'v1:bb2'
        new_document.metadata.app = tesseract_appid
        mmif_obj.add_document(new_document)
        self.assertEqual(len(mmif_obj.get_documents_by_app(tesseract_appid)), 2)

    def test_get_documents_locations(self):
        mmif_obj = Mmif(examples['mmif_example1'])
        self.assertEqual(len(mmif_obj.get_documents_locations('image')), 1)
        self.assertEqual(mmif_obj.get_document_location('image'), "/var/archive/image-0012.jpg")
        # text document is there but no location is specified
        self.assertEqual(len(mmif_obj.get_documents_locations('text')), 0)
        self.assertEqual(mmif_obj.get_document_location('text'), None)
        # audio document is not there
        self.assertEqual(len(mmif_obj.get_documents_locations('audio')), 0)

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
        self.assertEqual({f'{p}0', f'{p}2'}, set(mmif_obj.views._items.keys()))
        c_view = mmif_obj.new_view()
        self.assertEqual(c_view.id, f'{p}3')
        d_view = View()
        d_view.id = 'v4'
        mmif_obj.add_view(d_view)
        e_view = mmif_obj.new_view()
        self.assertEqual(e_view.id, f'{p}4')
        self.assertEqual(len(mmif_obj.views), 5)

    def test_add_document(self):
        mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        med_obj = Document(examples['document_ext_video_example'])
        mmif_obj.add_document(med_obj)
        try:
            mmif_obj.add_document(med_obj)
            self.fail("didn't raise exception on duplicate ID add")
        except KeyError:
            ...
        try:
            mmif_obj.add_document(med_obj, overwrite=True)
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
        self.assertIsInstance(mmif_obj['m1'], Document)
        self.assertIsInstance(mmif_obj['v1'], View)
        self.assertIsInstance(mmif_obj['v1:bb1'], Annotation)
        with self.assertRaises(KeyError):
            mmif_obj['asdf']
        a_view = View()
        a_view.id = 'm1'
        mmif_obj.add_view(a_view)
        with self.assertRaises(KeyError):
            mmif_obj['m1']
        document = Document()
        document.add_metadata('random_key', 'random_value')
        self.assertEqual(document.metadata['random_key'], 'random_value')


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

    def test_mmif_getitem_document(self):
        try:
            m1 = self.mmif_obj['m1']
            self.assertIs(m1, self.mmif_obj.documents.get('m1'))
        except TypeError:
            self.fail("__getitem__ not implemented")
        except KeyError:
            self.fail("didn't get document 'm1'")

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
                         'mmif': Mmif(example, frozen=False),
                         'annotations': [annotation
                                         for view in json.loads(example)['views']
                                         for annotation in view['annotations']]}
                     for i, example in self.examples.items()}

    def test_annotation_properties(self):
        props_json = self.data['mmif_example1']['annotations'][0]['properties']
        props_obj = DocumentMetadata(props_json)
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
                    new_mmif = Mmif(datum['json'], frozen=False)
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


class TestDocument(unittest.TestCase):

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
                         'mmif': Mmif(example, frozen=False),
                         'documents': json.loads(example)['documents']}
                     for i, example in self.examples.items()}

    def test_init(self):
        for i, datum in self.data.items():
            for j, document in enumerate(datum['documents']):
                try:
                    _ = Document(document)
                except Exception as ex:
                    self.fail(f"{type(ex)}: {str(ex)}: {i} {document['id']}")

    def test_document_metadata(self):
        metadata_json = self.data['mmif_example1']['documents'][1]['metadata']
        metadata_obj = DocumentMetadata(metadata_json)
        self.assertEqual(metadata_json, json.loads(metadata_obj.serialize()))

    def test_deserialize_with_whole_mmif(self):
        for i, datum in self.data.items():
            for j, document in enumerate(datum['documents']):
                try:
                    document_obj = datum['mmif'].get_document_by_id(document['id'])
                except KeyError:
                    self.fail(f"Document {document['id']} not found in MMIF")
                self.assertIsInstance(document_obj, Document)
                if 'metadata' in document:
                    self.assertIsInstance(document_obj.metadata, DocumentMetadata)
                if 'subdocuments' in document:
                    self.assertIsInstance(medium_obj.subdocuments, list)
                    for submedium in medium_obj.subdocuments:
                        self.assertIsInstance(submedium, Submedium)

    def test_deserialize_with_medium_str(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['documents']):
                medium_obj = Document(medium)
                self.assertIsInstance(medium_obj, Document)
                if 'metadata' in medium:
                    self.assertIsInstance(medium_obj.metadata, DocumentMetadata)
                if 'subdocuments' in medium:
                    self.assertIsInstance(medium_obj.subdocuments, list)
                    for submedium in medium_obj.subdocuments:
                        self.assertIsInstance(submedium, Submedium)

    def test_serialize_to_medium_str(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['documents']):
                medium_obj = Document(medium)
                serialized = json.loads(medium_obj.serialize())
                self.assertEqual(medium, serialized, f'Failed on {i}, {medium["id"]}')

    def test_serialize_with_whole_mmif(self):
        for i, datum in self.data.items():
            for j, medium in enumerate(datum['documents']):
                medium_serialized = json.loads(datum['mmif'].serialize())['documents'][j]
                self.assertEqual(medium, medium_serialized, f'Failed on {i}, {medium["id"]}')

    def test_add_metadata(self):
        for i, datum in self.data.items():
            for j in range(len(datum['json']['documents'])):
                medium_id = datum['json']['documents'][j]['id']
                metadata = datum['json']['documents'][j].get('metadata')
                if metadata:
                    removed_metadatum_key, removed_metadatum_value = list(metadata.items())[-1]
                    metadata.pop(removed_metadatum_key)
                    try:
                        new_mmif = Mmif(datum['json'], frozen=False)
                        new_mmif.get_medium_by_id(medium_id).add_metadata(removed_metadatum_key, removed_metadatum_value)
                        self.assertEqual(json.loads(datum['string']), json.loads(new_mmif.serialize()), f'Failed on {i}, {medium_id}')
                    except ValidationError:
                        continue


class TestDataStructure(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        self.datalist = self.mmif_obj.views
        self.freezable_datalist = self.mmif_obj.documents
        self.freezable_datadict = self.mmif_obj['v1'].metadata.contains

    def test_setitem(self):
        self.datalist['v1'] = View({'id': 'v1'})
        self.datalist['v2'] = View({'id': 'v2'})
        self.freezable_datalist['m1'] = Document({'id': 'm1'})
        self.freezable_datalist['m3'] = Document({'id': 'm3'})
        self.freezable_datadict['BoundingBox'] = Contain({"unit": "centimeters"})
        self.freezable_datadict['Segment'] = Contain({"unit": "milliseconds"})

    def test_getitem(self):
        self.assertIs(self.mmif_obj['v1'], self.datalist['v1'])
        self.assertIs(self.mmif_obj['m1'], self.freezable_datalist['m1'])
        self.assertIs(self.mmif_obj['v1'].metadata.contains['BoundingBox'], self.freezable_datadict['BoundingBox'])

    def test_append(self):
        self.assertTrue('v2' not in self.datalist._items)
        self.datalist.append(View({'id': 'v2'}))
        self.assertTrue('v2' in self.datalist._items)

        self.assertTrue('m3' not in self.freezable_datalist._items)
        self.freezable_datalist.append(Document({'id': 'm3'}))
        self.assertTrue('m3' in self.freezable_datalist._items)

    def test_append_overwrite(self):
        try:
            self.datalist.append(View({'id': 'v1'}))
            self.fail('appended without overwrite')
        except KeyError as ke:
            self.assertEqual('Key v1 already exists', ke.args[0])

        try:
            self.datalist.append(View({'id': 'v1'}), overwrite=True)
        except AssertionError:
            raise
        except Exception as ex:
            self.fail(ex.args[0])

        try:
            self.freezable_datalist.append(Document({'id': 'm2'}))
            self.fail('appended without overwrite')
        except KeyError as ke:
            self.assertEqual('Key m2 already exists', ke.args[0])

        try:
            self.freezable_datalist.append(Document({'id': 'm2'}), overwrite=True)
        except AssertionError:
            raise
        except Exception as ex:
            self.fail(ex.args[0])

    def test_membership(self):
        self.assertIn('v1', self.datalist)
        self.assertIn('m1', self.freezable_datalist)
        self.assertIn('BoundingBox', self.freezable_datadict)

        self.assertNotIn('v2', self.datalist)
        self.datalist['v2'] = View({'id': 'v2'})
        self.assertIn('v2', self.datalist)

        self.assertNotIn('m3', self.freezable_datalist)
        self.freezable_datalist['m3'] = Document({'id': 'm3'})
        self.assertIn('m3', self.freezable_datalist)

        self.assertNotIn('Segment', self.freezable_datadict)
        self.freezable_datadict['Segment'] = Contain({"unit": "milliseconds"})
        self.assertIn('Segment', self.freezable_datadict)

    def test_len(self):
        self.assertEqual(1, len(self.datalist))
        for i in range(2, 10):
            self.datalist[f'v{i}'] = View({'id': f'v{i}'})
            self.assertEqual(i, len(self.datalist))

        self.assertEqual(2, len(self.freezable_datalist))
        for i in range(3, 10):
            self.freezable_datalist[f'm{i}'] = Document({'id': f'm{i}'})
            self.assertEqual(i, len(self.freezable_datalist))

        self.assertEqual(1, len(self.freezable_datadict))
        for i in range(2, 10):
            self.freezable_datadict[f'Type{i}'] = Contain({"type": f"i"})
            self.assertEqual(i, len(self.freezable_datadict))

    def test_iter(self):
        for i in range(2, 10):
            self.datalist[f'v{i}'] = View({'id': f'v{i}'})
        for i in range(3, 10):
            self.freezable_datalist[f'm{i}'] = Document({'id': f'm{i}'})
        for i in range(2, 10):
            self.freezable_datadict[f'Type{i}'] = Contain({"type": f"i"})

        for expected_index, (actual_index, item) in zip(range(9), enumerate(self.datalist)):
            self.assertEqual(expected_index, actual_index)
            self.assertEqual(expected_index+1, int(item['id'][-1]))
        for expected_index, (actual_index, item) in zip(range(9), enumerate(self.freezable_datalist)):
            self.assertEqual(expected_index, actual_index)
            self.assertEqual(expected_index+1, int(item['id'][-1]))
        for expected_index, (actual_index, item) in zip(range(9), enumerate(self.freezable_datadict.values())):
            self.assertEqual(expected_index, actual_index)

    def test_dict_views(self):
        for i in range(2, 10):
            self.freezable_datadict[f'Type{i}'] = Contain({"type": f"i"})
        i = -1
        for i, item in enumerate(self.freezable_datadict.values()):
            pass
        self.assertEqual(8, i, 'values')
        i = -1
        for i, item in enumerate(self.freezable_datadict.keys()):
            pass
        self.assertEqual(8, i, 'keys')
        i = -1
        for i, (key, value) in enumerate(self.freezable_datadict.items()):
            pass
        self.assertEqual(8, i, 'items')

    def test_setitem_fail_on_reserved_name(self):
        for i, name in enumerate(self.datalist.reserved_names):
            try:
                self.datalist[name] = View({'id': f'v{i+1}'})
                self.fail("was able to setitem on reserved name")
            except KeyError as ke:
                self.assertEqual("can't set item on a reserved name", ke.args[0])

        for i, name in enumerate(self.freezable_datalist.reserved_names):
            try:
                self.freezable_datalist[name] = Document({'id': f'm{i+1}'})
                self.fail("was able to setitem on reserved name")
            except KeyError as ke:
                self.assertEqual("can't set item on a reserved name", ke.args[0])

        for i, name in enumerate(self.freezable_datadict.reserved_names):
            try:
                self.freezable_datadict[name] = Contain({'index': i})
                self.fail("was able to setitem on reserved name")
            except KeyError as ke:
                self.assertEqual("can't set item on a reserved name", ke.args[0])

    def test_get_reserved_name(self):
        self.assertEqual(self.datalist._items, self.datalist['_items'])
        self.assertEqual(self.datalist.reserved_names, self.datalist['reserved_names'])
        self.assertEqual(self.freezable_datalist._items, self.freezable_datalist['_items'])
        self.assertEqual(self.freezable_datalist.reserved_names, self.freezable_datalist['reserved_names'])
        self.assertEqual(self.freezable_datadict._items, self.freezable_datadict['_items'])
        self.assertEqual(self.freezable_datadict.reserved_names, self.freezable_datadict['reserved_names'])

    def test_get(self):
        self.assertEqual(self.datalist['v1'], self.datalist.get('v1'))
        self.assertEqual(self.freezable_datalist['m1'], self.freezable_datalist.get('m1'))
        self.assertEqual(self.freezable_datadict['BoundingBox'], self.freezable_datadict.get('BoundingBox'))
        self.assertIsNone(self.datalist.get('v5'))
        self.assertIsNone(self.freezable_datalist.get('m5'))
        self.assertIsNone(self.freezable_datadict.get('Segment'))

    def test_update(self):
        other_contains = """{
          "Segment": { "unit": "seconds" },
          "TimePoint": { "unit": "seconds" }
        }"""
        other_datadict = ContainsDict(other_contains)
        self.freezable_datadict.update(other_datadict)
        self.assertEqual(3, len(self.freezable_datadict))

        other_contains = """{
                  "Segment": { "unit": "seconds" },
                  "TimePoint": { "unit": "milliseconds" , "foo": "bar" }
                }"""
        other_datadict = ContainsDict(other_contains)

        try:
            self.freezable_datadict.update(other_datadict)
            self.fail('overwrote without error')
        except KeyError as ke:
            self.assertEqual("Key Segment already exists", ke.args[0])

        self.freezable_datadict.update(other_datadict, overwrite=True)
        self.assertEqual({"unit": "milliseconds", "foo": "bar"}, self.freezable_datadict['TimePoint']._serialize())


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
