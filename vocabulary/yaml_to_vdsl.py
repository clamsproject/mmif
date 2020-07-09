import yaml
from vocabulary.publish import VERSION


def kv_to_vdsl(key, value):
    if isinstance(value, bool):
        value = value.__repr__().lower()
    elif isinstance(value, str):
        value = value.__repr__().replace("'", '"')
    return f'''{key} {value}'''


def dict_to_vdsl(name: str, dictionary: dict, level=1):
    out = name + ' { \n'
    for key, value in dictionary.items():
        line = '\t'*level
        if value is None:
            continue
        if not isinstance(value, dict):
            line += kv_to_vdsl(key, value)
        else:
            line += dict_to_vdsl(key, value, level+1)
        line += '\n'
        out += line
    return out + '\t'*(level-1) + '}'


def yaml_to_vdsl() -> str:
    out_str = f"""schema="http://schema.org"
iso="http://www.isocat.org/datcat"

version='{VERSION}'

"""

    terms = []

    with open("clams.vocabulary.yaml", 'r') as yaml_file:
        vocabulary = yaml.safe_load_all(yaml_file)

        for term in vocabulary:
            name = term.pop('name')
            parent = term.pop('parent')
            definition = term.pop('description')
            term_modified = {'parent': parent, 'definition': definition, **term}
            terms.append(dict_to_vdsl(name, term_modified))

    return out_str + '\n\n'.join(terms)


if __name__ == '__main__':
    with open('clams.vocabulary', 'w') as vdsl:
        vdsl.write(yaml_to_vdsl())
