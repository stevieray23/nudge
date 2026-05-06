import urllib.request, json, re

# Fetch the echtzeit page which loaded successfully
url = 'https://www.gelbeseiten.de/gsservice/echtzeit?uuid=dae6a367-d362-4c44-a93b-b67fc56eafa2'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9',
    'Referer': 'https://www.gelbeseiten.de/'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
print('Size:', len(html))

# Extract all external links
ext_links = re.findall(r'href="(https?://(?!www\.gelbeseiten)[^"]{5,200})"', html)
print('\nExternal links:')
for item in ext_links[:30]:
    link = item if isinstance(item, str) else item[0]
    print(' ', link[:100])

# Look for JSON-LD with website
json_ld = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
for j in json_ld:
    try:
        obj = json.loads(j)
        if 'website' in str(obj).lower() or 'url' in str(obj).lower():
            print('\nJSON-LD with website:')
            print(json.dumps(obj, indent=2, ensure_ascii=False)[:1000])
    except:
        pass

# Look for data attributes
for pattern in [r'data-website=["\']([^"\']+)["\']', r'data-href=["\']([^"\']+)["\']', r'data-url=["\']([^"\']+)["\']']:
    m = re.findall(pattern, html)
    if m:
        print(f'\nPattern {pattern}: {m}')

# Look for any JS variable with website
js_vars = re.findall(r'(?:var|let|const)\s+\w*[Ww]ebsite\w*\s*[=:]\s*["\']([^"\']+)["\']', html)
print('\nWebsite vars:', js_vars[:10])

# Check for hidden form fields
hidden = re.findall(r'<input[^>]+type="hidden"[^>]*value="([^"]+)"[^>]*name="([^"]+)"', html)
print('\nHidden fields:', hidden[:10])
