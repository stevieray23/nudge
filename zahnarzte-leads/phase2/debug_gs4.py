import urllib.request, json, re

# Try to get the detailseite JS to find API endpoints
js_url = 'https://www.gelbeseiten.de/webgs/js/detailseite_below.js?1777456580405'
req = urllib.request.Request(js_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})
js_html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
print('JS size:', len(js_html))

# Find API-related strings
api_patterns = [
    r'["\'](https?://[^"\']*(?:api|service|content|data)[^"\']*)["\']',
    r'endpoint["\s:]+["\']([^"\']+)["\']',
    r'url["\s:]+["\']([^"\']*(?:detail|business|company|profile)[^"\']*)["\']',
    r'["\'](\/api\/[^"\']+)["\']',
    r'["\'](\/gsservice\/[^"\']+)["\']',
]
for pattern in api_patterns:
    matches = re.findall(pattern, js_html, re.IGNORECASE)
    if matches:
        unique = list(dict.fromkeys(matches))[:10]
        print(f'Pattern {pattern[:50]}: {unique}')

# Try to find fetch/XMLHttpRequest patterns
fetch_patterns = [
    r'fetch\([^)]+',
    r'XMLHttpRequest',
    r'\.open\([\'"]GET[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]',
]
for pattern in fetch_patterns:
    matches = re.findall(pattern, js_html, re.IGNORECASE)
    if matches:
        print(f'Fetch pattern {pattern[:30]}: {matches[:5]}')

# Try GelbeSeiten API directly - they have a public API at:
# https://www.gelbeseiten.de/api/...
test_urls = [
    'https://www.gelbeseiten.de/api/v1/company/dae6a367-d362-4c44-a93b-b67fc56eafa2',
    'https://www.gelbeseiten.de/api/company/dae6a367-d362-4c44-a93b-b67fc56eafa2',
    'https://www.gelbeseiten.de/gsservice/echtzeit?uuid=dae6a367-d362-4c44-a93b-b67fc56eafa2',
    'https://www.gelbeseiten.de/gsservice/detail?uuid=dae6a367-d362-4c44-a93b-b67fc56eafa2',
]
for test_url in test_urls:
    try:
        req2 = urllib.request.Request(test_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Referer': 'https://www.gelbeseiten.de/'
        })
        resp = urllib.request.urlopen(req2, timeout=5)
        content = resp.read().decode('utf-8', errors='ignore')
        print(f'URL {test_url}: Status OK, {len(content)} chars, preview: {content[:200]}')
    except Exception as e:
        print(f'URL {test_url}: {type(e).__name__}: {e}')
