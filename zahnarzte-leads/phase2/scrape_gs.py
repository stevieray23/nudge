import urllib.request, re, json, sys

# Load batch
with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_2_websites.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

def get_actual_website(gs_url):
    """Fetch GelbeSeiten page and find the actual clinic website URL."""
    try:
        req = urllib.request.Request(gs_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        # Find all external links (not gelbeseiten)
        links = re.findall(r'href="(https?://(?!www\.gelbeseiten)[^"]+)"', html)
        for url, domain in links:
            domain_lower = domain.lower()
            # Skip social media, maps, ads
            skip_domains = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'google.com/maps', 'bing.com/maps', 'yelp', 'jimdo', 'wix.com', 'wordpress', ' Squarespace']
            if any(skip in domain_lower for skip in skip_domains):
                continue
            if domain_lower.startswith('www.'):
                domain_lower = domain_lower[4:]
            # Prefer real clinic websites
            return url
        return None
    except Exception as e:
        return None

def get_impressum_data(website_url):
    """Try to find Impressum page and extract owner name + email."""
    try:
        # Try common impressum paths
        base = website_url.rstrip('/')
        if base.startswith('http://'):
            base = base.replace('http://', 'https://')
        if not base.startswith('https'):
            base = 'https://' + base

        impressum_paths = ['/impressum', '/impressum/', '/impressum.html', '/legal', '/rechtliches', '/impress', '/anbieterkennzeichnung', '/rechtliche-angaben']
        
        # Try main page first
        pages_to_try = [base] + [base + p for p in impressum_paths]
        
        for page_url in pages_to_try:
            try:
                req = urllib.request.Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
                html_lower = html.lower()
                
                if 'impressum' not in html_lower and page_url != base:
                    continue
                
                # Look for owner name patterns
                name_patterns = [
                    r'(?:Inhaber[in]*|Geschäftsführer[in]*|Verantwortlich[er]*|Betreiber[in]*|Zahnarzt[z]*|Zahnärztin|Dr\.?\s*(?:med\.?|med\. dent\.?|dent\.?)?)\s*[:\s]+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})',
                    r'(?:Inhaberin|Inhaber)\s*[^<\n]{0,50}\s*<[^>]+>\s*([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)',
                ]
                
                owner_name = None
                for pattern in name_patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    if matches:
                        owner_name = matches[0].strip()
                        break
                
                # Look for email addresses - prefer personal ones
                email_pattern = r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})'
                emails = re.findall(email_pattern, html)
                
                personal_email = None
                generic_patterns = ['info@', 'kontakt@', 'service@', 'termin@', 'praxis@', 'office@', 'admin@', 'web@', 'post@']
                for email in emails:
                    local = email.lower().split('@')[0]
                    is_generic = any(local.startswith(g.replace('@', '')) for g in generic_patterns)
                    if not is_generic:
                        personal_email = email
                        break
                
                if emails and not personal_email:
                    # fallback to first email
                    personal_email = emails[0]
                
                if owner_name or personal_email:
                    return {
                        'name': owner_name,
                        'email': personal_email,
                        'found_on': page_url
                    }
            except:
                continue
        return None
    except Exception as e:
        return None

results = []
for i, lead in enumerate(batch):
    print(f"[{i+1}/{len(batch)}] Processing: {lead['clinic_name']}")
    clinic_website = get_actual_website(lead['website'])
    print(f"  -> Actual website: {clinic_website}")
    
    result = {
        'clinic_name': lead['clinic_name'],
        'address': lead['address'],
        'city': lead['city'],
        'website': lead['website'],
        'actual_website': clinic_website,
        'vorname': '',
        'nachname': '',
        'email': '',
        'impressum_found': False,
        'email_found': False,
        'notes': ''
    }
    
    if clinic_website:
        imp = get_impressum_data(clinic_website)
        if imp:
            result['impressum_found'] = True
            if imp['name']:
                name_parts = imp['name'].split()
                if len(name_parts) >= 2:
                    result['vorname'] = name_parts[0]
                    result['nachname'] = ' '.join(name_parts[1:])
                else:
                    result['nachname'] = imp['name']
            if imp['email']:
                result['email'] = imp['email']
                result['email_found'] = True
            result['notes'] = f"Found on: {imp['found_on']}"
            print(f"  -> Name: {imp['name']}, Email: {imp['email']}")
        else:
            result['notes'] = 'Impressum page not found or no data extracted'
    else:
        result['notes'] = 'Could not extract actual clinic website from GelbeSeiten'
    
    results.append(result)

# Save results
output_path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_2_enriched.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

emails_found = sum(1 for r in results if r['email_found'])
names_found = sum(1 for r in results if r['vorname'] or r['nachname'])
print(f"\nDone! {emails_found} emails found, {names_found} names found out of {len(results)} leads")
