from mmif.serialize import *
from mmif.vocab import *

_res_pkg = 'res'
_ver_pkg = 'ver'
__version__ = 'UNK'
_schema_res_name = 'mmif.json'

try:
    import importlib
    i = importlib.import_module(f'{__name__}.{_ver_pkg}')
    __version__ = i.__version__
except ImportError:
    # don't set version
    pass
