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
                          'empfang@', 'za-@']

# Words that are clearly NOT personal names (common German words)
BAD_NAME_WORDS = {
    'zuständige', 'kammer', 'berufsrechtliche', 'regelungen', 'angaben', 'gemäß',
    'patienten', 'willkommen', 'hier', 'ihre', 'unser', 'für', 'und', 'oder',
    'das', 'die', 'der', 'den', 'dem', 'nicht', 'sind', 'auch', 'ein', 'eine',
    'praxis', 'zahnarzt', 'zahnärztin', 'praxis', 'home', 'footer', 'kontakt',
    'termin', 'impressum', 'website', 'dental', 'ihren', 'ihrer', 'behandlung',
    'leistung', 'unseren', 'vielen', 'gmbh', 'mbh', 'bv', ' Holding', 'group',
    'ihrem', 'beratung', 'service', 'erleben', 'persoenlich', 'modern',
    'galerie', 'team', 'dieser', 'seite', 'seite', 'gestellte', 'fragen',
    'verlinkten', 'inhalte', 'externen', 'liebe', 'patientinnen', 'patienten',
    'angehörige', 'angehoerige', 'erfahren', 'spezialisten', 'vorrangiges',
    'bestreben', 'ausgebildete', 'mitarbeiter', 'beratung', 'kontakt',
    'verantwortliche', 'redaktionelle', 'verlags', 'gesellschaft', 'mbh',
    'zahn', 'mund', 'kiefer', 'heilkunde', 'praxis', 'dres', 'mvz',
    'from', 'content', 'skip', 'navigation', 'menu', 'sidebar'
}

MIN_NAME_LEN = 2  # Both parts must be at least 2 chars

def is_real_clinic_url(url):
    if not url:
        return False
    u = url.lower()
    return not any(d in u for d in SKIP_DOMAINS)

