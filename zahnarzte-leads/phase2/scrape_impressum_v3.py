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
    '/praxis/impressum/', '/start/impressum/'
]

GENERIC_EMAIL_PREFIXES = ['info@', 'kontakt@', 'service@', 'post@', 'office@', 'mail@', 
                          'termin@', 'praxis@', 'klinik@', 'web@', 'hello@', 'no-reply@',
                          'empfang@', 'kontakt.']  # 'kontakt.' like 'kontakt.praxis@'

def is_real_clinic_url(url):
    if not url:
        return False
    u = url.lower()
    return not any(d in u for d in SKIP_DOMAINS)

def try_url(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml'
    })
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=12)
        if resp.status == 200:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        pass
    return None

def extract_meta_description(html_content):
    """Extract meta description - often has clean impressum summary"""
    m = re.search(r'<meta\s+(?:name|id)=["\']description["\']\s+content=["\']([^"\']+)["\']', html_content, re.I)
    if not m:
        m = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+(?:name|id)=["\']description["\']', html_content, re.I)
    if m:
        return m.group(1).strip()
    return ''

def extract_meta_title(html_content):
    m = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.I)
    if m:
        return m.group(1).strip()
    return ''

def html_to_text(html_content):
    """Better HTML to text conversion that preserves some structure"""
    # Remove scripts and styles
    text = re.sub(r'(?is)<style[^>]*>.*?</style>', ' ', html_content)
    text = re.sub(r'(?is)<script[^>]*>.*?</script>', ' ', text)
    text = re.sub(r'(?is)<!--.*?-->', ' ', text)
    # Replace common separators
    text = re.sub(r'(?i)<br\s*/?\s*>', '\n', text)
    text = re.sub(r'(?i)<hr\s*/?\s*>', '\n---\n', text)
    # Replace block elements with newlines
    text = re.sub(r'(?i)</(p|div|h[1-6]|li|tr)>', '\n', text)
    # Remove remaining tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode entities
    text = htmlmod.unescape(text)
    # Clean whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text.strip()

def extract_name_from_text(text, clinic_name=''):
    """Find dentist/owner name in impressum text"""
    text = text.strip()
    if len(text) < 30:
        return '', ''
    
    # Strategy 1: Look for meta description pattern "Impressum [Title/Name] [Address]"
    # e.g. "Impressum Zahnarzt Christoph Hennig Breslauer Straße 20"
    m = re.search(r'Impressum\s+(?:Zahnarzt(?:praxis)?\s*)?(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)?([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)\s+([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)\b', text, re.U)
    if m:
        v, n = m.group(1), m.group(2)
        if len(v) > 1 and len(n) > 1:
            return v, n
    
    # Strategy 2: Look for label patterns
    label_patterns = [
        # "Verantwortlich gemäß § 18 Abs. 2 MStV: FirstName LastName"
        r'(?:Verantwortlich(?:er)?|Inhaber(?:in)?|Geschäftsführer(?:in)?|Betreiber(?:in)?)\s*(?:gemäß|\s)\s*(?:§\s*\d+\s*[^\n:]*[:\-])?\s*([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)\s+([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)',
        # "Zahnarzt: FirstName LastName"
        r'(?:Zahnarzt|Zahnärztin|Kieferorthopäde|Fachzahnarzt)[^\w]*([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)\s+([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)',
    ]
    for pat in label_patterns:
        m = re.search(pat, text, re.U)
        if m:
            v, n = m.group(1), m.group(2)
            if len(v) > 1 and len(n) > 1 and not any(w in v.lower() for w in ['gem', 'abs', 'mstv', 'ddg', 'mfg', 'für']):
                return v, n
    
    # Strategy 3: "Dr." followed by two capitalized words  
    m = re.search(r'(?:^|\n)\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:\s*dent\.?\s*)?|Herr|Frau)\s+([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)', text, re.M | re.U)
    if m:
        v, n = m.group(1), m.group(2)
        if len(v) > 1 and len(n) > 1:
            return v, n
    
    return '', ''

