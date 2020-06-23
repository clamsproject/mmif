import unittest
import json
import sys
import traceback
import mmif
from tests.mmif_examples import *


class TestMmif(unittest.TestCase):

    def setUp(self) -> None:
        self.mmif_json: dict = json.loads(example1)

    def test_mmif_deserialize(self):
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = mmif.serialize.Mmif(json_str)
        except AssertionError:
            print("Assertion failed on: ")
            traceback.print_exc()
            self.fail()
        self.assertEqual(self.mmif_json, mmif_obj.serialize())

    def test_bad_mmif_deserialize_no_context(self):
        self.mmif_json.pop('@context')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = mmif.serialize.Mmif(json_str)
            self.fail()
        except AssertionError:
            pass

    def test_bad_mmif_deserialize_no_metadata(self):
        self.mmif_json.pop('metadata')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = mmif.serialize.Mmif(json_str)
            self.fail()
        except AssertionError:
            pass

    def test_bad_mmif_deserialize_no_media(self):
        self.mmif_json.pop('media')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = mmif.serialize.Mmif(json_str)
            self.fail()
        except AssertionError:
            pass

    def test_bad_mmif_deserialize_no_views(self):
        self.mmif_json.pop('views')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = mmif.serialize.Mmif(json_str)
            self.fail()
        except AssertionError:
            pass

    def test_bad_mmif_deserialize_no_contains(self):
        self.mmif_json.pop('contains')
        json_str = json.dumps(self.mmif_json)
        try:
            mmif_obj = mmif.serialize.Mmif(json_str)
            self.fail()
        except AssertionError:
            pass


if __name__ == '__main__':
    unittest.main()
