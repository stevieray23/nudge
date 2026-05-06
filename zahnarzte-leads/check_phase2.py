import json, os

base = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2'
for i in range(1, 6):
    f = os.path.join(base, f'batch_{i}_enriched.json')
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        real = [r for r in data if r.get('website', '').strip() and 'gelbeseiten' not in r.get('website', '').lower()]
        emails = [r for r in data if r.get('email_found')]
        print(f'Batch {i}: {len(data)} records, {len(real)} real websites, {len(emails)} emails found')
        for r in real[:3]:
            print(f'  {r.get("website")}')
    else:
        print(f'Batch {i}: NOT FOUND')
