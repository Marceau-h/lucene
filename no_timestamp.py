from pathlib import Path

import json

no_tt = set()
for path in Path('smaller').rglob('*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

        if "datestamp" not in data or data["datestamp"] == "":
            no_tt.add(path)

print(len(no_tt))
print(no_tt)

# Seems like we dont have the timestamp of the collect for cairn.info
