from pathlib import Path
import json

import pandas as pd


def json_to_df(data: dict) -> pd.DataFrame:
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

    for key, value in new_data.items():
        if isinstance(value, list):
            if any(isinstance(v, dict) for v in value):
                new = [
                    f"{v['#text']}@LANG_CODE=({v['@xml:lang']})"
                    if isinstance(v, dict) else v
                    for v in value
                    if v is not None
                ]
            else:
                new = [v for v in value if v is not None]

            new_data[key] = '|'.join(new)

        elif isinstance(value, dict):
            new_data[key] = f"{value['#text']}@LANG_CODE=({value['@xml:lang']})"



    # print(json.dumps(new_data, indent=4, sort_keys=True))

    return pd.DataFrame.from_records([new_data])


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

    df = pd.concat(dfs, ignore_index=True)

    df.to_csv('data.csv', index=False)


if __name__ == '__main__':
    main()
