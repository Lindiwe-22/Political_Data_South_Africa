import re
from common import database

table_in = database['sa_pa_financial']
table_out = database['sa_wealth_timeline']

def parse_number_field(value):
    if not value:
        return None
    value = value.replace(' ', '').strip()
    try:
        return float(value)
    except ValueError:
        return None


def parse_rand_amount(text):
    if not text:
        return None
    text = text.strip()

    def fix_separators(s):
        s = re.sub(r',(\d{1,2})(?!\d)', r'.\1', s)
        s = re.sub(r'\s(\d{2})(?!\d)$', r'.\1', s.strip())
        s = s.replace(',', '')
        s = s.replace(' ', '')
        return s

    match = re.search(r'[\d][\d,.\s]*', text)
    if not match:
        return None
    cleaned = fix_separators(match.group(0))
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_nominal_value(raw, number_field):
    """Returns (value, confidence). confidence is one of:
    'total', 'per_share_calculated', 'per_share_unresolved',
    'per_share_suspicious', 'undisclosed'."""
    if not raw:
        return None, 'undisclosed'

    text = raw.strip()
    if not text or 'no value' in text.lower():
        return None, 'undisclosed'

    bracket_match = re.search(r'\[R?\s*([\d,.\s]+)\s*total\]', text, re.IGNORECASE)
    if bracket_match:
        val = parse_rand_amount(bracket_match.group(1))
        return (val, 'total') if val is not None else (None, 'undisclosed')

    cleaned = re.sub(r'[+\-±\\]+', ' ', text)  # note: '/' NOT stripped, it's part of "p/s"
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    is_per_share = bool(re.search(r'per\s*share|p\s*/\s*s|ps\b', cleaned, re.IGNORECASE))

    million_match = re.search(r'R?\s*([\d,.\s]+)\s*(million|ml)\b', cleaned, re.IGNORECASE)
    if million_match:
        base = parse_rand_amount(million_match.group(1))
        if base is not None:
            return base * 1_000_000, 'total'

    base_value = parse_rand_amount(cleaned)
    if base_value is None:
        return None, 'undisclosed'

    if is_per_share:
        if base_value > 5000:  # implausible per-share price; likely a source data-entry error
            return base_value, 'per_share_suspicious'
        shares = parse_number_field(number_field)
        if shares is not None:
            return base_value * shares, 'per_share_calculated'
        return base_value, 'per_share_unresolved'

    return base_value, 'total'


def build():
    table_out.delete()
    rows_by_person_year = {}

    for row in table_in:
        year_match = re.search(r'(20\d{2})', row.get('report') or '')
        if not year_match:
            continue
        year = int(year_match.group(1))

        value, confidence = parse_nominal_value(row.get('nominal_value'), row.get('number'))

        key = (row['person_id'], year)
        if key not in rows_by_person_year:
            rows_by_person_year[key] = {
                'person_name': row.get('person_name'),
                'total_confirmed': 0.0,
                'count_confirmed': 0,
                'count_unresolved': 0,
                'count_suspicious': 0,
                'count_undisclosed': 0,
            }
        bucket = rows_by_person_year[key]

        if confidence in ('total', 'per_share_calculated') and value is not None:
            bucket['total_confirmed'] += value
            bucket['count_confirmed'] += 1
        elif confidence == 'per_share_unresolved':
            bucket['count_unresolved'] += 1
        elif confidence == 'per_share_suspicious':
            bucket['count_suspicious'] += 1
        else:
            bucket['count_undisclosed'] += 1

    for (person_id, year), b in rows_by_person_year.items():
        table_out.insert({
            'person_id': person_id,
            'person_name': b['person_name'],
            'year': year,
            'total_declared_value': b['total_confirmed'],
            'num_confirmed_interests': b['count_confirmed'],
            'num_unresolved_interests': b['count_unresolved'],
            'num_suspicious_interests': b['count_suspicious'],
            'num_undisclosed_interests': b['count_undisclosed'],
        })

    print(f"Built {len(rows_by_person_year)} person-year records")


if __name__ == '__main__':
    build()