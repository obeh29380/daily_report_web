import os
import json

import pandas as pd


def make_trash_json_from_xlsx():
    path = os.getcwd()
    print(path)
    df = pd.read_excel(f'{os.getcwd()}/app/tools/trash.xlsx')

    json_data = list()
    row_title = []  # [品目1, 品目2, ...]
    header_set = False
    for col_title, row_obj in df.items():
        if not header_set:
            for row in row_obj.values:
                row_title.append(row)
            header_set = True
            continue

        for i, row in enumerate(row_obj.values):
            if row == '':
                continue

            try:
                cost = int(row)
            except Exception:
                continue

            json_data.append(
                {
                    'dest': col_title,
                    'item': row_title[i],
                    'cost': cost
                }
            )

    json_file = open(f'{os.getcwd()}/app/tools/trash.json',
                     mode="w", encoding="utf-8")
    json.dump(json_data, json_file, indent=4, ensure_ascii=False)
    json_file.close()


if __name__ == "__main__":
    make_trash_json_from_xlsx()
