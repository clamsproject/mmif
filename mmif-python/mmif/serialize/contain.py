from typing import Union

from .model import MmifObject


class Contain(MmifObject):
    producer: str
    gen_time: str

    def __init__(self, contain_obj: Union[str, dict] = None):
        self.producer = ''
        self.gen_time = None     # datetime.datetime
        super().__init__(contain_obj)

    def _deserialize(self, contain_dict: dict):
        pass
