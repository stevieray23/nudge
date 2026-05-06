import json, re
from collections import Counter

with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase1\agent1_frankfurt_bremen.json') as f:
    data = json.load(f)

print("Total records:", len(data))
print()
for city, n in sorted(Counter(r['city'] for r in data).items()):
    print(f"  {city}: {n}")

print()

# Sample
shown = set()
for r in data:
    c = r['city']
    if c not in shown:
        shown.add(c)
        print("---", c, "---")
        print("  NAME:", r['clinic_name'])
        print("  ADDR:", r['address'])
        print()

# Bad checks
bad = [r for r in data if len(r['clinic_name'].strip()) < 4]
print("Very short names:", len(bad))

no_dental = [r for r in data if not re.search(r'(dr\.|praxis|mvz|zahnarzt|kiefer|implant|oral|mkg|dent|gen)', r['clinic_name'].lower())]
print("Names without dental keywords:", len(no_dental))
for r in no_dental[:10]:
    print("  -", r['clinic_name'], "|", r['address'][:60])
