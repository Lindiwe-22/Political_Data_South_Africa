import os
import re
import openpyxl
from common import database, DATA_PATH

IN = os.path.join(DATA_PATH, 'dmr', 'All-Operating-Mines-SA-Feb2026.xlsx')

table = database['sa_mines']


def slugify(value, sep='_'):
    value = re.sub(r'[^\w\s-]', '', value or '').strip().lower()
    return re.sub(r'\s+', sep, value)


def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def load():
    table.delete()
    wb = openpyxl.load_workbook(IN, read_only=True, data_only=True)
    ws = wb['data']
    rows = ws.iter_rows(values_only=True)
    header = [slugify(h) for h in next(rows)]

    for row in rows:
        if row[0] is None:
            continue
        data = dict(zip(header, row))
        if not data.get('mine_name'):
            continue
        for numeric_field in ('life_of_mine', 'workforce', 'start_year'):
            if numeric_field in data:
                data[numeric_field] = safe_int(data[numeric_field])
        table.insert(data)


if __name__ == '__main__':
    load()