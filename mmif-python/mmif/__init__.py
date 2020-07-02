_res_pkg = 'res'
_ver_pkg = 'ver'
__version__ = 'UNK'
_schema_res_name = 'mmif.json'
_vocab_res_name = 'clams.vocabulary.yaml'

try:
    import importlib
    i = importlib.import_module(f'{__name__}.{_ver_pkg}')
    __version__ = i.__version__
except ImportError:
    # don't set version
    pass

from mmif.serialize import *
from mmif.vocab import *
