import urllib.request, json, re

url = 'https://www.gelbeseiten.de/gsbiz/dae6a367-d362-4c44-a93b-b67fc56eafa2'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

# Find API endpoints in JS
api_patterns = [
    r'(?:api|fetch|xhr|ajax|axios|request)\s*[(:=]\s*["\']([^"\']+)["\']',
    r'["\'](/api/[^"\']+)["\']',
    r'"endpoint"\s*:\s*"([^"]+)"',
    r'baseURL\s*[=:]\s*"([^"]+)"',
]
for pattern in api_patterns:
    matches = re.findall(pattern, html, re.IGNORECASE)
    if matches:
        print(f'API pattern: {matches[:5]}')

# Look for main JS files and get their URLs
js_files = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
print('\nJS files:')
for jf in js_files[:20]:
    print(' ', jf)

# Look for all URLs with gelbeseiten api
gs_api_urls = re.findall(r'["\']((?:/api|/ajax|/rpc|rest)[^"\']+)["\']', html)
print('\nGS API URLs:')
for u in gs_api_urls[:20]:
    print(' ', u)

# Find the main JS bundle that loads company data
main_js = [j for j in js_files if 'main' in j.lower() or 'bundle' in j.lower() or 'app' in j.lower() or 'chunk' in j.lower()]
print('\nMain JS files:')
for j in main_js[:10]:
    print(' ', j)

# Look for fetch calls
fetch_calls = re.findall(r'fetch\(["\']([^"\']+)["\']', html)
print('\nFetch calls:')
for f in fetch_calls[:10]:
    print(' ', f)

# Try to find the data loading section
# Look for any URL construction
url_construction = re.findall(r'(?:https?://)?(?:www\.)?gelbeseiten\.de[^\s"\'<>]{10,100}', html)
for u in url_construction[:20]:
    print('GS URL:', u)

# Get all links from HTML
all_links = re.findall(r'href=["\']([^"\']+)["\']', html)
print('\nAll links with website in them:')
for link in all_links:
    if 'website' in link.lower() or 'weburl' in link.lower() or 'homepage' in link.lower() or 'extern' in link.lower():
        print(' ', link)
