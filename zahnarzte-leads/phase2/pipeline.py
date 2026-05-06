import urllib.request, json, re, time, html as html_module
from urllib.parse import urljoin, quote

# ── Impressum extractor ──────────────────────────────────────────────────────

IMPRESSUM_PATHS = [
    '/impressum', '/impressum/', '/impressum.html',
    '/legal', '/rechtliches', '/impress', '/anbieterkennzeichnung',
    '/rechtliche-angaben', '/kontakt', '/ueber-uns'
]

GENERIC_EMAILS = ['info@', 'kontakt@', 'service@', 'termin@', 'praxis@',
                  'office@', 'admin@', 'web@', 'post@', 'mail@', 'hello@']

def get_page(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='ignore')
    except Exception:
        return None

def extract_impressum(base_url):
    """Try to find and parse an Impressum page. Returns (name, email, found_url)."""
    if not base_url.startswith('http'):
        base_url = 'https://' + base_url
    base_url = base_url.rstrip('/')

    pages_to_try = [base_url] + [base_url + p for p in IMPRESSUM_PATHS]

    for page_url in pages_to_try:
        html = get_page(page_url, timeout=8)
        if not html:
            continue

        html_lc = html.lower()
        if 'impressum' not in html_lc and page_url != base_url:
            continue

        # Extract emails
        emails = re.findall(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', html)
        personal_email = None
        for e in emails:
            local = e.lower().split('@')[0]
            if not any(local.startswith(g.replace('@', '')) for g in GENERIC_EMAILS):
                personal_email = e
                break
        if not personal_email and emails:
            personal_email = emails[0]

        # Extract owner name - look for Inhaber/Geschäftsführer patterns
        name = None

        # Pattern 1: labelled field
        name_patterns = [
            r'(?:Inhaber[in]*|Geschäftsführer[in]*|Verantwortlich[er]*|Betreiber[in]*)\s*[:\-–]\s*([A-ZÄÖÜ][a-zäöüß\-]+(?:\s+[A-ZÄÖÜ][a-zäöüß\-]+){1,2})',
            r'(?:Zahnarzt[z]*|Zahnärztin)\s*[:\-–]\s*([A-ZÄÖÜ][a-zäöüß\-]+(?:\s+[A-ZÄÖÜ][a-zäöüß\-]+){1,2})',
            r'(?:Praxis|inhaberin|inhaber)\s*[:\-–]\s*([A-ZÄÖÜ][a-zäöüß\-]+(?:\s+[A-ZÄÖÜ][a-zäöüß\-]+){1,2})',
            r'(?:Dr\.?\s*(?:med\.?|med\.?\s*dent\.?|dent\.?)?)\s+([A-ZÄÖÜ][a-zäöüß\-]+)\s+([A-ZÄÖÜ][a-zäöüß\-]+)',
        ]

        for pattern in name_patterns:
            m = re.search(pattern, html, re.IGNORECASE)
            if m:
                name = ' '.join(g for g in m.groups() if g).strip()
                break

        # Pattern 2: look in HTML structure for name fields
        if not name:
            # Try to find text near labels
            label_patterns = [
                r'(?:Inhaber[in]*|Geschäftsführer[in]*|Zahnärztin|Zahnarzt)\s*</[^>]+>\s*<[^>]+>\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,2})',
            ]
            for lp in label_patterns:
                m = re.search(lp, html, re.IGNORECASE)
                if m:
                    name = m.group(1).strip()
                    break

        if name or personal_email:
            return name, personal_email, page_url

    return None, None, None

# ── GelbeSeiten: get actual website from profile ────────────────────────────

def get_gs_website(gs_url):
    """Fetch GelbeSeiten page HTML and extract the real clinic website URL via any method."""
    try:
        req = urllib.request.Request(gs_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'de-DE,de;q=0.9',
            'Referer': 'https://www.google.com/'
        })
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

        # Method 1: look for external links that look like clinic websites
        ext_links = re.findall(r'href="(https?://(?!www\.gelbeseiten)[^"]+)"', html)
        skip = {'facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'google.com/maps',
                'bing.com', 'yelp', 'apple.com', 'amazon', 'docinsider', 'dastelefonbuch',
                'dasoertliche', 'tiktok', 'pinterest', 'cloudflare', 'doubleclick', 'consentmanager'}
        for url, domain in ext_links:
            d = domain.lower()
            if d.startswith('www.'):
                d = d[4:]
            if not any(s in d for s in skip):
                # Looks like a real website
                return url

        # Method 2: look for data attributes
        for pat in [r'data-website="([^"]+)"', r'data-url="([^"]+)"', r'data-href="([^"]+)"']:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                return m.group(1)

        return None
    except Exception as e:
        return None

# ── Main ─────────────────────────────────────────────────────────────────────

with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_2_websites.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

results = []
for i, lead in enumerate(batch):
    print(f'[{i+1}/{len(batch)}] {lead["clinic_name"][:50]}')

    actual_url = get_gs_website(lead['website'])
    print(f'  -> actual URL: {actual_url}')

    rec = {
        'clinic_name': lead['clinic_name'],
        'address': lead['address'],
        'city': lead['city'],
        'website': lead['website'],
        'actual_website': actual_url,
        'vorname': '', 'nachname': '', 'email': '',
        'impressum_found': False, 'email_found': False,
        'notes': ''
    }

    if actual_url:
        name, email, found_url = extract_impressum(actual_url)
        if name:
            parts = name.split()
            rec['vorname'] = parts[0]
            rec['nachname'] = ' '.join(parts[1:])
            rec['impressum_found'] = True
            print(f'  -> name: {name}, email: {email}')
        if email:
            rec['email'] = email
            rec['email_found'] = True
        if name or email:
            rec['notes'] = f'Found on: {found_url}'
        else:
            rec['notes'] = 'Impressum not found'
    else:
        rec['notes'] = 'Could not extract clinic website from GelbeSeiten'

    results.append(rec)
    time.sleep(0.5)  # be polite

# Save
out = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_2_enriched.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

emails = sum(1 for r in results if r['email_found'])
names  = sum(1 for r in results if r['vorname'] or r['nachname'])
found_urls = sum(1 for r in results if r['actual_website'])
print(f'\nDone. {found_urls}/{len(results)} websites found, {names} names, {emails} emails')
