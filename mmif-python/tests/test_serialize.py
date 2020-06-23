import unittest
import json
import mmif
from tests.mmif_examples import example1


class TestMmif(unittest.TestCase):
    def test_mmif_deserialize(self):
        mmif_obj = mmif.serialize.Mmif(example1)
        self.assertEqual(json.loads(example1), mmif_obj.serialize())


if __name__ == '__main__':
    unittest.main()