def extract_email_from_text(text):
    """Find email in text"""
    emails = re.findall(r'([a-zA-Z0-9.+%-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    
    # Also look for (at) format
    at_emails = re.findall(r'([a-zA-Z0-9.+%-]+)\s*\(at\)\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    for l, d in at_emails:
        emails.append((l, d))
    
    for local, domain in emails:
        email = f"{local}@{domain}".lower()
        # Skip if starts with generic prefix
        is_generic = any(email.startswith(p.lower()) for p in GENERIC_EMAIL_PREFIXES)
        if not is_generic:
            return email
    
    # Return first non-social email
    for local, domain in emails:
        email = f"{local}@{domain}".lower()
        if not any(x in email for x in ['@google.', '@facebook.', '@instagram.', '@linkedin.']):
            return email
    
    return ''

def parse_clinic_name(clinic_name):
    """Parse first/last name from the clinic_name field"""
    # Remove common suffixes
    clean = re.sub(r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?|Zahnärzte?|Praxis|Zahnarztpraxis|Kieferorthopädie|Fachzahnarzt|GbR|MVZ|MVZ GbR|Kieferzentrum)', '', clinic_name, flags=re.I).strip()
    
    # Look for Dr. pattern
    m = re.search(r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)', clean, re.U)
    if m:
        return m.group(1), m.group(2)
    
    # Look for two capitalized words
    m = re.search(r'\b([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)', clean, re.U)
    if m:
        v, n = m.group(1), m.group(2)
        # Skip if it looks like an address part
        skip = ['Str.', 'Strasse', 'straße', 'Nordrhein', 'West', 'Mitte', 'Stadtmitte']
        if n not in skip:
            return v, n
    
    return '', ''

def get_impressum(url):
    """Get impressum content from clinic URL"""
    base = url.rstrip('/')
    
    # First: try to get meta description from main page as it often has clean name
    main_html = try_url(base)
    meta_desc = ''
    if main_html:
        meta_desc = extract_meta_description(main_html)
    
    # Try impressum paths
    for path in IMPRESSUM_PATHS:
        impressum_url = base + path
        html_content = try_url(impressum_url)
        if html_content and len(html_content) > 500:
            text = html_to_text(html_content)
            # Check if it looks like impressum
            if any(kw in text.lower() for kw in ['inhaber', 'verantwortlich', 'zahnarzt', 'geschaeftsfuehrer', 'angaben gem', 'betreiber']):
                # Also try meta description from impressum page
                imp_meta = extract_meta_description(html_content)
                if imp_meta and len(imp_meta) > len(meta_desc):
                    meta_desc = imp_meta
                return impressum_url, html_content, text, meta_desc
    
    # Try main page if no impressum found
    if main_html:
        text = html_to_text(main_html)
        if any(kw in text.lower() for kw in ['inhaber', 'verantwortlich', 'impressum']):
            return base, main_html, text, meta_desc
    
    return None, None, '', meta_desc

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
emails_found = 0
names_found = 0
impressum_found = 0

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
        entry['notes'] = 'No clinic website found'
        results.append(entry)
        continue
    
    print(f"\n[{i+1}/{len(original_leads)}] {lead['clinic_name']}")
    print(f"  URL: {clinic_url}")
    
    impressum_url, html_content, text_content, meta_desc = get_impressum(clinic_url)
    
    vorname, nachname = '', ''
    email = ''
    
    if text_content:
        impressum_found += 1
        entry['impressum_found'] = True
        
        # Extract name from text
        vorname, nachname = extract_name_from_text(text_content, lead['clinic_name'])
        
        # If not found in text, try meta description
        if not (vorname and nachname) and meta_desc:
            vorname, nachname = extract_name_from_text(meta_desc, lead['clinic_name'])
        
        # Extract email from text
        email = extract_email_from_text(text_content)
        
        print(f"  Impressum: {impressum_url}")
        print(f"  Meta desc: {meta_desc[:100]}")
        print(f"  Vorname: {vorname}, Nachname: {nachname}")
        print(f"  Email: {email}")
    
    # Fallback: parse from clinic_name
    if not (vorname and nachname):
        v, n = parse_clinic_name(lead['clinic_name'])
        if v and n:
            vorname, nachname = v, n
            entry['notes'] = 'Name from clinic_name (not from impressum)'
            print(f"  Name from clinic_name: {vorname} {nachname}")
    
    entry['vorname'] = vorname
    entry['nachname'] = nachname
    entry['email'] = email
    
    if vorname or nachname:
        names_found += 1
    if email:
        emails_found += 1
        entry['email_found'] = True
    
    results.append(entry)

# Save
out_path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_enriched.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n\n=== SUMMARY ===")
print(f"Total: {len(results)}")
print(f"Impressum found: {impressum_found}")
print(f"Names: {names_found}")
print(f"Emails: {emails_found}")
print(f"Saved: {out_path}")
