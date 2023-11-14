from pathlib import Path

import json

accessibilites = set()
for path in Path('smaller').rglob('*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

        if "accessibilites" in data:
            if isinstance(data['accessibilites'], list):
                accessibilites.update(data['accessibilites'])
                print("list")
            else:
                accessibilites.add(data['accessibilites'])

accessibilites = sorted(accessibilites)

with open('accessibilites.json', 'w', encoding='utf-8') as f:
    json.dump(accessibilites, f, indent=4, ensure_ascii=False)