def try_url(url, timeout=12):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml'
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
    text = re.sub(r'(?i)<hr\s*/?\s*>', '\n---\n', text)
    text = re.sub(r'(?i)</(p|div|h[1-6]|li|tr)>', '\n', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = htmlmod.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text.strip()

def clean_name_part(word):
    """Remove common prefixes/suffixes from a name part"""
    word = word.strip(".,;:()[]{}")
    # Remove common titles/prefixes
    for p in ['Dr.', 'Dr', 'Frau', 'Herr', 'Herrn']:
        word = re.sub(r'^' + p + r'\s*', '', word, flags=re.I)
    return word.strip()

def extract_name_parts(text, clinic_name=''):
    """Extract [vorname, nachname] from impressum text. Returns (vorname, nachname)."""
    text = text.strip()
    if len(text) < 30:
        return '', ''
    
    def is_good_name(v, n):
        v = clean_name_part(v)
        n = clean_name_part(n)
        vl = v.lower()
        nl = n.lower()
        if len(v) < MIN_NAME_LEN or len(n) < MIN_NAME_LEN:
            return False
        if vl in BAD_NAME_WORDS or nl in BAD_NAME_WORDS:
            return False
        # Check if either part looks like a word that should not be a name
        for bad in BAD_NAME_WORDS:
            if bad in vl or bad in nl:
                if len(bad) > 3 and (vl.startswith(bad) or nl.startswith(bad)):
                    return False
        return True
    
    # Strategy 1: Meta description - often has clean "Impressum Name Surname Address"
    meta_desc = get_meta_description('<html>' + text[:5000] + '</html>')
    if meta_desc:
        # Pattern: "Impressum [Title] FirstName LastName"
        m = re.search(r'Impressum\s+(?:Angaben\s+gemäß[^\n]*\n?\s*)?(?:Zahnarzt(?:praxis)?\s*)?(?:MVZ\s*)?(?:Dr\.?\s*(?:med\.?\s*)?(?:\s*dent\.?\s*)?)?([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)\b', meta_desc, re.U)
        if m and is_good_name(m.group(1), m.group(2)):
            return clean_name_part(m.group(1)), clean_name_part(m.group(2))
        
        # "Vertreten durch: Dr. FirstName LastName"
        m = re.search(r'Vertreten\s+(?:durch|:)\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:\s*dent\.?\s*)?)?([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)', meta_desc, re.U)
        if m and is_good_name(m.group(1), m.group(2)):
            return clean_name_part(m.group(1)), clean_name_part(m.group(2))
        
        # "Inhaber: FirstName LastName"
        m = re.search(r'(?:Inhaber(?:in)?|Betreiber(?:in)?|Verantwortlich(?:er)?)[^\w]*([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)', meta_desc, re.U)
        if m and is_good_name(m.group(1), m.group(2)):
            return clean_name_part(m.group(1)), clean_name_part(m.group(2))
    
    # Strategy 2: Look in full text for label patterns
    label_patterns = [
        r'Vertreten\s+(?:durch|:)\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:\s*dent\.?\s*)?)?([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
        r'(?:Inhaber(?:in)?|Betreiber(?:in)?|Verantwortlich(?:er)?)[^\w]*([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
        r'(?:Zahnarzt|Zahnärztin|Kieferorthopäd(?:e|in)|Facharzt)[^\w]*(?:Dr\.?\s*(?:med\.?\s*)?(?:\s*dent\.?\s*)?)?([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)',
    ]
    for pat in label_patterns:
        m = re.search(pat, text, re.U)
        if m and is_good_name(m.group(1), m.group(2)):
            return clean_name_part(m.group(1)), clean_name_part(m.group(2))
    
    # Strategy 3: Dr. pattern in text
    m = re.search(r'(?:^|\n)\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:\s*dent\.?\s*)?)\s+([A-ZÄÖÜ][a-zäöüß-]+)\s+([A-ZÄÖÜ][a-zäöüß-]+)', text, re.M | re.U)
    if m and is_good_name(m.group(1), m.group(2)):
        return clean_name_part(m.group(1)), clean_name_part(m.group(2))
    
    return '', ''

def extract_email(text):
    """Extract personal email from text"""
    emails = re.findall(r'([a-zA-Z0-9.+%-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    
    # (at) encoding
    for m in re.findall(r'([a-zA-Z0-9.+%-]+)\s*\(at\)\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text):
        emails.append((m[0], m[1]))
    
    for local, domain in emails:
        email = f"{local}@{domain}".lower()
        # Skip generic prefixes
        if any(email.startswith(p.lower()) for p in GENERIC_EMAIL_PREFIXES):
            continue
        # Skip social media
        if any(x in email for x in ['@google.', '@facebook.', '@instagram.', '@linkedin.']):
            continue
        return email
    
    # Return first non-social email
    for local, domain in emails:
        email = f"{local}@{domain}".lower()
        if not any(x in email for x in ['@google.', '@facebook.', '@instagram.', '@linkedin.']):
            return email
    return ''

def parse_clinic_name(clinic_name):
    """Fallback: parse name from clinic_name field"""
    clean = re.sub(r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?|Zahnärzte?|Praxis|Zahnarztpraxis|Kieferorthopädie|Fachzahnarzt|GbR|MVZ(?: GbR)?|Kieferzentrum|Dentaparks)', '', clinic_name, flags=re.I).strip()
    clean = re.sub(r'^\s*[\&,\|]+\s*', '', clean).strip()
    
    # Dr. pattern
    m = re.search(r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)', clean, re.U)
    if m:
        v, n = m.group(1), m.group(2)
        if len(v) >= MIN_NAME_LEN and len(n) >= MIN_NAME_LEN:
            return v, n
    
    # Two capitalized words
    m = re.search(r'\b([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)\b', clean, re.U)
    if m:
        v, n = m.group(1), m.group(2)
        skip = {'Str.', 'Strasse', 'Nordrhein', 'West', 'Mitte', 'Stadtmitte', 'Ost'}
        if n not in skip and len(v) >= MIN_NAME_LEN and len(n) >= MIN_NAME_LEN:
            if v.lower() not in BAD_NAME_WORDS and n.lower() not in BAD_NAME_WORDS:
                return v, n
    
    return '', ''

def get_impressum(clinic_url):
    """Fetch impressum content from clinic URL"""
    base = clinic_url.rstrip('/')
    
    # Try impressum paths first
    for path in [''] + IMPRESSUM_PATHS:
        url = base + path
        html_content = try_url(url)
        if html_content and len(html_content) > 500:
            text = html_to_text(html_content)
            has_impressum = any(kw in text.lower() for kw in [
                'inhaber', 'verantwortlich', 'zahnarzt', 'geschaeftsfuehrer', 
                'angaben gem', 'betreiber', 'vertreten'
            ])
            if has_impressum:
                meta_desc = get_meta_description(html_content)
                return url, text, meta_desc
    
    # Try main page
    main_html = try_url(base)
    if main_html:
        text = html_to_text(main_html)
        meta_desc = get_meta_description(main_html)
        if any(kw in text.lower() for kw in ['inhaber', 'verantwortlich', 'impressum']):
            return base, text, meta_desc
    
    return None, '', ''

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
    
    print(f"[{i+1}/{len(original_leads)}] {lead['clinic_name']} -> {clinic_url}")
    
    impressum_url, text_content, meta_desc = get_impressum(clinic_url)
    
    vorname, nachname = '', ''
    email = ''
    
    if impressum_url and text_content:
        impressum_count += 1
        entry['impressum_found'] = True
        
        # Extract name
        vorname, nachname = extract_name_parts(text_content)
        
        # Extract email
        email = extract_email(text_content)
        
        if vorname and nachname:
            entry['notes'] = ''
        elif vorname or nachname:
            entry['notes'] = 'Only partial name found'
        else:
            entry['notes'] = 'Name not found in impressum'
    
    # Fallback name from clinic_name
    if not (vorname and nachname):
        cv, cn = parse_clinic_name(lead['clinic_name'])
        if cv and cn:
            vorname, nachname = cv, cn
            if entry['notes']:
                entry['notes'] += '; '
            entry['notes'] += 'Name from clinic_name field'
    
    entry['vorname'] = vorname
    entry['nachname'] = nachname
    entry['email'] = email
    
    if vorname or nachname:
        names_count += 1
    if email:
        emails_count += 1
        entry['email_found'] = True
    
    status = f"V: {vorname} {nachname} | E: {email[:40]}" if email else f"V: {vorname} {nachname} | E: (none)"
    print(f"  -> {status}")
    
    results.append(entry)

# Save
out_path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_enriched.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== SUMMARY ===")
print(f"Total: {len(results)}")
print(f"Impressum pages: {impressum_count}")
print(f"Names: {names_count}")
print(f"Emails: {emails_count}")
print(f"Output: {out_path}")
