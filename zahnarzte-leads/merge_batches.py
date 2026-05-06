import json, csv, re
from pathlib import Path
from collections import OrderedDict

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

all_listings = []

# Parse all 3 batch files
for fname in ['gs_batch_a.json','gs_batch_b.json','gs_batch_c.json']:
    p = BASE / fname
    if not p.exists(): continue
    d = json.load(open(p, encoding='utf-8'))
    if isinstance(d, list):
        for city_data in d:
            city = city_data.get('city','')
            listings = city_data.get('listings', [])
            for l in listings:
                l['city'] = city
                all_listings.append(l)
    elif isinstance(d, dict):
        for city, val in d.items():
            if isinstance(val, dict):
                listings = val.get('listings', [])
            elif isinstance(val, list):
                listings = val
            else:
                listings = []
            for l in listings:
                l['city'] = city
                all_listings.append(l)

print(f'Total raw listings: {len(all_listings)}')

# Deduplicate by name (some names appear multiple times)
seen_names = {}
unique = []
for l in all_listings:
    name = l.get('name','').strip()
    city = l.get('city','').strip()
    key = (name.lower(), city.lower())
    if key not in seen_names:
        seen_names[key] = True
        unique.append(l)

print(f'Unique listings: {len(unique)}')

# Extract vorname/nachname from name
def parse_name(name):
    # Remove prefixes
    name = re.sub(r'^(Dr\.?\s*|Prof\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|'
                  r'Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|'
                  r'Oralchirurgie\s*|Kieferorthopädie\s*|Frau\s*|Herrn?\s*)', '', name, flags=re.I).strip()
    # Remove suffixes
    name = re.sub(r'(\s*,?\s*(?:Zahnärzte|Zahnarztpraxis|Praxis|MVZ|GmbH|AG|KG|PartG)$)', '', name, flags=re.I).strip()
    name = re.sub(r'^[\-\s]+|[\-\s]+$', '', name).strip()
    
    # Split into parts
    parts = name.split()
    if not parts: return '', ''
    if len(parts) == 1: return parts[0], ''
    
    # First part = vorname, last part = nachname (heuristic)
    # For multiple names like "Dr. Hans Müller und Dr. Peter Schmidt"
    # Just take the first two reasonable parts
    vn = parts[0]
    ln = parts[-1] if len(parts) > 1 else ''
    
    # Clean up
    vn = re.sub(r'^(Dr\.?|Prof\.?)$', '', vn).strip()
    if not vn: vn = parts[0]
    
    # Skip if looks like a role
    BAD = {'und','und ','von','van','der','die','das','kollegen','partner','zahnärzte','zahnarzt'}
    if vn.lower() in BAD: vn = parts[1] if len(parts) > 1 else ''
    if ln.lower() in BAD: ln = parts[-2] if len(parts) > 1 else ''
    
    return vn, ln

# Save the unique listings as CSV
out_csv = BASE / 'zahnarzte_names_only.csv'
with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['vorname','nachname','name','city'], delimiter=';')
    w.writeheader()
    for l in unique:
        vn, ln = parse_name(l['name'])
        w.writerow({'vorname': vn, 'nachname': ln, 'name': l['name'], 'city': l.get('city','')})

print(f'Saved: {out_csv}')
print(f'\nCity breakdown:')
from collections import Counter
city_counts = Counter(l.get('city','') for l in unique)
for city, cnt in city_counts.most_common():
    print(f'  {city}: {cnt}')

print('\nSample parsed names:')
for l in unique[:10]:
    vn, ln = parse_name(l['name'])
    print(f'  {vn} {ln} ({l["city"]}) | {l["name"]}')
