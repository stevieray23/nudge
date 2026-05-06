import csv, re, os
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
OUT = BASE / 'zahnarzte_1000_final.csv'

def is_personal(email):
    if not email or '@' not in email: return False
    local = email.lower().split('@')[0]
    domain = email.lower().split('@')[1] if '@' in email else ''
    bad = {'noreply','no-reply','datenschutz','privacy','info@','kontakt@','praxis@','service@',
        'support@','team@','office@','mail@','termin','rezeption','empfang','sekretariat',
        'poststelle','redaktion','webmaster','cookie','consent','borlabs','tracking','marketing',
        'sentry','usercentrics','google.com','domain.com','facebook','instagram','linkedin',
        'bezirk','lzk','kzvr','kzvs','zaek','aek','bezreg','lzkth','lzkbw','bezirksstelle',
        'lzk-nrw','aekwl','bezreg-koeln','bezreg','docinsider','jameda','jimdo','webnode',
        'wix.com','squarespace','dentalke','dentalke','zahni','zahn','dental'}
    if any(b in local or b in domain for b in bad): return False
    if '.png' in email or '.jpg' in email or '.svg' in email: return False
    if 'alldent' in domain: return False
    # Accept if local has firstname.lastname pattern or looks like a name
    if '.' in local and len(local) > 4: return True
    if len(local) >= 3 and local[0].isupper(): return True
    if re.match(r'^[a-z]+\.[a-z]+$', domain): return True
    return True

def clean_name(cn):
    if not cn: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Dr\.?\s*med\.?\s*dent\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Fachpraxis\s*|Zahnärztin\s*|Zahnarzt\s*)', '', cn, flags=re.I).strip()
    n = re.sub(r'[\.,]+$', '', n)
    parts = n.split()
    if len(parts) >= 2: return parts[0], parts[-1]
    elif len(parts) == 1: return '', parts[0]
    return '', ''

all_rows = []
seen_emails = set()

# Existing final CSV
existing = BASE / 'zahnarzte_final.csv'
if existing.exists():
    with open(existing, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            em = row.get('email','').strip().lower()
            if em and em not in seen_emails and is_personal(em):
                seen_emails.add(em)
                all_rows.append(row)
    print(f'zahnarzte_final.csv: {len(all_rows)} emails')

# Batch CSVs
for pattern in ['paralysis*/leads_*.csv', 'batch_*/leads_*.csv', 'batch_*.csv']:
    for bf in sorted(BASE.glob(pattern)):
        with open(bf, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                em = row.get('email','').strip().lower()
                if em and em not in seen_emails and is_personal(em):
                    seen_emails.add(em)
                    all_rows.append(row)
        print(f'  {bf.name}: {len(all_rows)} total so far')

print(f'\nTotal unique personal emails: {len(all_rows)}')
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
    writer.writeheader()
    writer.writerows(all_rows)
print(f'Saved to: {OUT}')
print('Sample:')
for r in all_rows[:5]:
    print(f'  {r.get("vorname","")} {r.get("nachname","")} | {r.get("email","")}')
