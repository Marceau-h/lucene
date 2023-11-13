from pathlib import Path
import json
from datetime import datetime

from redo_folder import main as redo_folder

match = {
    "datestamp": "datestamp",
    "identifier": "identifier",
    "id": "identifier",
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


def addtemp(data: dict, key: str, temp: dict) -> tuple[list, str]:
    lang = clean_lang(temp['lang'])
    if len(lang) not in (0, 2):
        print(f"Unexpected lang {lang}")
        print(temp)
        raise ValueError

    text = temp['text']
    # We remove the 's' at the end of the key and add the lang if it exists (e.g. 'titles' -> 'title_fr')
    # In the rares cases where leng is just an empty string, we add back the 's' (e.g. 'titles' -> 'titles')
    # To ensure the value to go back in the dict
    newkey = f"{key[:-1]}{f'_{lang}' if lang else 's'}"
    value = data.get(newkey, [])
    value.append(text)

    return value, newkey


def make_dates_great_again(bad_date: str) -> str:
    if not bad_date:
        return ""  # Can't do anything with an empty string

    if bad_date.startswith("info:eu-repo/date/embargoEnd/"):
        bad_date = bad_date[29:]  # We remove the prefix

    if len(bad_date) == 4:
        try:
            date = datetime.strptime(bad_date, "%Y")
            return date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise

    if len(bad_date) == 7:
        try:
            date = datetime.strptime(bad_date, "%Y-%m")
            return date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise

    if len(bad_date) == 10:
        try:
            date = datetime.strptime(bad_date, "%Y-%m-%d")
            return date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise

    try:
        date = datetime.fromisoformat(bad_date)
        return date.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        print(bad_date)
        return ""


def clean_lang(lang: str) -> str:
    match lang:
        case "eng":
            return "en"
        case "ang":
            return "en"
        case "fre":
            return "fr"
        case "fra":
            return "fr"
        case _:
            if len(lang) in (0, 2):
                return lang
            else:
                print(f"Unexpected lang {lang}")
                raise ValueError


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
            "nb_languages": len(new_data['languages']),
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

    new_data['best_title'] = best_title['#text'] if isinstance(best_title, dict) else best_title
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

    temp = {}
    toremove = []
    for key in ("titles", "descriptions", "subjects"):
        if isinstance(new_data[key], dict):
            value, newkey = addtemp(temp, key, new_data[key])
            temp[newkey] = value
            toremove.append(key)
        elif isinstance(new_data[key], list):
            for item in new_data[key]:
                if isinstance(item, dict):
                    value, newkey = addtemp(temp, key, item)
                    temp[newkey] = value
                    toremove.append((key, item))
                elif isinstance(item, str):
                    pass
                else:
                    raise TypeError(f"Unexpected type {type(item)} for {item}")
        elif isinstance(new_data[key], str):
            pass
        else:
            raise TypeError(f"Unexpected type {type(new_data[key])} for {new_data[key]}")

    for item in toremove:
        if isinstance(item, str):
            del new_data[item]
        elif isinstance(item, tuple):
            new_data[item[0]].remove(item[1])
        else:
            raise TypeError(f"Unexpected type {type(item)} for {item}")

    if isinstance(new_data['languages'], list):
        new_data['languages'] = [clean_lang(lang) for lang in new_data['languages']]
    elif isinstance(new_data['languages'], str):
        new_data['languages'] = clean_lang(new_data['languages'])
    else:
        raise TypeError(f"Unexpected type {type(new_data['languages'])} for {new_data['languages']}")

    new_data.update(temp)

    # print(json.dumps(new_data, indent=4, sort_keys=True))

    for key in ("dates", "datestamp"):
        if isinstance(new_data[key], list):
            new_data[key] = [make_dates_great_again(date) for date in new_data[key]]
        elif isinstance(new_data[key], str):
            new_data[key] = make_dates_great_again(new_data[key])
        else:
            raise TypeError(f"Unexpected type {type(new_data[key])} for {new_data[key]}")

    new_data["id"] = new_data["identifier"]

    allkeys_out = {k for k in new_data.keys()}

    return new_data, allkeys, allkeys_out


def main():
    jsons = Path("/home/marceau/PycharmProjects/cartographie/scripts/EIH_oai/records_full").glob('**/*.json')
    # jsons = Path('test').glob('*.json')
    new_jsons = Path('smaller')
    # new_jsons.mkdir(exist_ok=True)
    redo_folder(new_jsons)

    allkeys = set()
    allkeys_out = set()

    for file in jsons:
        # print(file)

        with open(file, encoding="utf-8") as f:
            with open(new_jsons / file.name, 'w', encoding="utf-8") as new_f:
                data = json.load(f)
                new_data, keys, keys_out = json_2_smaller_1(data)
                json.dump(new_data, new_f, indent=4, sort_keys=True, ensure_ascii=False)

                allkeys |= keys
                allkeys_out |= keys_out

    with open('allkeys.json', 'w') as f:
        json.dump(list(allkeys), f, indent=4, sort_keys=True)

    with open('allkeys_out.json', 'w') as f:
        json.dump(list(allkeys_out), f, indent=4, sort_keys=True)

    try:
        # checking k == 'id' prevents IndexError, checking k[-3] == '_' for lang specific keys
        # but "id"[-3] doesn't exist, so chexking it forst prevents python from checking the second,
        # longer to compute, condition
        allkeys_out = {match[k] for k in allkeys_out if k != 'id' and not any((
            k.startswith('nb_'), k == 'best_title', k[-3] == '_'))}
    except KeyError:
        print(allkeys_out)
        raise

    with open('allkeys_out_match.json', 'w') as f:
        json.dump(list(allkeys_out), f, indent=4, sort_keys=True)

    with open("difference.json", "w") as f:
        json.dump(list(allkeys - allkeys_out), f, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
