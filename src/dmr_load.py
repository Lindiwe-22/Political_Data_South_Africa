import os
import csv
import re
from common import database, DATA_PATH

IN = os.path.join(DATA_PATH, 'dmr', 'dmr.csv')

table = database['sa_mines']


def slugify(value, sep='_'):
    value = re.sub(r'[^\w\s-]', '', value or '').strip().lower()
    return re.sub(r'\s+', sep, value)


def convert_row(row):
    data = {}
    for key, value in row.items():
        key = slugify(key, sep='_')
        data[key] = value.strip() if isinstance(value, str) else value
    return data


def load():
    table.delete()
    with open(IN, 'r', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            row = convert_row(row)
            if not row['mine_name']:
                continue
            table.insert(row)


if __name__ == '__main__':
    load()