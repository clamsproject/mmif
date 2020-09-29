import os

from mmif import __specver__
from string import Template

__all__ = ['JSON_STR',
           'MMIF_EXAMPLES',
           'SUB_EXAMPLES']


def substitute(example_dict: dict) -> dict:
    return dict((k, Template(v).substitute(specver=__specver__)) for k, v in example_dict.items())


raw_path = os.path.join('..', 'specifications', 'samples', 'everything', 'raw.json')

if os.getcwd().rsplit(os.path.sep)[-1] == 'tests':
    raw_path = os.path.join('..', raw_path)

with open(raw_path) as raw_json:
    JSON_STR = raw_json.read().replace('0.2.0', '${specver}')

example_templates = dict(
    mmif_example1=JSON_STR
)

sub_example_templates = {'doc_example': """{
  "@type": "http://mmif.clams.ai/${specver}/vocabulary/TextDocument",
    "properties": {
      "id": "td999",
      "mime": "text/plain",
      "location": "/var/archive/transcript-1000.txt" 
    }
}"""}

MMIF_EXAMPLES = substitute(example_templates)
SUB_EXAMPLES = substitute(sub_example_templates)
