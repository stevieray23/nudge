import urllib.request, json, re

url = 'https://www.gelbeseiten.de/gsbiz/dae6a367-d362-4c44-a93b-b67fc56eafa2'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

print('HTML size:', len(html))

# Find JSON-LD
json_matches = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
for jm in json_matches[:3]:
    print('JSON-LD:', jm[:500])
    print('---')

# Find window data
window_matches = re.findall(r'window\.__.*?=.*?(\{.*?\});', html, re.DOTALL)
for wm in window_matches[:2]:
    print('Window data:', wm[:300])
    print('---')

# Look for website in HTML
website_in_html = re.findall(r'"website"\s*:\s*"([^"]+)"', html, re.IGNORECASE)
for w in website_in_html[:5]:
    print('Website:', w)

# Find all external links
ext_links = re.findall(r'href="(https?://(?!www\.gelbeseiten)[^"]+)"', html)
for item in ext_links[:20]:
    if isinstance(item, tuple):
        print('Ext link:', item[1], '->', item[0][:80])
    else:
        print('Ext link:', item[:80])

# Print all JSON-LD fully
print('\n=== ALL JSON-LD ===')
for jm in json_matches:
    try:
        obj = json.loads(jm)
        print(json.dumps(obj, indent=2, ensure_ascii=False)[:2000])
        print('---')
    except:
        print(jm[:500])
        print('---')
