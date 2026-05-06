import csv, json, re
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
OUT = BASE / 'FINAL_LEADS.csv'

# Email filter: accept personal + practice clinic emails, reject tracking/associations
BAD_EMAILS = {'sentry','usercentrics','cookiebot','cookie','consent','tracking',
    'kzvh','kzvr','zaek','aekwl','bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi',
    'blzk','bezirksstelle','zahnarztboerse','dentale','domain.com','google.com',
    'facebook','instagram','linkedin','xing','twitter','bit.ly','sentry.io',
    'sentry-next.wixpress.com','exceptions.doctolib.de'}
BAD_LOCAL = {'noreply','no-reply','datenschutz','privacy','redaktion','presse','marketing','abstimmung'}
PUBLIC_DOMAINS = {'gmail.com','yahoo.com','hotmail.com','outlook.com','web.de','t-online.de',
    'gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com'}
GENERIC_LOCAL = {'info','kontakt','praxis','service','team','office','mail','termin',
    'rezeption','empfang','sekretariat','poststelle','redaktion','webmaster',
    'noreply','datenschutz','kontaktformular','kontakt-mail','bewerbung'}
CHAIN = {'alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft'}

def is_acceptable(email):
    if not email or '@' not in email: return False
    lo = email.lower()
    local = lo.split('@')[0]
    domain = lo.split('@')[1] if '@' in lo else ''
    if any(x in lo for x in ['.png','data:image','@2x','favicon','logo']): return False
    if any(x in domain for x in BAD_EMAILS): return False
    if any(x in local for x in BAD_LOCAL): return False
    if any(x in domain for x in CHAIN): return False
    if local in GENERIC_LOCAL:
        if any(p in domain for p in PUBLIC_DOMAINS): return False
        # Clinic domain = accept
        if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch','.eu')): return True
        return False
    return True

def clean_name(cn):
    if not cn: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|Kieferorthopädie\s*)','',cn,flags=re.I).strip()
    n = re.sub(r'[\.,]+$','',n)
    p = n.split()
    return (p[0] if p else '', p[-1] if len(p)>=2 else n)

seen = set()
rows = []

def add(vorname, nachname, email, website, source):
    if not email: return
    em = email.strip()
    if em.lower() in seen: return
    if not is_acceptable(em): return
    seen.add(em.lower())
    vn = (vorname or '').strip()
    ln = (nachname or '').strip()
    if not vn or not ln:
        vn2, ln2 = clean_name(website)
        vn = vn or vn2
        ln = ln or ln2
    rows.append({'vorname': vn, 'nachname': ln, 'email': em, 'adress': '', 'website': (website or '')})

# 1. zahnarzte_final.csv (261 emails, all real - from checkpoint results)
f1 = BASE / 'zahnarzte_final.csv'
if f1.exists():
    n = 0
    with open(f1, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter=';'):
            em = row.get('email','').strip()
            if em and is_acceptable(em):
                add(row.get('vorname',''), row.get('nachname',''), em, row.get('website',''), 'v1')
                n += 1
    print(f'zahnarzte_final.csv: {n} acceptable')

# 2. v2_batch*.json (fresh scrape from new agents)
for bf in sorted(BASE.glob('v2_batch*.json')):
    n = 0
    try:
        d = json.load(open(bf, 'r', encoding='utf-8'))
        recs = d.get('records', [])
        res = d.get('results', [])
        for i, r in enumerate(res):
            if i >= len(recs): break
            rec = recs[i]
            em = (r.get('em') or '').strip()
            if not em: continue
            if is_acceptable(em):
                add(r.get('fn',''), r.get('ln',''), em, rec.get('website',''), bf.name)
                n += 1
    except Exception as e:
        print(f'Error {bf.name}: {e}')
    print(f'{bf.name}: {n} acceptable emails')

# 3. filled_leads_batch_*.csv
for bf in sorted(BASE.glob('filled_leads_batch_*.csv')):
    n = 0
    with open(bf, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter=';'):
            em = row.get('email','').strip()
            if em and is_acceptable(em):
                add(row.get('vorname',''), row.get('nachname',''), em, row.get('website',''), bf.name)
                n += 1
    if n: print(f'{bf.name}: {n} acceptable emails')

# Write final CSV
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
    writer.writeheader()
    writer.writerows(rows)

print(f'\nFinal: {len(rows)} clean personal emails')
print(f'Saved: {OUT}')
print('\nSample:')
for r in rows[:8]:
    print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]} | {r["website"][:50]}')
