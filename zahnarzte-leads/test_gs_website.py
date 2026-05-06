import httpx, re

HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36', 'Accept-Language': 'de-DE,de;q=0.9'}

r = httpx.get('https://www.gelbeseiten.de/suche/zahnarzt/berlin', headers=HDRS, timeout=15.0, follow_redirects=True)
html = r.text

# Find external website links in articles
# Look for patterns like: href="http://www.clinicname.de"
external_links = re.findall(r'href="(https?://(?!www\.gelbeseiten\.de|plus\.google|facebook|instagram|linkedin|twitter|bing)[^"?#\s]+)"', html, re.I)
print(f'External links found: {len(external_links)}')
unique_links = list(dict.fromkeys(external_links))
print(f'Unique: {len(unique_links)}')
for lnk in unique_links[:10]:
    print(f'  {lnk}')

# Also check for data attributes with website URLs
website_attrs = re.findall(r'data-[a-z]+=["\']https?://[^"\']+["\']', html, re.I)
print(f'\ndata-* website attrs: {len(website_attrs)}')
for a in website_attrs[:5]:
    print(f'  {a}')

# Check for JSON data with URLs
json_urls = re.findall(r'"(https?://(?!www\.gelbeseiten)[^"]+)"', html)
print(f'\nJSON URLs: {len(json_urls)}')
for u in json_urls[:5]:
    print(f'  {u}')
