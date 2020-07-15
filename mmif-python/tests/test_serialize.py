import unittest
import json

import pytest
from jsonschema import ValidationError
from mmif.serialize import Mmif
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


if __name__ == '__main__':
    unittest.main()
