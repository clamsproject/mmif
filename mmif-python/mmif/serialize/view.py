from datetime import datetime
from typing import Dict, List, Union, Optional, Any

from .contain import Contain
from .model import MmifObject
from .annotation import Annotation


class View(MmifObject):
    id: str
    contains: Dict[str, Contain]
    annotations: List[Annotation]
    anno_ids = set()

    def __init__(self, view_obj: Union[str, dict] = None):
        self.id = ''
        self.contains = {}
        self.annotations = []
        super().__init__(view_obj)

    def _deserialize(self, view_dict: dict):
        self.id = view_dict['id']
        for at_type, contain in view_dict['metadata']['contains'].items():
            self.new_contain(at_type, contain['producer'])
        for anno_dict in view_dict['annotations']:
            self.add_annotation(Annotation(anno_dict))

    def new_contain(self, at_type: str, producer: str):
        new_contain = Contain()
        new_contain.producer = producer
        self.contains[at_type] = new_contain
        return new_contain

    def new_annotation(self, aid: str, at_type: str):
        new_annotation = Annotation()
        new_annotation.at_type = at_type
        new_annotation.id = aid
        return self.add_annotation(new_annotation)

    def add_annotation(self, annotation: Annotation) -> Annotation:
        self.annotations.append(annotation)
        self.anno_ids.add(annotation.id)
        return annotation


class ViewMetadata(MmifObject):
    medium: str
    timestamp: Optional[datetime] = None
    tool: str
    contains: Dict[str, Any]

