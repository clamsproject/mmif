import logging
import unittest
from io import StringIO
from unittest.mock import patch
import json

from mmif.serialize import *
from mmif.serialize.model import FreezableMmifObject
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
            self.v1.metadata.document = 'm1'
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
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.v1.metadata.contains['Segment'] = Contain()
            self.fail('able to overwrite values in contains dict after deep freeze')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_deep_freeze_returns_true(self):
        self.assertTrue(self.v1.deep_freeze())


class TestFreezeDocument(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(examples['mmif_example1'], frozen=False)

        self.m2: Document = self.mmif_obj['m2']

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
            self.m2.subdocuments.append(Subdocument())
            self.fail('able to append to subdocuments list after deep freeze')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_deep_freeze_returns_true(self):
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


class TestFreezeSubdocumentsList(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(examples['mmif_example1'], frozen=False)
        self.subdocuments: SubdocumentsList = self.mmif_obj['m2'].subdocuments

    def test_deep_freeze(self):
        self.subdocuments['sm1'] = Subdocument({ "id": "sm1", "annotation": "bb1", "text": { "@value": "yelp" }})
        self.subdocuments.deep_freeze()
        try:
            self.subdocuments['sm1']['annotation'] = 'bb2'
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_invariance_after_freeze(self):
        before = json.loads(self.subdocuments.serialize())

        self.subdocuments.freeze()

        after = json.loads(self.subdocuments.serialize())

        self.assertEqual(before, after)

    def test_invariance_after_deep_freeze(self):
        before = json.loads(self.subdocuments.serialize())

        self.subdocuments.deep_freeze()

        after = json.loads(self.subdocuments.serialize())

        self.assertEqual(before, after)

    def test_proper_setitem_called_for_datalist(self):
        logger = logging.getLogger()
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.addHandler(logging.StreamHandler(fake_out))
            self.subdocuments['sub1'] = Subdocument()
        logger.setLevel(old_level)
        self.assertEqual('DataList.__setitem__', fake_out.getvalue().split()[2])

    def test_freezing_works_for_setitem(self):
        self.subdocuments.freeze()
        try:
            self.subdocuments['sub1'] = Subdocument()
            self.fail("was able to setitem")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_freezing_works_for_append(self):
        self.subdocuments.freeze()
        try:
            self.subdocuments.append(Subdocument())
            self.fail('able to append to subdocuments after freeze')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])


class TestFreezeMmif(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj_unfrozen = Mmif(examples['mmif_example1'], frozen=False)
        self.mmif_obj_frozen = Mmif(examples['mmif_example1'], frozen=True)
        self.mmif_obj_default = Mmif(examples['mmif_example1'])

    def test_freeze_mmif(self):
        self.assertFalse(self.mmif_obj_unfrozen.documents.is_frozen())
        self.mmif_obj_unfrozen.freeze_documents()
        self.assertTrue(self.mmif_obj_unfrozen.documents.is_frozen())

    def test_default_behavior_is_frozen(self):
        self.assertTrue(self.mmif_obj_default.documents.is_frozen())

    def test_kwarg(self):
        self.assertFalse(self.mmif_obj_unfrozen.documents.is_frozen())
        self.assertTrue(self.mmif_obj_frozen.documents.is_frozen())

    def test_try_frozen_add_document(self):
        try:
            self.mmif_obj_frozen.add_document(Document())
        except TypeError as te:
            self.assertEqual("MMIF object is frozen", te.args[0])

        self.mmif_obj_unfrozen.freeze_documents()
        try:
            self.mmif_obj_unfrozen.add_document(Document())
        except TypeError as te:
            self.assertEqual("MMIF object is frozen", te.args[0])


class TestFreezable(unittest.TestCase):
    def setUp(self) -> None:
        class MutableFoo:
            def __init__(self, *args, **kwargs):
                for k, v in kwargs.items():
                    self.__setattr__(k, v)

        self.obj1 = FreezableMmifObject({'a': 1, 'b': 2, 'c': 3})  # all fields contain constants
        self.obj2 = FreezableMmifObject({'a': 1, 'b': 2, 'c': 3, 'd': MutableFoo(x=1, y=2)})  # field 'd'
        self.mutable_foo = MutableFoo

    def test_deep_freeze_returns_true(self):
        self.assertTrue(self.obj1.deep_freeze())

    def test_deep_freeze_returns_false(self):
        self.assertIsInstance(self.obj2['d'], self.mutable_foo, 'type of "d" list should not be changed')
        fully_frozen = self.obj2.deep_freeze()
        if fully_frozen:  #
            try:
                self.obj2['d'].x = 2
                self.fail("should be frozen!")
            except TypeError as te:
                self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])
        self.assertFalse(fully_frozen, 'deep freeze should return false because "d" is mutable')
