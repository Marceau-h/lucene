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

langages = sorted(l for l in langages if l)

with open('langages.txt', 'w', encoding='utf-8') as f:
    print('<?xml version="1.0" encoding="UTF-8" ?>\n<enumsConfig>\n\t<enum name="languages">', file=f)
    for langage in langages:
        print(f"\t<value>{langage}</value>", file=f)
    print('\t</enum>\n</enumsConfig>', file=f)

with open('langages.json', 'w', encoding='utf-8') as f:
    json.dump(langages, f, indent=2, ensure_ascii=False)


