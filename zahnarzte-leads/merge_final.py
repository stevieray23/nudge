import csv, re
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

def parse_name(n):
    if not n: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Prof\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|Kieferorthopädie\s*)','',n,flags=re.I).strip()
    parts = n.split()
    if not parts: return '',''
    return parts[0], (parts[-1] if len(parts)>1 else '')

# Load new 667 from gs_detail_pipeline
new_data = []
with open(BASE / 'ZAHNARZTE_LEADS_FINAL.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f, delimiter=';'):
        new_data.append(row)
print(f'New data: {len(new_data)} rows')

# Load old 257
old_data = []
with open(BASE / 'FINAL_LEADS_v2.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f, delimiter=';'):
        old_data.append(row)
print(f'Old data: {len(old_data)} rows')

# Merge and deduplicate
seen_emails = set()
all_rows = []
for d in new_data + old_data:
    em = d.get('email','').strip().lower()
    if not em or '@' not in em: continue
    if em in seen_emails: continue
    seen_emails.add(em)
    vn = d.get('vorname','').strip()
    ln = d.get('nachname','').strip()
    ws = d.get('website','').strip()
    city = d.get('city','').strip()
    # Prefer row with better name
    all_rows.append({'vorname': vn, 'nachname': ln, 'email': d.get('email','').strip(), 'website': ws, 'city': city})

print(f'Merged total: {len(all_rows)} unique emails')

# Sort by email
all_rows.sort(key=lambda r: r['email'].lower())

# Write final
out = BASE / 'ZAHNARZTE_LEADS_FINAL.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','website','city'], delimiter=';')
    w.writeheader()
    w.writerows(all_rows)

print(f'Written: {out}')
print(f'\nTotal leads: {len(all_rows)}')

# Show samples
print('\nFirst 15 rows:')
for r in all_rows[:15]:
    print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]} | {r["city"]}')
