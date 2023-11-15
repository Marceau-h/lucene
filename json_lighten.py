import re
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

openess = {
    "All rights reserved": False,
    "Cairn": False,
    "copyrighted": False,
    "http://creativecommons.org/licenses/by-nc-nd/": True,
    "http://creativecommons.org/licenses/by-nc-sa/": True,
    "http://creativecommons.org/licenses/by-nc/": True,
    "http://creativecommons.org/licenses/by-nd/": True,
    "http://creativecommons.org/licenses/by-sa/": True,
    "http://creativecommons.org/licenses/by/": True,
    "http://creativecommons.org/publicdomain/zero/1.0/": True,
    "http://hal.archives-ouvertes.fr/licences/copyright/": False,
    "http://hal.archives-ouvertes.fr/licences/etalab/": True,
    "http://hal.archives-ouvertes.fr/licences/publicDomain/": True,
    "https://creativecommons.org/licenses/by-nc-nd/4.0/": True,
    "https://creativecommons.org/licenses/by-nc-sa/4.0/": True,
    "https://creativecommons.org/licenses/by-nc/4.0/": True,
    "https://creativecommons.org/licenses/by-nd/4.0/": True,
    "https://creativecommons.org/licenses/by-sa/4.0/": True,
    "https://creativecommons.org/licenses/by/4.0/": True,
    "https://www.gnu.org/licenses/gpl-3.0-standalone.html": True,
    "https://www.openedition.org/12554": False,
    "info:eu-repo/semantics/OpenAccess": True,
    "info:eu-repo/semantics/embargoedAccess": True,
    "info:eu-repo/semantics/openAccess": True,
    "info:eu-repo/semantics/restrictedAccess": False,
}

openedition = re.compile("oai:\w+.openedition.org:")
bad_subject = re.compile("^\d+$")


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


def addtemp(data: dict, key: str, temp: dict) -> tuple[list, str, str]:
    lang = clean_lang(temp['lang'])
    if len(lang) not in (0, 2):
        print(f"Unexpected lang {lang}")
        print(temp)
        raise ValueError

    text = temp['text']
    # We remove the 's' at the end of the key and add the lang if it exists (e.g. 'titles' -> 'title_fr')
    # In the rares cases where leng is just an empty string, we add back the 's' (e.g. 'titles' -> 'titles')
    # To ensure the value to go back in the dict
    newkey = f"{key[:-1]}{f'-{lang.capitalize()}' if lang else 's'}"
    value = data.get(newkey, [])
    value.append(text)

    return value, newkey, lang


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


def is_open(rights: str) -> bool:
    if rights in openess:
        return openess[rights]
    else:
        print(f"Unexpected rights {rights}")
        raise ValueError


