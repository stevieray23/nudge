"""
Rebuild ZAHNARZTE_LEADS_FINAL.csv cleanly.
Extract names from email local part, domain, and Impressum pages.
"""
import csv, re, asyncio, httpx
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9',
}

GENERIC_LOCAL = {'info','kontakt','praxis','service','team','office','mail','termin',
    'rezeption','empfang','sekretariat','poststelle','redaktion','webmaster',
    'noreply','datenschutz','terminvergabe','rezeptionistin','anmeldung',
    'terminplanung','behandlung','patienten','patient','kunden','kontaktformular',
    'sprechstunde','klinik','kontaktform'}
PUBLIC = {'gmail.com','yahoo.com','hotmail','outlook.com','web.de','t-online.de',
    'gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de',
    'live.de','msn.com','gmx.net','email.de','live.com','outlook.de',
    'yahoo.de','hotmail.com','outlook.de','gmx.ch','gmx.at','yahoo.de',
    'arcor.de','tiscali.de','supermail.de','onlinehome.de','kabelmail.de',
    'surfeu.de','foni.net','comcast.net','rocketmail.com'}
BAD_DOMAINS = {'sentry','usercentrics','cookiebot','kzvh','kzvr','zaek','aekwl',
    'bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi','blzk',
    'bezirksstelle','zahnarztboerse','dentale','alldent','dentalke',
    'dentall','dentazoo','dentacon','dentalligator','dentaloft',
    'sentry.io','wixpress.com','doctolib','jameda','docinsider',
    'sentry-next','lokalreport','stadtbranchenbuch','golocal',
    '11880.com','dasoertliche','kennstdueinen'}
BAD_PARTS = {'sentry','pixel','tracking','cropped','logo','icon','btn',
    'button','transparent','bg-','header','footer','div','span',
    'data','undefined','null','test123','example','no-reply',
    'datenschutzbeauftragter','kontaktformular'}
KNOWN_BAD_EMAILS = {'info@zahnarztpraxis-lauenstein.de','anmeldung@zahnarztpraxis-lauenstein.de',
    'info@praxis-dr-d已成.de','test@test.de','hello@fruits.co',
    'hv@alkenbrecher.info','moin@boris-hahn.com','mustermann@musterfirma.de',
    'praxis@m-leuschner-dresden.de','vasb@xhamr-zrqvra.qr','contact@digitalagenten.com',
    'curators@galerie.com','kanzlei@muenchen-immobilienrecht.de'}

# German first names (common)
GERMAN_FIRST = {'hans','klaus','peter','wolfgang','werner','jürgen','juergen','gerhard','ulf',
    'walter','helmut','herbert','franz','albert','erwin','otto','rudolf','karl','heinz',
    'andrea','anna','anja','birgit','brigitte','claudia','christine','daniela','elke',
    'eva','franziska','gerda','gisela','grete','hanna','heike','helga','ingrid','iris',
    'jan','jens','johannes','jonas','julia','karin','katja','katrin','kerstin','kristina',
    'lena','lisa','ludwig','marco','maria','marina','markus','martha','martin','matthias',
    'max','michael','monika','nicole','norbert','olga','oliver','patrick','paula','petra',
    'ralf','ralph','regina','renate','robert','sabine','sandrine','sandra','sarah',
    'silke','simon','stefan','stephan','susanne','thomas','tom','ulrike','ute','volker',
    'werner','wilhelm','zahnarzt','zahnärztin','dr','dr med','prof','prof dr'}

def is_acceptable_email(e):
    """Accept named locals anywhere + generic locals on clinic domains.
    Reject: public domain + generic local, bad domains, bad local patterns."""
    if not e or '@' not in e: return False
    lo = e.lower(); local, domain = lo.split('@', 1)
    domain = domain.rstrip('/').split('?')[0].split('#')[0]
    # Reject bad domains entirely
    if any(x in domain for x in BAD_DOMAINS): return False
    # Reject bad local fragments
    if any(x in lo for x in BAD_PARTS): return False
    # Reject known bad emails
    if lo in KNOWN_BAD_EMAILS: return False
    # Reject public email providers on generic local parts
    if local in GENERIC_LOCAL and any(p in domain for p in PUBLIC): return False
    return True

