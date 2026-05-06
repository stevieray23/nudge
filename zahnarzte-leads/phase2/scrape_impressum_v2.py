import urllib.request
import re
import ssl
import json
import html
from urllib.parse import urljoin

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SKIP_DOMAINS = ['gelbeseiten', '11880', 'golocal', 'meinungsmeister', 'kennstdueinen',
                'bing.com', 'google.com', 'facebook.com', 'instagram.com']

IMPRESSUM_PATHS = [
    '/impressum/', '/impressum.html', '/impressum', '/impressum.php',
    '/impressum/index.html', '/impressum.php',
    '/legal/', '/legal', '/rechtliches/', '/rechtliches',
    '/anbieterkennzeichnung/', '/impressum-2/', '/ueber-uns/impressum',
    '/kontakt/impressum/'
]

GENERIC_EMAILS = ['info@', 'kontakt@', 'service@', 'post@', 'office@', 'mail@', 
                  'termin@', 'praxis@', 'klinik@', 'web@', 'hello@', 'no-reply@',
                  'empfang@', 'za-@']

def is_real_clinic_url(url):
    if not url:
        return False
    u = url.lower()
    return not any(d in u for d in SKIP_DOMAINS)

def try_url(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'de-DE,de;q=0.9'
    })
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=12)
        if resp.status == 200:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        pass
    return None

def html_to_text(html_content):
    # Remove scripts and styles first
    text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL|re.I)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL|re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_name_from_text(text):
    """Find owner/dentist name in impressum text"""
    # Clean text
    text = text.strip()
    if len(text) < 20:
        return '', ''
    
    # Try to find name after common labels
    # Look for "Inhaber", "Geschäftsführer", "Zahnarzt", "Dr."
    name_label_patterns = [
        # "Inhaber(in): Christoph Hennig" or "Inhaber: Christoph Hennig"
        r'(?:Inhaber(?:in)?|Inhaberin|Verantwortlich(?:er)?|Geschäftsführer(?:in)?|Vertreten (?:durch|von)|Betreiber(?:in)?)\s*[:\-]\s*(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?(?:Dr\.?\s*)?)?([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)\s+([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)',
        # "Christoph Hennig (Zahnarzt)" 
        r'\b([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)\s+([A-ZÄÖÜ][a-zäöüß]+(?:[-'']?[A-ZÄÖÜ][a-zäöüß]+)?)\s*(?:\(|,|\(|Zahnarzt|Inhaber)',
        # Dr. Firstname Lastname
        r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
    ]
    
    for pat in name_label_patterns:
        m = re.search(pat, text, re.I | re.U)
        if m:
            vorname = m.group(1).strip()
            nachname = m.group(2).strip()
            # Filter out very short or obvious non-name words
            if len(vorname) > 1 and len(nachname) > 1:
                # Filter out common non-name words
                skip_words = ['dent', 'med', 'dentist', 'praxis', 'zahnarzt', 'website', 
                              'für', 'und', 'oder', 'das', 'die', 'der', 'den', 'dem']
                if vorname.lower() not in skip_words and nachname.lower() not in skip_words:
                    return vorname, nachname
    
    # Fallback: look for "Dr." followed by two capitalized words
    m = re.search(r'\bDr\.?\s+(?:med\.?\s*)?(?:dent\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)', text, re.I | re.U)
    if m:
        return m.group(1), m.group(2)
    
    return '', ''

