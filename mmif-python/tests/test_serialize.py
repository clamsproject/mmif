import unittest
import json
import traceback
import mmif
from tests.mmif_examples import *


class TestMmif(unittest.TestCase):
    def test_mmif_deserialize(self):
        try:
            mmif_obj = mmif.serialize.Mmif(example1)
        except AssertionError:
            traceback.print_exc()
            self.fail()
        self.assertEqual(json.loads(example1), mmif_obj.serialize())

    def test_bad_mmif_deserialize(self):
        try:
            mmif_obj = mmif.serialize.Mmif(example2)
            self.fail()
        except AssertionError:
            traceback.print_exc()



if __name__ == '__main__':
    unittest.main()
