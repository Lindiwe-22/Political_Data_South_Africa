import os
import re
import openpyxl
from common import database, DATA_PATH

IN = os.path.join(DATA_PATH, 'uk_payments', 'Company payments data.xlsx')

table = database['sa_uk_payments']


def slugify(value, sep='_'):
    value = re.sub(r'[^\w\s]', ' ', value or '').strip().lower()
    return re.sub(r'\s+', sep, value)


def parse_money(value):
    if value is None or value == '-':
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(',', '').strip())
    except ValueError:
        return None


def load():
    table.delete()
    wb = openpyxl.load_workbook(IN, read_only=True, data_only=True)
    ws = wb['Sheet1']
    rows = ws.iter_rows(values_only=True)

    header_row = next(rows)
    header = [slugify(h) if h else f'col_{i}' for i, h in enumerate(header_row) if h or i < 12]
    header = header[:12]  # ignore trailing empty columns

    last_company = None
    last_country = None
    count = 0

    for row in rows:
        row = row[:12]
        if not any(row):
            continue

        company = row[0].strip() if row[0] else last_company
        country = row[1].strip() if row[1] else last_country
        last_company, last_country = company, country

        if not company:
            continue

        province = row[4].strip() if row[4] else None
        if province and 'total' in province.lower():
            continue

        data = dict(zip(header, row))


        data = dict(zip(header, row))
        data['reporting_company'] = company
        data['reporting_country'] = country
        for money_field in ('tax_payment_us', 'royalties_payment_us',
                             'infrastructure_improvements_payment_us',
                             'other_payment_us', 'total_project_payment_us'):
            if money_field in data:
                data[money_field] = parse_money(data[money_field])

        table.insert(data)
        count += 1

    print(f"Loaded {count} rows")


if __name__ == '__main__':
    load()