def extract_email_from_text(text):
    """Find personal email in impressum text"""
    # Find all emails
    all_emails = re.findall(r'[\w.+%-]+@[\w.-]+\.[a-zA-Z]{2,}', text)
    
    # Also look for (at) encoding
    at_emails = re.findall(r'([\w.+%-]+)\s*\(at\)\s*([\w.-]+\.[a-zA-Z]{2,})', text)
    for local, domain in at_emails:
        all_emails.append(f"{local}@{domain}")
    
    # Look for mailto links in original patterns
    mailto_emails = re.findall(r'mailto:([\w.+%-]+@[\w.-]+\.[a-zA-Z]{2,})', text)
    all_emails.extend(mailto_emails)
    
    # Remove dupes
    all_emails = list(dict.fromkeys(all_emails))
    
    # Prefer personal emails
    for email in all_emails:
        e = email.lower()
        is_generic = any(e.startswith(g) for g in GENERIC_EMAILS)
        is_praxis = 'praxis' in e and 'zahn' not in e and 'dr' not in e
        is_web = 'web' in e or 'site' in e or 'internet' in e
        if not is_generic and not is_praxis and not is_web:
            return email.lower()
    
    # If nothing personal, return first non-web generic
    for email in all_emails:
        e = email.lower()
        if not any(x in e for x in ['@google', '@facebook', '@instagram', '@linkedin']):
            return email.lower()
    
    return all_emails[0].lower() if all_emails else ''

def get_impressum_content(clinic_url):
    """Fetch impressum page from clinic website"""
    base = clinic_url.rstrip('/')
    
    # Try direct paths
    for path in [''] + IMPRESSUM_PATHS:
        url = base + path
        html_content = try_url(url)
        if html_content and len(html_content) > 500:
            # Check if this actually has impressum content
            text = html_to_text(html_content)
            if any(kw in text.lower() for kw in ['inhaber', 'zahnarzt', 'verantwortlich', 'geschaeftsfuehrer', 'angaben gem']):
                return url, html_content
    
    return None, None

def parse_name_from_clinic_name(clinic_name):
    """Fallback: parse name from clinic_name field"""
    # Pattern: "Dr. Name Name" or "Name Name" 
    m = re.search(r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)?([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})', clinic_name)
    if m:
        parts = m.group(1).strip().split()
        if len(parts) >= 2:
            return parts[0], ' '.join(parts[1:])
    return '', ''

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
emails_found_count = 0
names_found_count = 0
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
    
    print(f"\n[{i+1}/{len(original_leads)}] {lead['clinic_name']}")
    print(f"  URL: {clinic_url}")
    
    impressum_url, impressum_html = get_impressum_content(clinic_url)
    
    if impressum_html:
        impressum_count += 1
        entry['impressum_found'] = True
        
        text = html_to_text(impressum_html)
        
        # Extract name
        vorname, nachname = extract_name_from_text(text)
        
        # If no name found, try from clinic_name as fallback
        if not vorname and not nachname:
            vorname, nachname = parse_name_from_clinic_name(lead['clinic_name'])
            if vorname or nachname:
                entry['notes'] += 'Name from clinic_name field (not from impressum); '
        
        # Extract email
        email = extract_email_from_text(text)
        
        entry['vorname'] = vorname
        entry['nachname'] = nachname
        entry['email'] = email
        
        if email:
            emails_found_count += 1
            entry['email_found'] = True
        
        if vorname or nachname:
            names_found_count += 1
        
        print(f"  Impressum: {impressum_url}")
        print(f"  Vorname: {vorname}")
        print(f"  Nachname: {nachname}")
        print(f"  Email: {email}")
    else:
        # No impressum found - try to get name from clinic_name
        vorname, nachname = parse_name_from_clinic_name(lead['clinic_name'])
        entry['vorname'] = vorname
        entry['nachname'] = nachname
        entry['notes'] = 'No impressum found; name from clinic_name'
        if vorname or nachname:
            names_found_count += 1
        print(f"  NO IMPRESSUM - name from clinic_name: {vorname} {nachname}")
    
    results.append(entry)

# Save
out_path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_enriched.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n\n=== SUMMARY ===")
print(f"Total leads: {len(results)}")
print(f"Impressum pages found: {impressum_count}")
print(f"Names found: {names_found_count}")
print(f"Personal emails found: {emails_found_count}")
print(f"Output: {out_path}")