def is_named_local(local):
    """Does this email local part look like a personal name?"""
    lo = local.lower()
    if '.' in lo and len(lo) >= 5: return True
    if '-' in lo and len(lo) >= 4: return True
    if '_' in lo and len(lo) >= 5: return True
    if lo.startswith('dr.') and len(lo) >= 5: return True
    if len(lo) >= 4 and lo[0].isupper() and any(c.isupper() for c in lo[1:]): return True
    return False

def looks_like_name(word):
    """Is this word a plausible name (first or last)? Checks against common names + rules."""
    w = word.lower()
    if len(w) < 2: return False
    if w in GENERIC_LOCAL or w in BAD_PARTS: return False
    # All letters must be alpha (or German umlauts)
    if not all(c.isalpha() or c in 'äöüß' for c in w): return False
    # Check against known German first names
    if w in GERMAN_FIRST: return True
    # Plausible if: starts with uppercase, at least one vowel, 3+ letters
    if word[0].isupper() and len(w) >= 3:
        vowels = set('aeiouäöü')
        if any(c in vowels for c in w): return True
    return False

def split_name_parts(local):
    """Split email local part into candidate name parts."""
    # Remove titles
    local = re.sub(r'^(dr\.?|prof\.?|med\.?|med\.?|arzt\.?|zahnarzt\.?)\s*', '', local, flags=re.I)
    local = re.sub(r'^(frau|herr|miss|ms|mr)\s*', '', local, flags=re.I)
    parts = []
    # Split on dots, dashes, underscores
    for sep in ['.', '-', '_']:
        if sep in local:
            parts = [p for p in local.split(sep) if p]
            break
    if not parts:
        parts = [local] if local else []
    # Filter and validate
    good = []
    for p in parts:
        p = p.strip()
        if not p: continue
        if p.lower() in GENERIC_LOCAL or p.lower() in BAD_PARTS: continue
        if not p.isalpha() and not re.match(r'^[a-zA-ZäöüÄÖÜß]+$', p): continue
        good.append(p)
    return good

def extract_name_from_email(em):
    """Return (vorname, nachname) from email local part."""
    local = em.lower().split('@')[0]
    parts = split_name_parts(local)
    if not parts: return '', ''
    # Find first plausible first name
    vn = ''
    for p in parts:
        if p.lower() in GERMAN_FIRST and len(p) >= 3:
            vn = p.capitalize()
            break
    if not vn:
        # Use first plausible word as vorname
        for p in parts:
            if looks_like_name(p) and len(p) >= 3:
                vn = p.capitalize()
                break
    # Nachname = last plausible word that's different from vorname
    ln = ''
    for p in reversed(parts):
        pl = p.lower()
        if pl == vn.lower(): continue
        if looks_like_name(p) and len(p) >= 3 and pl != 'ihres' and pl != 'vertrauens':
            ln = p.capitalize()
            break
    # If we only got one name, use it as last name
    if vn and not ln:
        ln = ''
    return vn, ln

def extract_name_from_domain(domain):
    """Extract practice/owner name from website domain."""
    d = domain.lower().replace('https://','').replace('http://','').replace('www.','')
    d = d.split('/')[0].split('?')[0].rstrip('.')
    base = d.rsplit('.', 2)[0] if '.' in d else d
    # Remove common prefixes
    base = re.sub(r'^(praxis|zahnarzt|dr|dr\.|zahn|zahnmedizin|kfo|mvz|dental|oral|kinder|pädiatr)[-_]*', '', base, flags=re.I)
    base = re.sub(r'[-_]+', ' ', base).strip()
    words = [w.capitalize() for w in base.split() if len(w) >= 2 and w.isalpha()]
    if not words: return '', ''
    return '', ' '.join(words)

