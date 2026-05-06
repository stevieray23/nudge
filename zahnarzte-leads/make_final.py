import json, csv, re
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
data = json.load(open(BASE / 'gs_detail_emails.json', encoding='utf-8'))
print(f'Records: {len(data)}')
emails = [r for r in data if r.get('email')]
print(f'With email: {len(emails)}')

def parse_name(n):
    if not n: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Prof\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|Kieferorthopädie\s*)','',n,flags=re.I).strip()
    parts = n.split()
    if not parts: return '',''
    return parts[0], (parts[-1] if len(parts)>1 else '')

GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz','terminvergabe','anmeldung'}
PUBLIC = {'gmail.com','yahoo.com','hotmail','outlook.com','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com','gmx.net','email.de','live.com','outlook.de','arcor.de'}
BAD = {'sentry','usercentrics','kzvh','kzvr','zaek','aekwl','bezreg','lzkth','lzkbw','lzk','brd.nrw','alldent','dentalke','dentall','dentazoo','dentacon','dentaloft','doctolib','jameda','docinsider','sentry.io','wixpress.com','sentry-next','stadtbranchenbuch','golocal','11880.com','dasoertliche','meinungsmeister','consentmanager','adfarm','adition','wipe.de'}
BADLOCAL = {'sentry','pixel','tracking','cropped','logo','icon','btn','button','transparent','bg-','header','footer','data','undefined','no-reply'}

def is_ok(e):
    if not e or '@' not in e: return False
    lo = e.lower(); local, domain = lo.split('@', 1)
    domain = domain.rstrip('/').split('?')[0].split('#')[0]
    if any(x in domain for x in BAD): return False
    if any(x in lo for x in BADLOCAL): return False
    if local in GENERIC and any(p in domain for p in PUBLIC): return False
    return True

clean = []
seen = set()
for r in data:
    em = r.get('email','')
    if not em or not is_ok(em): continue
    if em.lower() in seen: continue
    seen.add(em.lower())
    vn, ln = parse_name(r.get('name',''))
    clean.append({'vorname': vn, 'nachname': ln, 'email': em, 'website': r.get('website',''), 'city': r.get('city','')})

print(f'Clean unique emails: {len(clean)}')

out = BASE / 'ZAHNARZTE_LEADS_FINAL.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','website','city'], delimiter=';')
    w.writeheader()
    w.writerows(clean)
print(f'Saved: {out}')

# Show samples
print('\nSample emails:')
for r in clean[:10]:
    print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]} | {r["city"]}')

# City breakdown
from collections import Counter
city_counts = Counter(r['city'] for r in clean)
print('\nCity breakdown:')
for city, cnt in city_counts.most_common():
    print(f'  {city}: {cnt}')
