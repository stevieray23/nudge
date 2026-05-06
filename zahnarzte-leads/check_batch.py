import csv
from pathlib import Path
BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
for fname in ['leads_batch_1.csv','leads_batch_6.csv','leads_batch_3.csv']:
    f = BASE / fname
    if f.exists():
        rows = list(csv.DictReader(open(f, encoding='utf-8'), delimiter=';'))
        print(f'=== {fname}: {len(rows)} rows ===')
        has_email = [r for r in rows if r.get('email','').strip()]
        no_email = [r for r in rows if not r.get('email','').strip()]
        print(f'With email: {len(has_email)}, without: {len(no_email)}')
        print('Sample WITH email:')
        for r in has_email[:3]:
            print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]} | {r["website"][:50]}')
        print('Sample WITHOUT email:')
        for r in no_email[:3]:
            print(f'  {r["vorname"]} {r["nachname"]} | {r["website"][:50]}')
