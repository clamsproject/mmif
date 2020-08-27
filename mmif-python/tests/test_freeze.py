import logging
import unittest
from io import StringIO
from unittest.mock import patch
import json

from mmif.serialize import *
from mmif.serialize.medium import SubmediaList
from tests.mmif_examples import *


class TestFreezeView(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(examples['mmif_example2'], frozen=False)
        self.v1: View = self.mmif_obj['v1']
        self.v2: View = self.mmif_obj['v2']

    def test_freeze(self):
        self.v1.freeze()

        try:
            self.v1.id = 'v3'
            self.fail()
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_deep_freeze(self):
        self.v1.deep_freeze()

        try:
            self.v1.id = 'v3'
            self.fail("able to set top-level attribute")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.v1.metadata.medium = 'm1'
            self.fail("able to set lower-level attribute")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.v1.metadata.contains['Segment'].producer = 'Phil'
            self.fail('able to set attribute of Contain object in frozen View')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.v1.metadata.contains['BoundingBox'] = Contain()
            self.fail('able to add to contains dict after deep freeze')
        except AssertionError:
            raise
        except Exception as ex:
            print(ex.args[0])

        try:
            self.v1.metadata.contains['Segment'] = Contain()
            self.fail('able to overwrite values in contains dict after deep freeze')
        except AssertionError:
            raise
        except Exception as ex:
            print(ex.args[0])


class TestFreezeMedium(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(examples['mmif_example1'], frozen=False)

        self.m2: Medium = self.mmif_obj['m2']

    def test_freeze(self):
        self.m2.freeze()

        try:
            self.m2.id = 'm3'
            self.fail()
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_deep_freeze(self):
        self.m2.deep_freeze()

        try:
            self.m2.id = 'm3'
            self.fail("able to set top-level attribute")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.m2.metadata.source = 'm1'
            self.fail("able to set lower-level attribute")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.m2.text.lang = 'spanish'
            self.fail('able to bypass immutability with @property setter')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.m2.submedia.append(Submedium())
            self.fail('able to append to submedia list after deep freeze')
        except AssertionError:
            raise
        except Exception as ex:
            print(ex.args[0])

    def test_bool_deep_freeze(self):
        fully_frozen = self.m2.deep_freeze()

        self.assertTrue(fully_frozen)

    def test_invariance_after_freeze(self):
        before = json.loads(self.mmif_obj.serialize())

        self.mmif_obj['m2'].freeze()

        after = json.loads(self.mmif_obj.serialize())

        self.assertEqual(before, after)

    def test_invariance_after_deep_freeze(self):
        before = json.loads(self.mmif_obj.serialize())

        self.mmif_obj['m2'].deep_freeze()

        after = json.loads(self.mmif_obj.serialize())

        self.assertEqual(before, after)

    def test_proper_setitem_called_for_non_datalist(self):
        logger = logging.getLogger()
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.addHandler(logging.StreamHandler(fake_out))
            self.m2['id'] = 'm3'
        logger.setLevel(old_level)
        self.assertEqual('MmifObject.__setitem__', fake_out.getvalue().split()[2])


class TestFreezeSubmediaList(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        self.submedia: SubmediaList = self.mmif_obj['m2'].submedia

    def test_deep_freeze(self):
        self.submedia['sm1'] = Submedium({ "id": "sm1", "annotation": "bb1", "text": { "@value": "yelp" }})
        self.submedia.deep_freeze()
        try:
            self.submedia['sm1']['annotation'] = 'bb2'
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_invariance_after_freeze(self):
        before = json.loads(self.submedia.serialize())

        self.submedia.freeze()

        after = json.loads(self.submedia.serialize())

        self.assertEqual(before, after)

    def test_invariance_after_deep_freeze(self):
        before = json.loads(self.submedia.serialize())

        self.submedia.deep_freeze()

        after = json.loads(self.submedia.serialize())

        self.assertEqual(before, after)

    def test_proper_setitem_called_for_datalist(self):
        logger = logging.getLogger()
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.addHandler(logging.StreamHandler(fake_out))
            self.submedia['sub1'] = Submedium()
        logger.setLevel(old_level)
        self.assertEqual('DataList.__setitem__', fake_out.getvalue().split()[2])

    def test_freezing_works_for_setitem(self):
        self.submedia.freeze()
        try:
            self.submedia['sub1'] = Submedium()
            self.fail("was able to setitem")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_freezing_works_for_append(self):
        self.submedia.freeze()
        try:
            self.submedia.append(Submedium())
            self.fail('able to append to submedia after freeze')
        except AssertionError:
            raise
        except Exception as ex:
            self.assertEqual("frozen FreezableMmifObject should be immutable", ex.args[0])


class TestFreezeMmif(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj_unfrozen = Mmif(examples['mmif_example1'], frozen=False)
        self.mmif_obj_frozen = Mmif(examples['mmif_example1'], frozen=True)
        self.mmif_obj_default = Mmif(examples['mmif_example1'])

    def test_freeze_mmif(self):
        self.assertFalse(self.mmif_obj_unfrozen.media.is_frozen())
        self.mmif_obj_unfrozen.freeze_media()
        self.assertTrue(self.mmif_obj_unfrozen.media.is_frozen())

    def test_default_behavior_is_frozen(self):
        self.assertTrue(self.mmif_obj_default.media.is_frozen())

    def test_kwarg(self):
        self.assertFalse(self.mmif_obj_unfrozen.media.is_frozen())
        self.assertTrue(self.mmif_obj_frozen.media.is_frozen())

    def test_try_frozen_add_medium(self):
        try:
            self.mmif_obj_frozen.add_medium(Medium())
        except TypeError as te:
            self.assertEqual("MMIF object is frozen", te.args[0])

        self.mmif_obj_unfrozen.freeze_media()
        try:
            self.mmif_obj_unfrozen.add_medium(Medium())
        except TypeError as te:
            self.assertEqual("MMIF object is frozen", te.args[0])
