from pathlib import Path
import json
from datetime import datetime

from redo_folder import main as redo_folder

match = {
    "datestamp": "datestamp",
    "identifier": "identifier",
    "sets": "setSpec",
    "contributors": "dc:contributor",
    "creators": "dc:creator",
    "dates": "dc:date",
    "descriptions": "dc:description",
    "identifiers": "dc:identifier",
    "languages": "dc:language",
    "publishers": "dc:publisher",
    "relations": "dc:relation",
    "rights": "dc:rights",
    "sources": "dc:source",
    "subjects": "dc:subject",
    "titles": "dc:title",
    "types": "dc:type",
    "couvertures": "dc:coverage",
    "accessibilites": "dcterms:accessRights"
}


def format_lang_n_types(text: dict) -> dict | str:
    try:
        if isinstance(text, dict):
            if '@xml:lang' in text:
                return {
                    'text': text['#text'],
                    'lang': text['@xml:lang']
                }
            elif '@xsi:type' in text:
                if "dcterms:W3CDTF" == text['@xsi:type']:
                    return datetime.fromisoformat(text['#text']).strftime("%Y-%m-%dT%H:%M:%SZ")
    except KeyError:
        print(text)
        return ""
    raise ValueError(f"Unknown format: {text}")


def json_2_smaller_1(data: dict) -> tuple[dict, set, set]:
    """Converts a json file to a pandas DataFrame"""

    # print(json.dumps(data, indent=4, sort_keys=True))

    # Shortcuts to make the dictionary creation below more readable
    header = data['header']
    oai = data['metadata']['oai_dc:dc']

    allkeys = {k for k in header.keys()} | {k for k in oai.keys()}

    # Dictionary creation, we squeeze the nested dictionaries into one, much more simple
    new_data = {
        "datestamp": header.get('datestamp', ""),
        "identifier": header['identifier'],  # This one is mandatory
        "sets": header.get('setSpec', ""),
        # All the following are in plural because they can be multiple, we'll need to remove the lists
        # But they are not always present, so we need to account for that
        "contributors": oai.get("dc:contributor", ""),
        "creators": oai.get("dc:creator", ""),
        "dates": oai.get("dc:date", ""),
        "descriptions": oai.get("dc:description", ""),
        "identifiers": oai.get("dc:identifier", ""),
        "languages": oai.get("dc:language", ""),
        "publishers": oai.get("dc:publisher", ""),
        "relations": oai.get("dc:relation", ""),
        "rights": oai.get("dc:rights", ""),
        "sources": oai.get("dc:source", ""),
        "subjects": oai.get("dc:subject", ""),
        "titles": oai.get("dc:title", ""),
        "types": oai.get("dc:type", ""),
        "couvertures": oai.get("dc:coverage", ""),
        "accessibilites": oai.get("dcterms:accessRights", ""),
    }

    new_data.update(
        {
            "nb_sets": len(new_data['sets']),
            "nb_contributors": len(new_data['contributors']),
            "nb_creators": len(new_data['creators']),
            "nb_publishers": len(new_data['publishers']),
            "nb_subjects": len(new_data['subjects']),
            "nb_titles": len(new_data['titles']),
        }
    )

    best_title = None
    en_found = False
    if isinstance(new_data['titles'], list):
        for title in new_data['titles']:
            if isinstance(title, dict):
                if title['@xml:lang'] == 'en':
                    best_title = title
                    en_found = True
                elif title['@xml:lang'] == 'fr':
                    best_title = title
                    break
                elif not en_found:
                    best_title = title
            elif not en_found:
                best_title = title
    else:
        best_title = new_data['titles']

    new_data['best_title'] = best_title
    # print(best_title)

    for key, value in new_data.items():
        if isinstance(value, list):
            if any(isinstance(v, dict) for v in value):
                new = [
                    format_lang_n_types(v)
                    if isinstance(v, dict) else v
                    for v in value
                    if v is not None
                ]
            else:
                new = [v for v in value if v is not None]

            new_data[key] = new

        elif isinstance(value, dict):
            try:
                code_key = ""
                if "@xml:lang" in value:
                    code_key = "@xml:lang"
                elif "@xsi:type" in value:
                    code_key = "@xsi:type"
                elif "@xsi:schemaLocation" in value:
                    code_key = "@xsi:schemaLocation"

                new_data[key] = format_lang_n_types(value)

            except KeyError:
                print(value)
                raise

    allkeys_out = {k for k in new_data.keys()}

    # print(json.dumps(new_data, indent=4, sort_keys=True))

    return new_data, allkeys, allkeys_out


def main():
    # jsons = Path("/home/marceau/PycharmProjects/cartographie/scripts/EIH_oai/records_full").glob('**/*.json')
    jsons = Path('test').glob('*.json')
    new_jsons = Path('smaller')
    # new_jsons.mkdir(exist_ok=True)
    redo_folder(new_jsons)

    allkeys = set()
    allkeys_out = set()

    for file in jsons:
        # print(file)

        with open(file) as f:
            with open(new_jsons / file.name, 'w') as new_f:
                data = json.load(f)
                new_data, keys, keys_out = json_2_smaller_1(data)
                json.dump(new_data, new_f, indent=4, sort_keys=True)

                allkeys |= keys
                allkeys_out |= keys_out


    with open('allkeys.json', 'w') as f:
        json.dump(list(allkeys), f, indent=4, sort_keys=True)

    with open('allkeys_out.json', 'w') as f:
        json.dump(list(allkeys_out), f, indent=4, sort_keys=True)

    allkeys_out = {match[k] for k in allkeys_out if not k.startswith('nb_') and k != 'best_title'}

    with open('allkeys_out_match.json', 'w') as f:
        json.dump(list(allkeys_out), f, indent=4, sort_keys=True)

    with open("difference.json", "w") as f:
        json.dump(list(allkeys - allkeys_out), f, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
