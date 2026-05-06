"""
Correct email filter - accept personal + practice clinic emails, reject only truly bad ones.
"""
import csv, json
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

# BAD: image pixels, Sentry, Doctolib tracking, dental associations, known chains
BAD_EMAILS = {
    'sentry', 'usercentrics', 'cookiebot', 'cookie', 'consent', 'tracking',
    'exception', 'error', 'bug', 'monitoring', 'keen', 'segment', 'mux', 'bugsnag'
}
BAD_LOCAL = {'noreply', 'no-reply', 'datenschutz', 'privacy', 'redaktion', 'presse', 'marketing', 'abstimmung', 'abstimm'}
# BAD domains: dental associations, chains, public trackers
BAD_DOMAINS = {'kzvh.de','kzvr.de','zaekwl.de','zaek.de','lzkth.de','lzkbw.de','lzk.de','aekwl.de','aek.de',
    'blzk.de','bezreg-koeln.de','brd.nrw.de','sozmi.landsh.de','bezirksstelle.de','zahnarztboerse.de',
    'alldent.de','dentalke.de','dentall.de','dentazoo.de','dentacon.de','dentalligator.de','dentaloft.de',
    'sentry.io','sentry-next.wixpress.com','exceptions.doctolib.de','wixpress.com','crashlytics.com',
    'google.com','googlemail.com','facebook.com','instagram.com','linkedin.com','xing.com',
    'twitter.com','bit.ly','t.co','domain.com'}
# Accept only if local is very generic AND domain is a public email provider
PUBLIC_EMAIL_DOMAINS = {'gmail.com','yahoo.com','hotmail.com','outlook.com','web.de','t-online.de',
    'gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com'}
GENERIC_LOCAL = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption',
    'empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz','privacy',
    'kontaktformular','kontakt-mail','bewerbung','anmeldung'}

def is_acceptable(email):
    """Accept: personal, named-domain, or practice clinic domain. Reject: bad/chain/tracker."""
    if not email or '@' not in email: return False
    lo = email.lower()
    local = lo.split('@')[0]
    domain = lo.split('@')[1] if '@' in lo else ''
    
    # Reject image pixel filenames
    if any(x in lo for x in ['.png','data:image','favicon','logo@','@2x','@3x']): return False
    # Reject Sentry/Doctolib tracking IDs
    if len(local) == 32 and any(c in lo for c in ['sentry','wixpress','doctolib','exceptions']): return False
    # Reject association domains
    if any(d in domain for d in BAD_DOMAINS): return False
    # Reject bad local parts with public email
    if local in GENERIC_LOCAL or local in BAD_LOCAL:
        if any(p in domain for p in PUBLIC_EMAIL_DOMAINS): return False
    # Accept: personal name email (firstname.lastname or firstname-nachname)
    if '.' in local or '-' in local or '_' in local:
        if len(local) >= 4: return True
    # Accept: mixed case single-word name
    if len(local) >= 3 and local[0].isupper() and local.isalpha(): return True
    # Accept: named clinic domain (anything.de with a real name in it)
    if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch','.eu')):
        domain_name = domain.split('.')[0]
        if len(domain_name) >= 3 and not any(b in domain for b in ['google','amazon','facebook','instagram','linkedin','twitter']):
            return True
    return False

# Analyze all unique emails
seen = set()
bad_examples = []
good_examples = []
all_sources = []

# Collect from all sources
for fname in ['zahnarzte_final.csv']:
    f = BASE / fname
    with open(f, 'r', encoding='utf-8') as fh:
        for row in csv.DictReader(fh, delimiter=';'):
            em = row.get('email','').strip()
            if em and em.lower() not in seen:
                seen.add(em.lower())
                all_sources.append((em, 'v1', row))

for bf in sorted(BASE.glob('v2_batch*.json')):
    d = json.load(open(bf, 'r', encoding='utf-8'))
    for r in d.get('results', []):
        em = (r.get('em') or '').strip()
        if em and em.lower() not in seen:
            seen.add(em.lower())
            all_sources.append((em, bf.name, r))

for bf in sorted(BASE.glob('leads_batch_*.csv')):
    with open(bf, 'r', encoding='utf-8') as fh:
        for row in csv.DictReader(fh, delimiter=';'):
            em = row.get('email','').strip()
            if em and em.lower() not in seen:
                seen.add(em.lower())
                all_sources.append((em, bf.name, row))

print(f'Total unique emails: {len(all_sources)}')
good = [e for e, _, _ in all_sources if is_acceptable(e)]
bad = [e for e, _, _ in all_sources if not is_acceptable(e)]
print(f'Acceptable: {len(good)}, Rejected: {len(bad)}')

# Show rejected
print('\nRejected (should these be accepted?):')
for e in bad[:30]:
    print(f'  REJECT: {e}')

print('\nAccepted:')
for e in good[:20]:
    print(f'  ACCEPT: {e}')