async def get_impressum_name(client, url, sem):
    if not url or not url.startswith('http'): return '', ''
    base = url.rstrip('/')
    for path in ['/impressum','/impressum/','/impress','/legal']:
        async with sem:
            try:
                r = await client.get(base + path, timeout=httpx.Timeout(10.0, connect=5.0),
                    follow_redirects=True, headers=HDRS)
                if r.status_code == 200 and len(r.text) > 500:
                    html = r.text
                    # Inhaber: Dr. Vorname Nachname
                    for pat in [
                        r'(?:Inhaber[in]?|Betreiber[in]?|Verantwortlich[erin]?|Zahnärzt[in]?)\s*[:\.]?\s*(?:Dr\.?\s*(?:med\.?\s*)?)?([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})',
                        r'(?:Praxisinhaber[in]?|Besitzer[in]?)\s*[:\.]?\s*(?:Dr\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)',
                        r'(?<![a-z])(Dr\.?\s+(?:med\.?\s*)?[A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)',
                    ]:
                        m = re.search(pat, html, re.I)
                        if m:
                            name = m.group(1) if m.lastindex >= 1 else m.group(0)
                            parts = name.strip().split()
                            if len(parts) >= 2:
                                return parts[0].capitalize(), parts[-1].capitalize()
            except: pass
        await asyncio.sleep(0.1)
    return '', ''

async def main():
    print('Step 1: Collecting emails...')
    seen = set(); records = {}
    for fname in ['zahnarzte_final.csv','zahnarzte_final_v2.csv','zahnarzte_1000_final.csv','FINAL_LEADS.csv']:
        p = BASE / fname
        if not p.exists(): continue
        n = 0
        with open(p, encoding='utf-8', errors='ignore') as f:
            for row in csv.DictReader(f, delimiter=';'):
                em = row.get('email','').strip()
                if not is_acceptable_email(em): continue
                lo = em.lower()
                if lo in seen: continue
                seen.add(lo)
                ws = row.get('website','').strip() or row.get('Website','').strip() or ''
                if lo not in records:
                    records[lo] = {'email': em, 'website': ws}
                elif ws and 'gelbeseiten' not in ws.lower():
                    records[lo]['website'] = ws
                n += 1
        print(f'  {fname}: {n} unique')
    print(f'  Total: {len(records)} emails')

    print('\nStep 2: Extracting names...')
    results = []
    for lo, rec in records.items():
        em = rec['email']; ws = rec['website']
        vn, ln = extract_name_from_email(em)
        if not ln and ws:
            _, dn = extract_name_from_domain(ws)
            if dn: ln = dn
        results.append({'vorname': vn, 'nachname': ln, 'email': em, 'adress': '', 'website': ws})

    with_ln = sum(1 for r in results if r['nachname'])
    named = sum(1 for r in results if is_named_local(r['email'].split('@')[0]))
    print(f'  {with_ln}/{len(results)} have nachname | {named} named-local')

    # Step 3: Enrich missing via Impressum
    print('\nStep 3: Crawling Impressum...')
    missing = [(i,r) for i,r in enumerate(results) if not r['nachname']]
    print(f'  {len(missing)} need enrichment')
    if missing:
        SEM = asyncio.Semaphore(15)
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0),
            limits=httpx.Limits(max_connections=30)) as client:
            for idx in range(min(len(missing), 150)):
                i, r = missing[idx]
                if not r['website']: continue
                vn2, ln2 = await get_impressum_name(client, r['website'], SEM)
                if vn2 and ln2:
                    results[i]['vorname'] = vn2; results[i]['nachname'] = ln2
                    print(f'  {vn2} {ln2} <- {r["email"]}')
                await asyncio.sleep(0.15)

    # Step 4: Sort and write
    def skey(r):
        local = r['email'].lower().split('@')[0]
        return (0 if is_named_local(local) else 1, -len(r.get('nachname','')), r['email'])
    results.sort(key=skey)

    out = BASE / 'ZAHNARZTE_LEADS_FINAL.csv'
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
        w.writeheader(); w.writerows(results)

    with_ln = sum(1 for r in results if r['nachname'])
    named = sum(1 for r in results if is_named_local(r['email'].lower().split('@')[0]))
    print(f'\nFinal: {out}')
    print(f'  {len(results)} total | {named} named-local | {with_ln} with nachname')
    print('\nNamed-local samples:')
    for r in [x for x in results if is_named_local(x['email'].lower().split('@')[0])][:10]:
        print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]}')
    print('\nPractice-domain samples:')
    for r in [x for x in results if not is_named_local(x['email'].lower().split('@')[0])][:8]:
        print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]}')

if __name__ == '__main__':
    asyncio.run(main())
