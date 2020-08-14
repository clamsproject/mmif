_res_pkg = 'res'
_ver_pkg = 'ver'
__version__ = 'UNK'
__specver__ = 'UNK'
_schema_res_oriname = 'schema/mmif.json'
_schema_res_name = 'mmif.json'
_vocab_res_oriname = 'vocabulary/clams.vocabulary.yaml'
_vocab_res_name = 'clams.vocabulary.yaml'

try:
    import importlib
    i = importlib.import_module(f'{__name__}.{_ver_pkg}')
    __version__ = i.__version__  # pytype: disable=attribute-error
    __specver__ = i.__specver__  # pytype: disable=attribute-error
except ImportError:
    # don't set version
    pass

from mmif.serialize import *
from mmif.vocab import *
