import unittest
import json
from mmif import Mmif, View, Annotation, AnnotationTypes
from mmif.serialize.model import MmifObjectEncoder
from tests.mmif_examples import *


class TestAnnotationTypes(unittest.TestCase):

    def test_encode(self):
        list_of_two = [AnnotationTypes.Annotation, AnnotationTypes.Chapter]
        string_of_two = '["http://mmif.clams.ai/0.1.0/vocabulary/Annotation", "http://mmif.clams.ai/0.1.0/vocabulary/Chapter"]'
        string_out = json.dumps(list_of_two, indent=None, cls=MmifObjectEncoder)
        self.assertEqual(string_of_two, string_out)

    def test_use_in_mmif(self):
        mmif_obj = Mmif(examples['example1'])
        view_obj: View = mmif_obj.get_view_by_id('v1')
        view_obj.new_annotation('p1', AnnotationTypes.Polygon)
        view_obj.new_annotation('bb2', AnnotationTypes.BoundingBox)
        self.assertEqual(list(view_obj.metadata.contains.keys()), ['BoundingBox', 'http://mmif.clams.ai/0.1.0/vocabulary/Polygon'])

    def test_serialize_within_mmif(self):
        mmif_obj = Mmif(examples['example1'])
        view_obj: View = mmif_obj.get_view_by_id('v1')
        anno_obj: Annotation = view_obj.new_annotation('p1', AnnotationTypes.Polygon)
        anno_obj.add_property('coordinates', [[20, 30], [20, 40], [60, 30]])
        expected = json.loads(Mmif(example1_modified).serialize())
        actual = json.loads(mmif_obj.serialize())
        expected['views'][0]['metadata']['contains']['http://mmif.clams.ai/0.1.0/vocabulary/Polygon']['gen_time'] = 'dummy'
        actual['views'][0]['metadata']['contains']['http://mmif.clams.ai/0.1.0/vocabulary/Polygon']['gen_time'] = 'dummy'
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
