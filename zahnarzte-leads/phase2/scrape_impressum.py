import urllib.request
import re
import ssl
import json
import html
from urllib.parse import urljoin

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Directories to skip
SKIP_DOMAINS = ['gelbeseiten', '11880', 'golocal', 'meinungsmeister', 'kennstdueinen',
                'bing.com', 'google.com', 'facebook.com', 'instagram.com']

IMPRESSUM_PATHS = [
    '/impressum/', '/impressum.html', '/impressum', '/impressum.php',
    '/legal/', '/legal', '/rechtliches/', '/rechtliches',
    '/anbieterkennzeichnung/', '/anbieter'
]

GENERIC_EMAILS = ['info@', 'kontakt@', 'service@', 'post@', 'office@', 'mail@', 
                  'termin@', 'praxis@', 'klinik@', 'web@', 'hello@', 'no-reply@']

def is_real_clinic_url(url):
    if not url:
        return False
    u = url.lower()
    return not any(d in u for d in SKIP_DOMAINS) and any(k in u for k in ['.de', '.com', '.org', '.net'])

def try_urls(base_url, paths):
    """Try fetching multiple URL paths, return first successful"""
    for path in paths:
        url = base_url.rstrip('/') + path
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,Accept-Language: de-DE,de;q=0.9'
        })
        try:
            resp = urllib.request.urlopen(req, context=ctx, timeout=10)
            if resp.status == 200:
                html_content = resp.read().decode('utf-8', errors='ignore')
                ct = resp.headers.get('Content-Type', '')
                if 'text/html' in ct or not ct:
                    return url, html_content
        except Exception:
            pass
    return None, None

def extract_impressum(html_content, base_url):
    """Extract owner name and email from impressum page"""
    # Decode HTML entities
    text = html.unescape(html_content)
    
    result = {
        'vorname': '',
        'nachname': '',
        'email': '',
        'notes': ''
    }
    
    # Find emails - look for personal ones first (not generic)
    all_emails = re.findall(r'[\w.+%+-]+@[\w.-]+\.[a-zA-Z]{2,}', text)
    personal_emails = [e for e in all_emails if not any(e.lower().startswith(g) for g in GENERIC_EMAILS)]
    
    if personal_emails:
        result['email'] = personal_emails[0]
    elif all_emails:
        result['email'] = all_emails[0]
        result['notes'] += ' [WARNING: only generic email found] '
    
    # Find owner/Inhaber name
    # Common patterns: "Inhaber(in)", "Geschäftsführer", "Zahnarzt/Zahnärztin", "Dr."
    name_patterns = [
        r'(?:Inhaber[in]*|Geschäftsführer[in]*|Vertreten durch|Verantwortlich)[^a-zA-ZäöüÄÖÜß]*(?:Dr\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+(?:\s+(?:von|van|der))?\s+[A-ZÄÖÜ][a-zäöüß]+)',
        r'(?:Zahnarzt|Zahnärztin|Arzt|Ärztin)[^a-zA-ZäöüÄÖÜß]*(?:Dr\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+(?:\s+(?:von|van|der|de[nr]?))?\s+[A-ZÄÖÜ][a-zäöüß]+)',
        r'(?:Herr|Frau)[^a-zA-ZäöüÄÖÜß]*(?:Dr\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'\bDr\.?\s+(?:med\.?\s*)?(?:dent\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
    ]
    
    full_name = ''
    for pat in name_patterns:
        m = re.search(pat, text, re.I)
        if m:
            if len(m.groups()) == 2:
                full_name = f"{m.group(1)} {m.group(2)}"
            else:
                full_name = m.group(1)
            break
    
    if full_name:
        parts = full_name.strip().split()
        if len(parts) >= 2:
            result['vorname'] = parts[0]
            result['nachname'] = ' '.join(parts[1:])
        elif len(parts) == 1:
            result['nachname'] = parts[0]
    
    # Also try to extract from the raw HTML with HTML entities
    if not result['vorname'] and not result['nachname']:
        # Try finding in HTML source
        name_match = re.search(r'(?:Inhaber|Geschäftsführer)[^<>]*(?:Dr\.?\s*)?<[^>]*>([^<]+)<[^>]*>.*?<[^>]*>([^<]+)<', html_content)
        if name_match:
            result['vorname'] = name_match.group(1).strip()
            result['nachname'] = name_match.group(2).strip()
    
    return result

# Load leads
with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_websites.json', 'r', encoding='utf-8') as f:
    original_leads = json.load(f)

# Load clinic URLs we discovered
with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_with_urls.json', 'r', encoding='utf-8') as f:
    urls_data = json.load(f)

# Build clinic URL lookup
url_lookup = {}
for item in urls_data:
    gs_url = item['website']
    clinic_url = item.get('clinic_url_raw', '')
    if is_real_clinic_url(clinic_url):
        url_lookup[gs_url] = clinic_url

# Process each lead
results = []
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
        entry['notes'] = 'No clinic website found (only Gelbeseiten/directory link)'
        results.append(entry)
        continue
    
    print(f"\n[{i+1}/{len(original_leads)}] {lead['clinic_name']}")
    print(f"  Clinic URL: {clinic_url}")
    
    # Try main page first to look for impressum links
    main_url, main_html = try_urls(clinic_url, [''])
    impressum_url = None
    impressum_html = None
    
    if main_html:
        # Look for impressum links on main page
        impressum_link = re.search(r'href=["\']([^"\']*(?:impressum|rechtliches|legal|anbieterkennzeichnung)[^"\']*)["\']', main_html, re.I)
        if impressum_link:
            impressum_url = urljoin(clinic_url, impressum_link.group(1))
            print(f"  Found impressum link: {impressum_url}")
        else:
            # Try common impressum paths
            alt_url, alt_html = try_urls(clinic_url, IMPRESSUM_PATHS)
            if alt_url:
                impressum_url = alt_url
                impressum_html = alt_html
    else:
        # No main page, try impressum paths directly
        alt_url, alt_html = try_urls(clinic_url, IMPRESSUM_PATHS)
        if alt_url:
            impressum_url = alt_url
            impressum_html = alt_html
    
    # If we found an impressum link on main page, fetch it
    if impressum_url and not impressum_html:
        req = urllib.request.Request(impressum_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'de-DE,de;q=0.9'
        })
        try:
            resp = urllib.request.urlopen(req, context=ctx, timeout=10)
            impressum_html = resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"  Failed to fetch impressum: {e}")
    
    if impressum_html:
        entry['impressum_found'] = True
        data = extract_impressum(impressum_html, impressum_url)
        entry['vorname'] = data['vorname']
        entry['nachname'] = data['nachname']
        entry['email'] = data['email']
        entry['notes'] = data['notes']
        if data['email']:
            entry['email_found'] = True
        
        print(f"  Vorname: {data['vorname']}")
        print(f"  Nachname: {data['nachname']}")
        print(f"  Email: {data['email']}")
    else:
        entry['notes'] += ' Impressum page not found'
        print(f"  No impressum found")
    
    results.append(entry)

# Save results
out_path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_enriched.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

emails_found = sum(1 for r in results if r.get('email_found'))
names_found = sum(1 for r in results if r.get('vorname') or r.get('nachname'))
impressum_found = sum(1 for r in results if r.get('impressum_found'))

print(f"\n\n=== SUMMARY ===")
print(f"Total leads: {len(results)}")
print(f"Impressum pages found: {impressum_found}")
print(f"Names found: {names_found}")
print(f"Personal emails found: {emails_found}")
print(f"Output: {out_path}")
