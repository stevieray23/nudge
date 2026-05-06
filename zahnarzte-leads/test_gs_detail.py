import httpx, re

HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36', 'Accept-Language': 'de-DE,de;q=0.9'}

r = httpx.get('https://www.gelbeseiten.de/gsbiz/5f06ccb6-068f-4b36-91a4-63113f066676', headers=HDRS, timeout=15.0, follow_redirects=True)
html = r.text

# Find the real clinic website in context
idx = html.find('zahnaerztin-neukoelln.de')
if idx >= 0:
    start = max(0, idx-200)
    end = min(len(html), idx+200)
    ctx = html[start:end]
    print('Context around real website:')
    print(ctx)
    print()

# Also look for patterns
patterns = [
    r'class="[^"]*website[^"]*"[^>]*href="([^"]+)"',
    r'class="[^"]*Zur Website[^"]*"[^>]*href="([^"]+)"',
    r'data-[a-z]+="[^"]*website[^"]*"',
    r'"website":\s*"\/?([^"]+)"',
    r'"url":\s*"\/?([^"]+)"',
    r'"link":\s*"\/?([^"]+)"',
    r'<a[^>]+href="(https?://(?!www\.gelbeseiten)[^"?#]+)"[^>]*>\s*Website',
]

for pat in patterns:
    m = re.search(pat, html, re.I)
    if m:
        print(f'Pattern: {pat[:50]} -> {m.group(1)}')

# Find all external links that are NOT ads/trackers
ext = re.findall(r'href="(https?://(?!www\.gelbeseiten\.de|wwa\.wipe|adfarm|consentmanager|adition)[^"?#\s]+)"', html, re.I)
print('\nNon-ad external links:')
for l in ext:
    print(f'  {l}')
