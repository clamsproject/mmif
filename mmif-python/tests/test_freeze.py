import logging
import unittest
from io import StringIO
from unittest.mock import patch
import json

from mmif import __specver__
from mmif.serialize import *
from mmif.serialize.model import FreezableMmifObject
from mmif.serialize.view import AnnotationsList
from tests.mmif_examples import *


class TestFreezeView(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(MMIF_EXAMPLES['mmif_example1'], frozen=False)
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
            self.v1.metadata.contains[f'http://mmif.clams.ai/{__specver__}/vocabulary/TimeFrame'].producer = 'Phil'
            self.fail('able to set attribute of Contain object in frozen View')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.v1.metadata.contains['BoundingBox'] = Contain()
            self.fail('able to add to contains dict after deep freeze')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.v1.metadata.contains[f'http://mmif.clams.ai/{__specver__}/vocabulary/TimeFrame'] = Contain()
            self.fail('able to overwrite values in contains dict after deep freeze')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_deep_freeze_returns_true(self):
        self.assertTrue(self.v1.deep_freeze())


class TestFreezeDocument(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(MMIF_EXAMPLES['mmif_example1'], frozen=False)

        self.m1: Document = self.mmif_obj['m1']

    def test_freeze(self):
        self.m1.freeze()

        try:
            self.m1.id = 'm3'
            self.fail()
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_deep_freeze(self):
        self.m1.deep_freeze()

        try:
            self.m1.id = 'm3'
            self.fail("able to set top-level attribute")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.m1.properties.source = 'm1'
            self.fail("able to set lower-level attribute")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

        try:
            self.m1.properties.text.lang = 'spanish'
            self.fail('able to bypass immutability with @property setter')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_deep_freeze_returns_true(self):
        fully_frozen = self.m1.deep_freeze()
        self.assertTrue(fully_frozen)

    def test_invariance_after_freeze(self):
        before = json.loads(self.mmif_obj.serialize())

        self.mmif_obj['m1'].freeze()

        after = json.loads(self.mmif_obj.serialize())

        self.assertEqual(before, after)

    def test_invariance_after_deep_freeze(self):
        before = json.loads(self.mmif_obj.serialize())

        self.mmif_obj['m1'].deep_freeze()

        after = json.loads(self.mmif_obj.serialize())

        self.assertEqual(before, after)

    def test_proper_setitem_called_for_non_datalist(self):
        logger = logging.getLogger()
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.addHandler(logging.StreamHandler(fake_out))
            self.m1['properties']['id'] = 'm3'
        logger.setLevel(old_level)
        self.assertEqual('MmifObject.__setitem__', fake_out.getvalue().split()[2])


class TestFreezeAnnotationsList(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj = Mmif(MMIF_EXAMPLES['mmif_example1'], frozen=False)
        self.annotations: AnnotationsList = self.mmif_obj['v5'].annotations

    def test_deep_freeze(self):
        self.annotations['ann999'] = Annotation({"@type": "Annotation", "properties": {"id": "ann999"}})
        self.annotations.deep_freeze()
        try:
            self.annotations['ann999'].id = 'ann123'
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_invariance_after_freeze(self):
        before = json.loads(self.annotations.serialize())

        self.annotations.freeze()

        after = json.loads(self.annotations.serialize())

        self.assertEqual(before, after)

    def test_invariance_after_deep_freeze(self):
        before = json.loads(self.annotations.serialize())

        self.annotations.deep_freeze()

        after = json.loads(self.annotations.serialize())

        self.assertEqual(before, after)

    def test_proper_setitem_called_for_datalist(self):
        logger = logging.getLogger()
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            logger.addHandler(logging.StreamHandler(fake_out))
            self.annotations['bb1'] = Annotation()
        logger.setLevel(old_level)
        self.assertEqual('DataList.__setitem__', fake_out.getvalue().split()[2])

    def test_freezing_works_for_setitem(self):
        self.annotations.freeze()
        try:
            self.annotations['bb1'] = Annotation()
            self.fail("was able to setitem")
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])

    def test_freezing_works_for_append(self):
        self.annotations.freeze()
        try:
            self.annotations.append(Annotation())
            self.fail('able to append to subdocuments after freeze')
        except TypeError as te:
            self.assertEqual("frozen FreezableMmifObject should be immutable", te.args[0])


class TestFreezeMmif(unittest.TestCase):
    def setUp(self) -> None:
        self.mmif_obj_unfrozen = Mmif(MMIF_EXAMPLES['mmif_example1'], frozen=False)
        self.mmif_obj_frozen = Mmif(MMIF_EXAMPLES['mmif_example1'], frozen=True)
        self.mmif_obj_default = Mmif(MMIF_EXAMPLES['mmif_example1'])

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
