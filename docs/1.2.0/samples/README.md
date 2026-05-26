# Migration notice

These example files are being moved to `clamsproject/mmif-python` (`tests/mmif-spec-examples/`)
as part of the MMIF 1.1.1 spec update. The raw JSON files contain `$TypeName_VER` template
variables that depend on build machinery being removed in 1.1.1.

Once `mmif-python` integration is complete and `tests/mmif_examples.py` no longer fetches
from this repo via URL, this directory can be deleted.

See: https://github.com/clamsproject/mmif-python (tests/mmif-spec-examples/README.md)
