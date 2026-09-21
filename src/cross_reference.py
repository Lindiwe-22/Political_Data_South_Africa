import re
from common import database


def normalize(name):
    if not name:
        return None
    name = name.upper()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name or None


def is_match(tokens_a, tokens_b, min_overlap=2):
    """Flags a match if one name's words are fully contained in the other's,
    or they share at least min_overlap words. Catches name-order differences
    and middle names/initials, at the cost of some false positives on common
    surnames - treat results as leads for manual review, not confirmed links."""
    if not tokens_a or not tokens_b:
        return False
    if tokens_a == tokens_b:
        return True
    if len(tokens_a) == 1 or len(tokens_b) == 1:
        return False
    if tokens_a.issubset(tokens_b) or tokens_b.issubset(tokens_a):
        return True
    return len(tokens_a & tokens_b) >= min_overlap


def load_entries():
    mp_entries = []
    for row in database['sa_pa_persons']:
        n = normalize(row.get('name'))
        if n:
            mp_entries.append(('MP', row['name'], set(n.split())))

    other_entries = []
    for row in database['sa_mines']:
        n = normalize(row.get('owner'))
        if n:
            other_entries.append((f"Mine owner: {row.get('mine_name')}", row['owner'], set(n.split())))

    for row in database['sa_iec_donations']:
        n = normalize(row.get('donor_name'))
        if n:
            other_entries.append((f"IEC donor to {row.get('party_name')}", row['donor_name'], set(n.split())))

    return mp_entries, other_entries


def find_matches():
    mp_entries, other_entries = load_entries()
    matches = []

    # MPs (24k+ rows) checked only against the small lists (~270 rows) -
    # not against each other, which would be ~600 million comparisons.
    for mp_source, mp_name, mp_tokens in mp_entries:
        for other_source, other_name, other_tokens in other_entries:
            if is_match(mp_tokens, other_tokens):
                matches.append({
                    'name_a': mp_name, 'source_a': mp_source,
                    'name_b': other_name, 'source_b': other_source,
                })

    # Mines vs IEC donors (both small, cheap to compare directly)
    for i in range(len(other_entries)):
        src_a, name_a, tok_a = other_entries[i]
        for j in range(i + 1, len(other_entries)):
            src_b, name_b, tok_b = other_entries[j]
            is_cross = (src_a.startswith('Mine') and src_b.startswith('IEC')) or \
                       (src_a.startswith('IEC') and src_b.startswith('Mine'))
            if is_cross and is_match(tok_a, tok_b):
                matches.append({'name_a': name_a, 'source_a': src_a, 'name_b': name_b, 'source_b': src_b})

    return matches


def save_matches(matches):
    table = database['sa_cross_list_matches']
    table.delete()
    for m in matches:
        table.insert(m)


if __name__ == '__main__':
    matches = find_matches()
    print(f"Found {len(matches)} potential cross-list name matches")
    for m in matches[:20]:
        print(f"  {m['name_a']}  ({m['source_a']})  <->  {m['name_b']}  ({m['source_b']})")
    if len(matches) > 20:
        print(f"  ... and {len(matches) - 20} more (see sa_cross_list_matches table)")
    save_matches(matches)
    print("Saved to sa_cross_list_matches table")

    