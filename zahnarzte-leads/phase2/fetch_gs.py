import urllib.request
import re
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_websites.json', 'r', encoding='utf-8') as f:
    leads = json.load(f)

# Known generic/non-clinic domains to skip
skip_domains = ['gelbeseiten.de', 'google.com', 'facebook.com', 'instagram.com', 
                'twitter.com', 'linkedin.com', 'bing.com', 'yahoo.com', 'bing.com']

def is_clinic_website(url):
    url_lower = url.lower()
    if any(d in url_lower for d in skip_domains):
        return False
    # Keep URLs that look like actual clinic websites
    clinic_keywords = ['praxis', 'zahn', 'dr.', 'dr ', 'dent', 'arzt', 'klinik', 'clinic', 
                       'kiefer', ' Oral', 'mund-']
    return any(kw in url_lower for kw in clinic_keywords)

for i, lead in enumerate(leads):
    url = lead['website']
    clinic_url = ''
    print(f"[{i+1}/{len(leads)}] Fetching: {url}")
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    })
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Method 1: Look for website in JSON data on page
        website_match = re.search(r'"website"\s*:\s*"((?:https?://)?[^"]+\.(?:de|com|org|info|net|at|ch))"', html, re.I)
        if website_match:
            clinic_url = website_match.group(1)
            if not clinic_url.startswith('http'):
                clinic_url = 'https://' + clinic_url
        
        # Method 2: Look for "Zur Website" links
        if not clinic_url:
            website_match = re.search(r'href="((?:https?://)?(?:www\.)?[^"\'<>]+\.(?:de|com|org|info|net))"[^>]*>\s*(?:Zur Website|Website|Webseite|Web)', html, re.I)
            if website_match:
                clinic_url = website_match.group(1)
                if not clinic_url.startswith('http'):
                    clinic_url = 'https://' + clinic_url
        
        # Method 3: Any external domain link that looks like a clinic
        if not clinic_url:
            external = re.findall(r'href="(https?://(?:www\.)?[^"\'<>]+)"', html)
            for e in external:
                if is_clinic_website(e):
                    clinic_url = e
                    break
        
        print(f"  -> Clinic website: {clinic_url}")
        lead['clinic_url_raw'] = clinic_url
    except Exception as e:
        print(f"  -> Error: {e}")
        lead['clinic_url_raw'] = ''

with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_5_with_urls.json', 'w', encoding='utf-8') as f:
    json.dump(leads, f, ensure_ascii=False, indent=2)

print("\nDone! Saved to batch_5_with_urls.json")
