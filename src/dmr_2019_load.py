import os
import re
import openpyxl
from common import database, DATA_PATH

IN = os.path.join(DATA_PATH, 'dmr_2019', '2019 Operating Mines and Quarries and Mineral Processing in the RSA.xlsx')

table = database['sa_dmr_2019_operations']


def slugify(value, sep='_'):
    value = re.sub(r'[^\w\s]', ' ', value or '').strip().lower()
    return re.sub(r'\s+', sep, value)


def clean(value):
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    return value

def split_entity_type(value):
    if not value:
        return None, None
    parts = re.split(r'\s{2,}', value.strip())
    parts = [p.strip() for p in parts if p.strip()]
    category = parts[0] if parts else None
    method = parts[1] if len(parts) > 1 else None
    return category, method


def load():
    table.delete()
    wb = openpyxl.load_workbook(IN, read_only=True, data_only=True)
    ws = wb['D1 2019']
    rows = list(ws.iter_rows(values_only=True))

    header_row = rows[0][:9]
    header = [slugify(h) for h in header_row]

    count = 0
    for row in rows[5:]:
        row = row[:9]
        if not row[0] or not row[1]:
            continue
        data = dict(zip(header, [clean(v) for v in row]))
        category, method = split_entity_type(data.get('entity_mining_type'))
        data['operation_category'] = category
        data['operation_method'] = method
        table.insert(data)
        count += 1

    print(f"Loaded {count} rows")


if __name__ == '__main__':
    load()