def json_2_smaller_1(data: dict) -> tuple[dict, set, set]:
    """Converts a json file to a pandas DataFrame"""

    # print(json.dumps(data, indent=4, sort_keys=True))

    # Shortcuts to make the dictionary creation below more readable
    langages = set()
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
            "nb_sets": len(new_data['sets']) if isinstance(new_data['sets'], list) else 1,
            "nb_contributors": len(new_data['contributors']) if isinstance(new_data['contributors'], list) else 1,
            "nb_creators": len(new_data['creators']) if isinstance(new_data['creators'], list) else 1,
            "nb_publishers": len(new_data['publishers']) if isinstance(new_data['publishers'], list) else 1,
            "nb_subjects": len(new_data['subjects']) if isinstance(new_data['subjects'], list) else 1,
            "nb_titles": len(new_data['titles']) if isinstance(new_data['titles'], list) else 1,
            "nb_languages": len(new_data['languages']) if isinstance(new_data['languages'], list) else 1,
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

    best_description = None
    en_found = False
    if isinstance(new_data['descriptions'], list):
        for description in new_data['descriptions']:
            if isinstance(description, dict):
                if '#text' not in description:
                    continue

                if description['@xml:lang'] == 'en':
                    best_description = description
                    en_found = True
                elif description['@xml:lang'] == 'fr':
                    best_description = description
                    break
                elif not en_found:
                    best_description = description
            elif not en_found:
                best_description = description
    else:
        best_description = new_data['descriptions']

    new_data['best_description'] = best_description['#text'] if isinstance(best_description, dict) else best_description

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
            value, newkey, lang = addtemp(temp, key, new_data[key])
            if lang:
                langages.add(lang)
            temp[newkey] = value
            toremove.append(key)
        elif isinstance(new_data[key], list):
            for item in new_data[key]:
                if isinstance(item, dict):
                    value, newkey, lang = addtemp(temp, key, item)
                    if lang:
                        langages.add(lang)
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
        new_data['languages'] = [clean_lang(new_data['languages'])]
    else:
        raise TypeError(f"Unexpected type {type(new_data['languages'])} for {new_data['languages']}")

    new_data['languages'] = list(set(new_data['languages']) | langages)

    if len(new_data['languages']) == 0:
        new_data['languages'] = ""
    elif len(new_data['languages']) == 1:
        new_data['languages'] = new_data['languages'][0]

    new_data['nb_languages'] = len(new_data['languages'])

    new_data.update(temp)

    # print(json.dumps(new_data, indent=4, sort_keys=True))

    for key in ("dates", "datestamp"):
        if isinstance(new_data[key], list):
            new_data[key] = [make_dates_great_again(date) for date in new_data[key]]
        elif isinstance(new_data[key], str):
            new_data[key] = make_dates_great_again(new_data[key])
        else:
            raise TypeError(f"Unexpected type {type(new_data[key])} for {new_data[key]}")

    if "identifier" not in new_data:
        raise KeyError(f"No identifier in {new_data}")

    if new_data['identifier'].startswith('oai:cairn.info:'):
        new_data["origin"] = "cairn"
    elif new_data['identifier'].startswith('oai:revues.org:'):
        new_data["origin"] = "open editions"
    elif new_data['identifier'].startswith('oai:HAL:'):
        new_data["origin"] = "hal"
    elif re.match(openedition, new_data['identifier']):
        new_data["origin"] = "open editions"
    else:
        new_data["origin"] = "unknown"

    new_data["id"] = new_data["identifier"]

    new_data["open_access"] = None

    if "rights" in new_data:
        # Checking for both because if empty, we want to keep none
        if isinstance(new_data["rights"], list):
            new_data["open_access"] = any(is_open(v) for v in new_data["rights"] if v)

        elif isinstance(new_data["rights"], str):
            if new_data["rights"]:
                new_data["open_access"] = is_open(new_data["rights"])

        else:
            raise TypeError(f"Unexpected type {type(new_data['rights'])} for {new_data['rights']}")

    new_data["cairn_free_consultation"] = None
    if "accessibilites" in new_data:
        # Checking for both because if empty, we want to keep none
        if new_data["accessibilites"] == "free access":
            new_data["cairn_free_consultation"] = True
        elif new_data["accessibilites"] == "restricted access":
            new_data["cairn_free_consultation"] = False

    # new_data["datestamp"] = new_data["datestamp"] or None
    for key, value in new_data.items():
        if isinstance(value, list):
            new_data[key] = [v for v in value if v != ""]
        elif value == "":
            new_data[key] = None

    if isinstance(new_data['sets'], list):
        ### Small cleaning in sets for searching
        temp = set()
        for e in new_data['sets']:
            if re.fullmatch(bad_subject, e):
                continue

            if ":" in e:
                e = ":".join(e.split(":")[1:])

            e = e.lower()

            temp.add(e)

        new_data['sets'] = list(temp)

    for key, value in new_data.items():
        if key.startswith("subject"):
            if isinstance(value, list):
                ### Small cleaning in sets for searching
                toremove = set()
                for e in value:
                    if re.fullmatch(bad_subject, e):
                        toremove.add(e)
                        # print(f"Removing {e}")

                new_data[key] = [e for e in value if e not in toremove]

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
        allkeys_out = {
            match[k] for k in allkeys_out if k != 'id' and not any((
                k.startswith('nb_'),
                k in ('best_title', 'best_description', 'open_access', 'origin', 'cairn_free_consultation'),
                k[-3] == '-'
            ))
        }

    except KeyError:
        print(allkeys_out)
        raise

    with open('allkeys_out_match.json', 'w') as f:
        json.dump(list(allkeys_out), f, indent=4, sort_keys=True)

    with open("difference.json", "w") as f:
        json.dump(list(allkeys - allkeys_out), f, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
