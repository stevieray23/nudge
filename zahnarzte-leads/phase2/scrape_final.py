import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import urllib.request
import re
import ssl
import json
import html as htmlmod
from urllib.parse import urljoin

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SKIP_DOMAINS = ['gelbeseiten', '11880', 'golocal', 'meinungsmeister', 'kennstdueinen',
                'bing.com', 'google.com', 'facebook.com', 'instagram.com']

IMPRESSUM_PATHS = [
    '/impressum/', '/impressum.html', '/impressum', '/impressum.php',
    '/impressum/index.html',
    '/legal/', '/legal', '/rechtliches/', '/rechtliches',
    '/anbieterkennzeichnung/',
    '/kontakt/impressum/', '/ueber-uns/impressum', '/impressum-2/',
    '/praxis/impressum/', '/start/impressum/',
    '/kontakt/', '/impressum/index.php'
]

GENERIC_EMAIL_PREFIXES = ['info@', 'kontakt@', 'service@', 'post@', 'office@', 'mail@', 
                          'termin@', 'klinik@', 'web@', 'hello@', 'no-reply@',
                          'empfang@', 'za-@', 'kontakt.']

BAD_NAME_PARTS = {
    'zuständige', 'kammer', 'berufsrechtliche', 'regelungen', 'angaben', 'gemäß',
    'patienten', 'willkommen', 'hier', 'ihre', 'unser', 'für', 'und', 'oder',
    'das', 'die', 'der', 'den', 'dem', 'nicht', 'sind', 'auch', 'ein', 'eine',
    'praxis', 'zahnarzt', 'zahnärztin', 'praxis', 'home', 'footer',
    'termin', 'impressum', 'website', 'dental', 'ihren', 'ihrer', 'behandlung',
    'dortmund', 'düsseldorf', 'essen', 'bochum', 'wuppertal', 'köln', 'berlin',
    'hamburg', 'münchen', 'frankfurt', 'mannheim', 'hannover', 'nürnberg',
    'unseren', 'vielen', 'gmbh', 'mbh', 'bv', 'holding', 'group',
    'ihrem', 'beratung', 'service', 'erleben', 'persoenlich', 'modern',
    'galerie', 'team', 'dieser', 'seite', 'gestellte', 'fragen',
    'verlinkten', 'inhalte', 'externen', 'liebe', 'patientinnen',
    'angehörige', 'angehoerige', 'erfahren', 'spezialisten', 'vorrangiges',
    'bestreben', 'ausgebildete', 'mitarbeiter', 'kontakt',
    'verantwortliche', 'redaktionelle', 'verlags', 'gesellschaft',
    'mund', 'kiefer', 'heilkunde', 'dres', 'mvz', 'mvz gbr',
    'from', 'content', 'skip', 'navigation', 'menu', 'sidebar',
    'west', 'nord', 'süd', 'mitte', 'ost', 'stadtmitte', 'city',
    'ästetische', 'ästhetische', 'zentrum', 'plus', 'zzplus'
}

def is_real_clinic_url(url):
    if not url:
        return False
    u = url.lower()
    return not any(d in u for d in SKIP_DOMAINS)

def try_url(url, timeout=12):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=timeout)
        if resp.status == 200:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        pass
    return None

