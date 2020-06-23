import unittest
import os
import json
import mmif


class TestMmif(unittest.TestCase):
    def test_mmif_deserialize(self):
        with open(os.path.join('..', 'mmif', 'mmif_example_for_reference.json'), 'r') as json_file:
            json_str = json_file.read()
            mmif_obj = mmif.serialize.Mmif(json_str)
            self.assertEqual(json.loads(json_str), mmif_obj.serialize())


if __name__ == '__main__':
    unittest.main()
