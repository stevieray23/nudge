import json, os

base = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2'
for i in [1, 2, 3, 4]:
    f = os.path.join(base, f'batch_{i}_enriched.json')
    if os.path.exists(f):
        try:
            with open(f, 'r', encoding='utf-8-sig') as fh:
                data = json.load(fh)
        except Exception as e:
            print(f'Batch {i}: JSON error: {e}')
            continue
        real = [r for r in data if r.get('website', '').strip() and 'gelbeseiten' not in r.get('website', '').lower()]
        emails = [r for r in data if r.get('email_found')]
        print(f'Batch {i}: {len(data)} records, {len(real)} real websites, {len(emails)} emails')
        for r in real[:3]:
            print(f'  website: {r.get("website")}')
    else:
        print(f'Batch {i}: NOT FOUND')

# Also check for real_websites.json
rw = os.path.join(base, 'real_clinic_websites.json')
if os.path.exists(rw):
    with open(rw, 'r', encoding='utf-8-sig') as f:
        d = json.load(f)
    print(f'\nreal_clinic_websites.json: {len(d)} entries')
else:
    print(f'\nreal_clinic_websites.json: NOT FOUND')