def get_meta_description(html_content):
    m = re.search(r'<meta[^>]*(?:name|id)=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.I)
    if not m:
        m = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*(?:name|id)=["\']description["\']', html_content, re.I)
    if m:
        return m.group(1).strip()
    return ''

def html_to_text(html_content):
    text = re.sub(r'(?is)<style[^>]*>.*?</style>', ' ', html_content)
    text = re.sub(r'(?is)<script[^>]*>.*?</script>', ' ', text)
    text = re.sub(r'(?is)<!--.*?-->', ' ', text)
    text = re.sub(r'(?i)<br\s*/?\s*>', '\n', text)
    text = re.sub(r'(?i)<hr\s*/?\s*>', '\n', text)
    text = re.sub(r'(?i)</(p|div|h[1-6]|li|tr)>', '\n', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = htmlmod.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    return text.strip()

def is_good_name_part(word):
    w = word.lower()
    if len(word) < 2:
        return False
    if w in BAD_NAME_PARTS:
        return False
    for bad in BAD_NAME_PARTS:
        if w.startswith(bad) and len(bad) > 3:
            return False
    return True

def extract_name_parts(text):
    """Extract (vorname, nachname) from impressum text."""
    if len(text) < 30:
        return '', ''
    
    meta_desc = get_meta_description('<html><head><title></title></head><body>' + text[:3000] + '</body></html>')
    
    # Strategy 1: "Dr. FirstName LastName" pattern in text - this is most reliable
    # Look for "Dr." followed by name in the impressum text
    patterns_with_dr = [
        r'Vertreten\s+(?:durch)?:?\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)\s+([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
        r'(?:Inhaber(?:in)?|Betreiber(?:in)?|Verantwortlich(?:er)?)[^:]*:\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)\s+([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
        r'(?:Zahnarzt|Zahnärztin)[^:]*:\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)\s+([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
        # Dr. at start of impressum text
        r'^Impressum[^\n]*Dr\.?\s+(?:med\.?\s*)?(?:dent\.?\s*)?\s+([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
    ]
    
    for pat in patterns_with_dr:
        m = re.search(pat, text, re.M | re.U)
        if m:
            v, n = m.group(1).strip(), m.group(2).strip()
            if is_good_name_part(v) and is_good_name_part(n):
                return v, n
    
    # Strategy 2: Meta description "Impressum [Title] FirstName LastName"
    # Only use if the words after "Impressum" look like real names (not clinic names)
    if meta_desc:
        # Skip if meta starts with "Impressum" followed by non-name words (clinic name patterns)
        skip_patterns = [
            r'^Impressum\s+Zahnmedizin\s+',      # "Impressum Zahnmedizin Kettel"
            r'^Impressum\s+(?:Praxis|Medi|Dental|Klinik|Zentrum)\s+',  # clinic name patterns
        ]
        skip_meta = any(re.search(p, meta_desc, re.I) for p in skip_patterns)
        
        if not skip_meta:
            # Try: Impressum [optional title] FirstName LastName
            m = re.search(r'^Impressum\s+(?:Angaben\s+gemäß[^\n]*\n?\s*)?(?:MVZ\s*)?(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)?\s*([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)\b', meta_desc, re.U)
            if m:
                v, n = m.group(1).strip(), m.group(2).strip()
                if is_good_name_part(v) and is_good_name_part(n):
                    return v, n
    
    # Strategy 3: Label + name patterns in text
    label_patterns = [
        r'Vertreten\s+(?:durch)?:?\s*([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
        r'(?:Inhaber(?:in)?|Betreiber(?:in)?|Verantwortlich(?:er)?)[^:]*:\s*([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
        r'(?:Zahnarzt|Zahnärztin)[^:]*:\s*([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
    ]
    for pat in label_patterns:
        m = re.search(pat, text, re.U)
        if m:
            v, n = m.group(1).strip(), m.group(2).strip()
            if is_good_name_part(v) and is_good_name_part(n):
                return v, n
    
    # Strategy 4: "Dr." pattern anywhere in text
    m = re.search(r'(?:^|\n)\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:\s*dent\.?\s*)?)\s+([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)', text, re.M | re.U)
    if m:
        v, n = m.group(1).strip(), m.group(2).strip()
        if is_good_name_part(v) and is_good_name_part(n):
            return v, n
    
    return '', ''

def extract_email(text):
    emails = re.findall(r'([a-zA-Z0-9.+%-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    # (at) format
    for m in re.findall(r'([a-zA-Z0-9.+%-]+)\s*\(at\)\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text):
        emails.append((m[0], m[1]))
    
    for local, domain in emails:
        email = f"{local}@{domain}".lower()
        if any(email.startswith(p.lower()) for p in GENERIC_EMAIL_PREFIXES):
            continue
        if any(x in email for x in ['@google.', '@facebook.', '@instagram.', '@linkedin.']):
            continue
        return email
    for local, domain in emails:
        email = f"{local}@{domain}".lower()
        if not any(x in email for x in ['@google.', '@facebook.', '@instagram.', '@linkedin.']):
            return email
    return ''

def parse_clinic_name(clinic_name):
    """Parse first/last name from clinic_name field as fallback"""
    clean = re.sub(r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?|Zahnärzte?|Praxis|Zahnarztpraxis|Kieferorthopädie|Fachzahnarzt|GbR|MVZ(?: GbR)?|Kieferzentrum|Dentaparks)', '', clinic_name, flags=re.I).strip()
    clean = re.sub(r'^\s*[\&,\|]+\s*', '', clean).strip()
    
    # Dr. pattern
    m = re.search(r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)', clean, re.U)
    if m:
        v, n = m.group(1), m.group(2)
        if is_good_name_part(v) and is_good_name_part(n):
            return v, n
    
    # Two capitalized words
    m = re.search(r'\b([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)\b', clean, re.U)
    if m:
        v, n = m.group(1), m.group(2)
        if is_good_name_part(v) and is_good_name_part(n):
            return v, n
    
    return '', ''

def get_impressum(clinic_url):
    base = clinic_url.rstrip('/')
    for path in [''] + IMPRESSUM_PATHS:
        url = base + path
        html_content = try_url(url)
        if html_content and len(html_content) > 500:
            text = html_to_text(html_content)
            has_impressum = any(kw in text.lower() for kw in [
                'inhaber', 'verantwortlich', 'zahnarzt', 'geschaeftsfuehrer', 
                'angaben gem', 'betreiber', 'vertreten', 'mstv', 'ddg'
            ])
            if has_impressum:
                return url, text
    return None, ''

# Load data
with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_websites.json', 'r', encoding='utf-8') as f:
    original_leads = json.load(f)

with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_with_urls.json', 'r', encoding='utf-8') as f:
    urls_data = json.load(f)

url_lookup = {}
for item in urls_data:
    gs_url = item['website']
    clinic_url = item.get('clinic_url_raw', '')
    if is_real_clinic_url(clinic_url):
        url_lookup[gs_url] = clinic_url

results = []
emails_count = 0
names_count = 0
impressum_count = 0

for i, lead in enumerate(original_leads):
    gs_url = lead['website']
    clinic_url = url_lookup.get(gs_url, '')
    
    entry = {
        'clinic_name': lead['clinic_name'],
        'address': lead['address'],
        'city': lead['city'],
        'website': clinic_url,
        'vorname': '',
        'nachname': '',
        'email': '',
        'impressum_found': False,
        'email_found': False,
        'notes': ''
    }
    
    if not clinic_url:
        entry['notes'] = 'No clinic website found (directory only)'
        results.append(entry)
        continue
    
    impressum_url, text_content = get_impressum(clinic_url)
    
    vorname, nachname = '', ''
    email = ''
    
    if impressum_url and text_content:
        impressum_count += 1
        entry['impressum_found'] = True
        
        vorname, nachname = extract_name_parts(text_content)
        email = extract_email(text_content)
        
        if not (vorname and nachname):
            entry['notes'] = 'Name not found in impressum'
    else:
        entry['notes'] = 'No impressum found'
    
    # Fallback: parse from clinic_name
    if not (vorname and nachname):
        cv, cn = parse_clinic_name(lead['clinic_name'])
        if cv and cn:
            vorname, nachname = cv, cn
            if entry['notes']:
                entry['notes'] += '; '
            entry['notes'] += 'Name from clinic_name'
    
    entry['vorname'] = vorname
    entry['nachname'] = nachname
    entry['email'] = email
    
    if vorname or nachname:
        names_count += 1
    if email:
        emails_count += 1
        entry['email_found'] = True
    
    print(f"[{i+1}/{len(original_leads)}] {lead['clinic_name'][:40]:<40} V:{vorname:<15} N:{nachname:<20} E:{email:<40} Imp:{entry['impressum_found']}")
    
    results.append(entry)

out_path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_enriched.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== SUMMARY ===")
print(f"Total: {len(results)}")
print(f"Impressum: {impressum_count}")
print(f"Names: {names_count}")
print(f"Emails: {emails_count}")
print(f"Output: {out_path}")
