"""
Merge all known dentist email sources into one clean FINAL_LEADS_v2.csv.
Accepts: named personal emails, info@/kontakt@ on clinic domains
Rejects: public email providers, tracking pixels, dental associations, chains
"""
import csv, re
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin',
           'rezeption','empfang','sekretariat','poststelle','redaktion','webmaster',
           'noreply','datenschutz','terminvergabe','rezeptionistin'}
PUBLIC = {'gmail.com','yahoo.com','hotmail','outlook.com','web.de','t-online.de',
          'gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de',
          'live.de','msn.com','gmx.net','email.de','live.com','outlook.de'}
BAD_DOMAINS = {'sentry','usercentrics','cookiebot','kzvh','kzvr','zaek','aekwl',
               'bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi','blzk',
               'bezirksstelle','zahnarztboerse','dentale','alldent','dentalke',
               'dentall','dentazoo','dentacon','dentalligator','dentaloft',
               'sentry.io','wixpress.com','doctolib','jameda','docinsider'}
BAD_LOCAL = {'sentry','pixel','tracking','noreply','no-reply','datenschutz',
             'admin','root','test','example','undefined','null','contact',
             'cropped','marke','logo','icon','btn','button','bg-','header','footer',
             'transparent','b027','b307','d8b4','571w'}

def clean_email(e):
    if not e: return ''
    e = e.strip().strip('"\'').lower()
    if '@' not in e: return ''
    # Remove mailto:
    e = e.replace('mailto:', '')
    local, domain = e.split('@', 1)
    # Remove trailing dots/punctuation
    local = re.sub(r'[\.\\\/\-]+$', '', local)
    domain = re.sub(r'[\.\\\/\>\s]+$', '', domain)
    if not local or not domain: return ''
    if any(x in local for x in BAD_LOCAL): return ''
    return f"{local}@{domain}"

def is_acceptable(e):
    if not e or '@' not in e: return False
    local, domain = e.lower().split('@', 1)
    if any(x in domain for x in BAD_DOMAINS): return False
    if any(x in local for x in BAD_LOCAL): return False
    if local in GENERIC:
        if any(p in domain for p in PUBLIC): return False
        # Accept info@/kontakt@ on named clinic domains
        if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch','.eu')):
            return True
        return False
    return True

def is_excellent(e):
    if not is_acceptable(e): return False
    local, domain = e.lower().split('@', 1)
    # Excellent: has name-like local part
    if '.' in local and len(local) >= 4: return True
    if '-' in local or '_' in local: return True
    if len(local) >= 3 and local[0].isupper(): return True
    # Also: info@/kontakt@ on clearly named domains
    if local in GENERIC:
        if len(domain.split('.')[0]) >= 4: return True
    return False

def clean_name(n):
    """Extract first and last name from a name string."""
    if not n or len(n) < 2: return '', ''
    # Remove titles and prefixes
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|'
               r'Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|'
               r'Oralchirurgie\s*|Kieferorthopädie\s*|Prof\.?\s*|Frau\s*|Herrn?\s*)', 
               '', n, flags=re.I).strip()
    n = re.sub(r'[\.,]+$', '', n)
    # Remove common suffixes
    n = re.sub(r'(\s+(GmbH|AG|KG|mbH|Partnerschaft|PartG|in|Partners)$)', '', n, flags=re.I)
    parts = n.split()
    if len(parts) == 0: return '', ''
    if len(parts) == 1: return parts[0], ''
    # First word = first name, last word = last name
    return parts[0], parts[-1]

seen = set()
rows = []

def add(vn, ln, em, ws):
    em = clean_email(em)
    if not em or not is_acceptable(em): return
    if em in seen: return
    seen.add(em)
    _vn, _ln = clean_name(vn)
    vn, ln = (_vn if _vn else ''), (_ln if _ln else '')
    if not ln:
        _2vn, _2ln = clean_name(ln or '')
        if _2ln: ln = _2ln
    rows.append({'vorname': vn, 'nachname': ln, 'email': em,
                  'adress': '', 'website': ws or ''})

# Load each source file
sources = [
    ('zahnarzte_final.csv', ';'),
    ('zahnarzte_final_v2.csv', ';'),
    ('zahnarzte_1000_final.csv', ';'),
    ('FINAL_LEADS.csv', ';'),
]

for fname, delim in sources:
    p = BASE / fname
    if not p.exists(): continue
    n = 0
    with open(p, encoding='utf-8', errors='ignore') as f:
        for row in csv.DictReader(f, delimiter=delim):
            em = row.get('email','') or row.get('Email','') or row.get('EMAIL','')
            vn = row.get('vorname','') or row.get('Vorname','') or row.get('first_name','') or row.get('name','')
            ln = row.get('nachname','') or row.get('Nachname','') or row.get('last_name','')
            ws = row.get('website','') or row.get('Website','') or row.get('url','') or row.get('Website_url','')
            add(vn, ln, em, ws)
            n += 1
    print(f'{fname}: processed {n} rows')

# Sort: excellent first, then acceptable
def sort_key(r):
    return (0 if is_excellent(r['email']) else 1, r['email'])

rows.sort(key=sort_key)

# Write final
out = BASE / 'FINAL_LEADS_v2.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
    w.writeheader()
    w.writerows(rows)

print(f'\nFinal: {len(rows)} unique emails in {out}')
excellent = sum(1 for r in rows if is_excellent(r['email']))
print(f'  {excellent} excellent, {len(rows)-excellent} acceptable')
print('\nSample (excellent):')
for r in [x for x in rows if is_excellent(x['email'])][:8]:
    print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]}')
print('\nSample (acceptable):')
for r in [x for x in rows if not is_excellent(x['email'])][:5]:
    print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]}')
