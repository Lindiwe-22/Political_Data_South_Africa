import os
import xlrd
from common import database, DATA_PATH

FILES = [
    os.path.join(DATA_PATH, 'iec', '8_4_Published_Declarations_Report.xls'),
    os.path.join(DATA_PATH, 'iec', '9_1_Published_Declarations_Report.xls'),
]

table = database['sa_iec_donations']

COL_PARTY = 2
COL_DATE = 4
COL_DONOR = 8
COL_TYPE = 15
COL_AMOUNT_QUARTER = 18
COL_AMOUNT_ACCUM = 24


def load_file(path):
    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_index(0)
    source_file = os.path.basename(path)
    count = 0
    for i in range(23, ws.nrows):
        row = ws.row_values(i)
        party = row[COL_PARTY].strip() if isinstance(row[COL_PARTY], str) else row[COL_PARTY]
        donor = row[COL_DONOR].strip() if isinstance(row[COL_DONOR], str) else row[COL_DONOR]
        if not party or not donor:
            continue
        if party.upper().startswith('TOTAL') or party.upper() == 'PARTY NAME':
            continue
        data = {
            'source_file': source_file,
            'party_name': party,
            'date_of_receipt': row[COL_DATE] or None,
            'donor_name': row[COL_DONOR] or None,
            'donation_type': row[COL_TYPE] or None,
            'amount_quarter': row[COL_AMOUNT_QUARTER] or None,
            'amount_accumulative': row[COL_AMOUNT_ACCUM] or None,
        }
        table.insert(data)
        count += 1
    print(f"{source_file}: loaded {count} rows")


def load():
    table.delete()
    for f in FILES:
        load_file(f)


if __name__ == '__main__':
    load()