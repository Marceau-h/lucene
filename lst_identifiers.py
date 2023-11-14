from pathlib import Path

import json, re

comp = re.compile("oai:\w+.openedition.org:")

identifiers = set()
for path in Path('smaller').rglob('*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data['identifier'].startswith('oai:HAL:'):
        continue

    if data['identifier'].startswith('oai:cairn.info:'):
        continue

    if data['identifier'].startswith('oai:revues.org:'):
        continue

    if re.match(comp, data['identifier']):
        continue

    identifiers.add(data['identifier'])

    # if 'identifiers' in data:
    #     identifiers.update(data['identifiers'])

identifiers = sorted(identifiers)

with open('identifiers.json', 'w', encoding='utf-8') as f:
    json.dump(identifiers, f, indent=4, ensure_ascii=False)
