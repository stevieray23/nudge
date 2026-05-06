import json, re
from collections import Counter

with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase1\agent1_frankfurt_bremen.json') as f:
    data = json.load(f)

print("Total:", len(data))
print()
for city, n in sorted(Counter(r['city'] for r in data).items()):
    print(f"  {city}: {n}")

# Check address completeness: do they start with a 5-digit postal code?
starts_with_postal = 0
has_street = 0
for r in data:
    addr = r['address']
    if re.match(r'^\d{5}', addr):
        starts_with_postal += 1
    # Does address have a street pattern (letter word + number)?
    if re.search(r'[A-ZÄÖÜ][a-zäöüß]+[\s\-]+[\d]', addr):
        has_street += 1

print(f"\nAddresses starting with postal code: {starts_with_postal}/{len(data)}")
print(f"Addresses with street pattern: {has_street}/{len(data)}")

# Show random 5 addresses
import random
random.seed(42)
for r in random.sample(data, 5):
    print(f"  [{r['city']}] {r['clinic_name']} -> {r['address'][:80]}")
