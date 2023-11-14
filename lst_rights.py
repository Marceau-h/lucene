from pathlib import Path

import json

rights = set()
for path in Path('smaller').rglob('*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

        if "rights" in data:
            if isinstance(data['rights'], list):
                rights.update(data['rights'])
            else:
                rights.add(data['rights'])

rights = sorted(rights)

with open('rights.json', 'w', encoding='utf-8') as f:
    json.dump(rights, f, indent=4, ensure_ascii=False)
