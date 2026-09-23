import os
import re
import openpyxl
from common import database, DATA_PATH

IN = os.path.join(DATA_PATH, 'water_compliance', 'Water permit violations.xlsx')

table = database['sa_water_compliance']


def slugify(value, sep='_'):
    value = re.sub(r'[^\w\s]', ' ', value or '').strip().lower()
    return re.sub(r'\s+', sep, value)


def load():
    table.delete()
    wb = openpyxl.load_workbook(IN, read_only=True, data_only=True)
    total = 0

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = ws.iter_rows(values_only=True)
        next(rows)  # skip title row (e.g. "2017/2018")
        header_row = next(rows)
        header = [slugify(h) if h else f'col_{i}' for i, h in enumerate(header_row)]

        for row in rows:
            if len(row) < 2 or not row[1]:  # short/blank row or empty mine name -> skip  # mine name is empty -> skip
                continue
            data = dict(zip(header, row))
            data['reporting_year'] = sheet_name
            data.pop('none', None)  # drop the leading row-number column if unnamed
            table.insert(data)
            total += 1

    print(f"Loaded {total} rows across {len(wb.sheetnames)} sheets")


if __name__ == '__main__':
    load()