from pathlib import Path

import json

doi = set()
for path in Path('smaller').rglob('*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)


    if "doi" in data and data["doi"]:
        if data["doi"].startswith("10."):
            continue
        doi.add(f"{data['doi_link']}\n{data['url']}\n")

with open('doi.txt', 'w', encoding='utf-8') as f:
    for path in sorted(doi):
        print(path, file=f)

print(*sorted(doi), sep='\n\n')
