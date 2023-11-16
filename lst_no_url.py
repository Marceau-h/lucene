from pathlib import Path

import json

missing_url = set()
missing_doi = set()
for path in Path('smaller').rglob('*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "url" not in data or not data["url"]:
        # print(path)

        missing_url.add(path)

    if "doi" not in data or not data["doi"]:
        # print(path)

        missing_doi.add(path)


with open('missing.txt', 'w', encoding='utf-8') as f:
    for path in sorted(missing_url):
        print(path, file=f)

with open('missing_doi.txt', 'w', encoding='utf-8') as f:
    for path in sorted(missing_doi):
        print(path, file=f)
