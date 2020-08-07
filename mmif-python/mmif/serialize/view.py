from datetime import datetime
from typing import Dict, List, Union, Optional

from .annotation import Annotation
from .model import MmifObject


__all__ = ['View', 'ViewMetadata', 'Contain']


class View(MmifObject):
    id: str
    metadata: 'ViewMetadata'
    annotations: List['Annotation']
    anno_ids = set()

    def __init__(self, view_obj: Union[str, dict] = None):
        self.id = ''
        self.metadata = ViewMetadata()
        self.annotations = []
        super().__init__(view_obj)

    def _deserialize(self, view_dict: dict):
        _context = view_dict.get('_context')
        if _context is not None:
            self._context = _context
        self.id = view_dict['id']
        self.metadata = ViewMetadata(view_dict['metadata'])
        for anno_dict in view_dict['annotations']:
            self.add_annotation(Annotation(anno_dict))

    def new_contain(self, at_type: str, contain_dict: dict = None) -> Optional['Contain']:
        return self.metadata.new_contain(at_type, contain_dict)

    def new_annotation(self, aid: str, at_type: str):
        new_annotation = Annotation()
        new_annotation.at_type = at_type
        new_annotation.id = aid
        return self.add_annotation(new_annotation)

    def add_annotation(self, annotation: 'Annotation') -> 'Annotation':
        self.annotations.append(annotation)
        self.anno_ids.add(annotation.id)
        self.new_contain(annotation.at_type)
        return annotation


class ViewMetadata(MmifObject):
    medium: str
    timestamp: Optional[datetime] = None
    tool: str
    contains: Dict[str, 'Contain']

    def __init__(self, viewmetadata_obj: Union[str, dict] = None):
        self.medium = ''
        self.timestamp = datetime.now()
        self.tool = ''
        self.contains = {}
        super().__init__(viewmetadata_obj)

    def _deserialize(self, input_dict: dict) -> None:
        # TODO (angus-lherrou @ 8/4/2020): using __dict__ with potentially non-identifier
        #  keys "works" but is not pythonic so better to wrap a dict property.
        #  Unify implementations of this and MediumMetadata
        self.__dict__ = input_dict
        self.contains = {at_type: Contain(contain_obj) for at_type, contain_obj in input_dict.get('contains', {}).items()}

    def new_contain(self, at_type: str, contain_dict: dict = None) -> Optional['Contain']:
        # URI comparison hotfix
        absent = True
        for existing_type in self.contains.keys():
            if at_type.split('/')[-1] == existing_type.split('/')[-1]:
                absent = False
        if absent:
            new_contain = Contain(contain_dict)
            self.contains[at_type] = new_contain
            return new_contain


class Contain(MmifObject):
    producer: str
    gen_time: datetime

    def __init__(self, contain_obj: Union[str, dict] = None):
        self.producer = ''
        self.gen_time = datetime.now()     # datetime.datetime
        super().__init__(contain_obj)

    def _deserialize(self, input_dict: dict) -> None:
        super()._deserialize(input_dict)
        if 'gen_time' in self.__dict__ and isinstance(self.gen_time, str):
            self.gen_time = datetime.fromisoformat(self.gen_time)
