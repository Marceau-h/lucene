from pathlib import Path

import json

langages = set()
for path in Path('smaller').rglob('*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # print(data['languages'])
        if isinstance(data['languages'], list):
            langages.update(data['languages'])
        else:
            langages.add(data['languages'])

langages = sorted(langages)

for langage in langages:
    print(f"<value>{langage}</value>")
