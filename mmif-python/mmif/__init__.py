from mmif.ver import __version__
from mmif.ver import __specver__
from mmif.vocabulary import *
from mmif.serialize import *

_res_pkg = 'res'
_ver_pkg = 'ver'
_vocabulary_pkg = 'vocabulary'
_schema_res_name = 'mmif.json'

# This package file used to have several importlib tricks
# in an attempt to enable re-use of some variable (mostly subpackage names)
# in `setup.py` by importing this.
# But I dropped that idea as it introduced hard-to-solve circular dependency problems.