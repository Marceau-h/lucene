from pathlib import Path
import json

import polars as pl


def json_to_df(data: dict) -> pl.DataFrame:
    """Converts a json file to a pandas DataFrame"""

    # print(json.dumps(data, indent=4, sort_keys=True))

    # Shortcuts to make the dictionary creation below more readable
    header = data['header']
    oai = data['metadata']['oai_dc:dc']

    # Dictionary creation, we squeeze the nested dictionaries into one, much more simple
    new_data = {
        "datestamp": header['datestamp'],
        "identifier": header['identifier'],
        "sets": header['setSpec'],
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
    print(best_title)

    # for key, value in new_data.items():
    #     if isinstance(value, list):
    #         if any(isinstance(v, dict) for v in value):
    #             new = [
    #                 f"{v['#text']}@LANG_CODE=({v['@xml:lang']})"
    #                 if isinstance(v, dict) else v
    #                 for v in value
    #                 if v is not None
    #             ]
    #         else:
    #             new = [v for v in value if v is not None]
    #
    #         new_data[key] = '|'.join(new)
    #
    #     elif isinstance(value, dict):
    #         new_data[key] = f"{value['#text']}@LANG_CODE=({value['@xml:lang']})"

    temp = {}
    for key in ("titles", "descriptions", "subjects"):
        if isinstance(new_data[key], dict):
            addtemp(temp, key, new_data[key])
            del new_data[key]
        elif isinstance(new_data[key], list):
            for item in new_data[key]:
                if isinstance(item, dict):
                    addtemp(temp, key, item)
                    new_data[key].remove(item)
                elif isinstance(item, str):
                    pass
                else:
                    raise TypeError(f"Unexpected type {type(item)} for {item}")
        elif isinstance(new_data[key], str):
            pass
        else:
            raise TypeError(f"Unexpected type {type(new_data[key])} for {new_data[key]}")

    new_data.update(temp)

    # print(json.dumps(new_data, indent=4, sort_keys=True))

    return pl.from_records([new_data])


def addtemp(data: dict, key: str, temp: dict) -> None:
    lang = temp['@xml:lang']
    text = temp['#text']
    newkey = f"{key[:-1]}_{lang}"
    if newkey in data:
        data[newkey].append(text)
    else:
        data[newkey] = [text]


def main():
    # jsons = Path("/home/marceau/PycharmProjects/cartographie/scripts/EIH_oai/records_full").glob('**/*.json')
    jsons = Path('test').glob('*.json')
    # for file in jsons:
    #     print(file)
    #
    #     with open(file) as f:
    #         data = json.load(f)
    #
    #     df = json_to_df(data)

    dfs = []
    for file in jsons:
        print(file)

        with open(file) as f:
            data = json.load(f)

        dfs.append(json_to_df(data))

    df = pl.concat(dfs)  # , ignore_index=True)

    df.to_csv('data.csv')  # , index=False)


if __name__ == '__main__':
    main()
