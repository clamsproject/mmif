import json
import pathlib 

for jpath in pathlib.Path('.').glob('**/*.json'):
    with open(jpath) as jfile:
        try:
            j = json.load(jfile)
        except json.decoder.JSONDecodeError:
            print(f'erroneous json input at {jpath}')
        try:
            for view in j['views']:
                vid = view['id']
                for annotation in view['annotations']:
                    aid = annotation['properties']['id']
                    annotation['properties']['id'] = f'{vid}:{aid}'
        except KeyError as ke:
            print(f'no key {ke} in json input at {jpath}')
    with open(jpath.with_suffix('.new.json'), 'w') as ofile:
        json.dump(j, ofile, indent=2)
