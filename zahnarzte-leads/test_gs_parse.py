import httpx, re

HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36', 'Accept-Language': 'de-DE,de;q=0.9'}

r = httpx.get('https://www.gelbeseiten.de/suche/zahnarzt/berlin', headers=HDRS, timeout=15.0, follow_redirects=True)
html = r.text

# Extract each article block
articles = re.findall(r'<article[^>]+data-realid="([0-9a-f-]{36})"[^>]*>(.*?)</article>', html, re.I | re.DOTALL)
print(f'Articles found: {len(articles)}')

listings = []
for uuid, content in articles:
    # Get the main link
    link_m = re.search(r'href="(https://www\.gelbeseiten\.de/gsbiz/[^"]+)"', content, re.I)
    gs_url = link_m.group(1) if link_m else f'https://www.gelbeseiten.de/gsbiz/{uuid}'
    
    # Get name - look for it in the content
    name_m = re.search(r'aria-label=["\']([^"\']+)["\']', content, re.I)
    if not name_m:
        name_m = re.search(r'<h[12][^>]*>\s*<a[^>]*>\s*([^<\n]{3,80})\s*</a>', content, re.I)
    if not name_m:
        name_m = re.search(r'<span[^>]*class="[^"]*(?:name|title)[^"]*"[^>]*>([^<]{3,80})</span>', content, re.I)
    if not name_m:
        name_m = re.search(r'class="[^"]*entry[^"]*name[^"]*"[^>]*>([^<\n]{3,80})', content, re.I)
    
    name = name_m.group(1).strip() if name_m else ''
    name = re.sub(r'<[^>]+>', '', name).strip()
    name = re.sub(r'^(Dr\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|'
                  r'Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|'
                  r'Kieferorthopädie\s*|Gold Partner\s*|Premium Partner\s*|Silber Partner\s*|'
                  r'Bronze Partner\s*)', '', name, flags=re.I).strip()
    
    if name and len(name) >= 3:
        listings.append({'name': name, 'uuid': uuid, 'gs_url': gs_url})

print(f'Valid listings: {len(listings)}')
for l in listings[:5]:
    print(f'  {l["name"]} | {l["gs_url"]}')
