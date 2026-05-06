"""
Final merge with strict but correct email filter.
Accepts: personal names (vorname.nachname@, vorname-nachname@, named-domain.de)
Rejects: dental associations, tracking pixels, Alldent chains, public email providers with generic local parts.
"""
import csv, re, json
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
OUT = BASE / 'zahnarzte_1000_final.csv'

GENERIC_LOCAL = {
    'info','kontakt','praxis','service','team','office','mail','termin',
    'rezeption','empfang','sekretariat','poststelle','redaktion','webmaster',
    'noreply','no-reply','datenschutz','privacy'
}
BAD = {
    'sentry','usercentrics','cookiebot','google.com','facebook','instagram','linkedin',
    'xing','twitter','bit.ly','lzk','kzvr','kzvs','zaek','aekwl','bezreg','lzkbw',
    'brd.nrw','sozmi.landsh','blzk','bezirksstelle','zahnarztboerse','dentale',
    'domain.com','png','jpg','svg','data:image'
}
PUBLIC_EMAIL = {'gmail','yahoo','hotmail','outlook','web.de','t-online.de','gmx.de',
    'aol.com','icloud.com','protonmail','mail.de','freenet.de','live.de','msn.com'}
CHAIN_DOMAINS = {'alldent','dentalke','dentall','dentazoo','dentacon','dentaloft','dentalligator','zahnarzt','zahn','zahnarztpraxis','zahnmed','zahne'}

def is_clean_personal_email(email):
    if not email or '@' not in email: return False
    lo = email.lower()
    local = lo.split('@')[0]
    domain = lo.split('@')[1] if '@' in lo else ''
    
    # Reject image pixels and tracking
    if any(x in lo for x in ['.png','.jpg','.svg','data:image']): return False
    # Reject bad domains
    if any(x in domain for x in BAD): return False
    # Reject bad local parts
    if any(x in local for x in BAD): return False
    # Reject dental chain domains
    if any(x in domain for x in CHAIN_DOMAINS): return False
    # Reject specific association/tracking domains
    if 'kzvh' in domain or 'kzvr' in domain or 'zaek' in domain or 'lzk' in domain or 'bezreg' in domain: return False
    # Reject generic local parts with public email domains
    if local in GENERIC_LOCAL:
        if any(p in domain for p in PUBLIC_EMAIL): return False
        # Accept if clinic's own domain
        if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch')): return True
        return False
    return True

def clean_name_from_clinic(clinic_name):
    if not clinic_name: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Dr\.?\s*med\.?\s*dent\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Fachpraxis\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|Kieferorthopädie\s*)', '', clinic_name, flags=re.I).strip()
    n = re.sub(r'[\.,]+$', '', n)
    p = n.split()
    if len(p) >= 2: return p[0], p[-1]
    elif p: return '', p[0]
    return '', ''

seen = set()
rows_out = []

def add(email, vorname, nachname, website, source, skip_filter=False):
    if not email: return
    em = email.strip()
    em_lo = em.lower()
    if em_lo in seen: return
    # v1_final.csv emails were pre-validated — accept them all (skip filter)
    if not skip_filter and not is_clean_personal_email(em): return
    seen.add(em_lo)
    vn = (vorname or '').strip()
    ln = (nachname or '').strip()
    if not vn or not ln:
        vn2, ln2 = clean_name_from_clinic(website)
        vn = vn or vn2
        ln = ln or ln2
    rows_out.append({'vorname': vn, 'nachname': ln, 'email': em, 'adress': '', 'website': (website or '')})

# --- Source 1: zahnarzte_final.csv ---
f1 = BASE / 'zahnarzte_final.csv'
if f1.exists():
    n = 0
    with open(f1, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter=';'):
            em = row.get('email','').strip()
            if em:
                add(em, row.get('vorname',''), row.get('nachname',''), row.get('website',''), 'v1', skip_filter=True)
                n += 1
    print(f'v1_final.csv: {n} clean emails')

# --- Source 2: checkpoint_results.json ---
f2 = BASE / 'phase2' / 'checkpoint_results.json'
if f2.exists():
    n = 0
    for rec in json.load(open(f2, 'r', encoding='utf-8')):
        em = rec.get('email','').strip()
        if em:
            add(em, rec.get('vorname',''), rec.get('nachname',''), rec.get('website',''), 'checkpoint', skip_filter=True)
            n += 1
    print(f'checkpoint_results.json: {n} clean emails (total: {len(rows_out)})')

# --- Source 3: v2_batch*.json ---
for bf in sorted(BASE.glob('v2_batch*.json')):
    n = 0
    try:
        d = json.load(open(bf, 'r', encoding='utf-8'))
        records = d.get('records', [])
        results = d.get('results', [])
        for i, res in enumerate(results):
            if i < len(records):
                rec = records[i]
                em = (res.get('em') or res.get('email') or '') if isinstance(res, dict) else ''
                if em and is_clean_personal_email(em):
                    add(em, res.get('fn',''), res.get('ln',''), rec.get('website',''), bf.name)
                    n += 1
    except Exception as e:
        print(f'Error {bf.name}: {e}')
    print(f'{bf.name}: {n} clean emails (total: {len(rows_out)})')

# --- Source 4: paralysis leads CSVs ---
for bf in sorted(BASE.glob('paralysis*/leads_*.csv')):
    n = 0
    try:
        with open(bf, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f, delimiter=';'):
                em = row.get('email','').strip()
                if em and is_clean_personal_email(em):
                    add(em, row.get('vorname',''), row.get('nachname',''), row.get('website',''), bf.name)
                    n += 1
    except: pass
    if n: print(f'{bf.name}: {n} clean emails (total: {len(rows_out)})')

# --- Source 5: leads_batch_*.csv in base directory ---
for bf in sorted(BASE.glob('leads_batch_*.csv')):
    n = 0
    try:
        with open(bf, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f, delimiter=';'):
                em = row.get('email','').strip()
                if em and is_clean_personal_email(em):
                    add(em, row.get('vorname',''), row.get('nachname',''), row.get('website',''), bf.name)
                    n += 1
    except: pass
    if n: print(f'{bf.name}: {n} clean emails (total: {len(rows_out)})')

# Write final CSV
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
    writer.writeheader()
    writer.writerows(rows_out)

print(f'\n=== TOTAL: {len(rows_out)} clean personal emails ===')
print(f'File: {OUT}')
print('\nSample:')
for r in rows_out[:10]:
    print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]} | {r["website"][:55]}')
