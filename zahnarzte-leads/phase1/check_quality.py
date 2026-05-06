import json
from collections import defaultdict

with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase1\agent1_frankfurt_bremen.json') as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
print()

by_city = defaultdict(list)
for r in data:
    by_city[r['city']].append(r)

for city in ['Frankfurt am Main', 'Bremen', 'Essen', 'Bochum', 'Bielefeld', 'Bonn']:
    recs = by_city[city]
    print(f"=== {city} ({len(recs)} records) ===")
    for r in recs[:3]:
        print(f"  NAME:  {r['clinic_name']}")
        print(f"  ADDR:  {r['address']}")
    print()

bad = [r for r in data if not r['clinic_name'] or len(r['clinic_name']) < 3]
print(f"Bad entries (name too short): {len(bad)}")

street_like = [r for r in data if any(s in r['clinic_name'] for s in ['Str.', 'str.', 'Weg', 'Platz', 'Ring'])]
print(f"Potential street-name mistakes: {len(street_like)}")
for r in street_like[:5]:
    print(f"  {r['clinic_name']} | {r['address']}")
