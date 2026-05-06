import json, os

base = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads'
merged = os.path.join(base, 'all_leads_merged.json')

with open(merged, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total leads: {len(data)}')

# Check website field
websites = [r.get('website','') for r in data]
empty = sum(1 for w in websites if not w.strip())
gs_links = sum(1 for w in websites if 'gelbeseiten' in w.lower())
real = sum(1 for w in websites if w.strip() and 'gelbeseiten' not in w.lower())

print(f'Empty website: {empty}')
print(f'Gelbe Seiten links: {gs_links}')
print(f'Real external websites: {real}')

# Show some real website examples
real_examples = [r for r in data if r.get('website','').strip() and 'gelbeseiten' not in r['website'].lower()]
print(f'\nFirst 5 real website examples:')
for r in real_examples[:5]:
    print(f'  {r["website"]} | {r["clinic_name"]}')
