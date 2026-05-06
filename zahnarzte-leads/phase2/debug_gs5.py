import urllib.request, json, re

# Fetch the detailseite JS
js_url = 'https://www.gelbeseiten.de/webgs/js/detailseite_below.js?1777456580405'
req = urllib.request.Request(js_url, headers={
    'User-Agent': 'Mozilla/5.0',
})
js_content = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

# Find XMLHttpRequest .open calls
xhr_calls = re.findall(r'\.open\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']', js_content)
print('XHR open calls:')
for method, url in xhr_calls[:30]:
    print(f'  {method}: {url}')

# Find all string literals with /gsservice/ or /api/
gs_strings = re.findall(r'["\'](/(?:gsservice|api|ajax)[^"\']{0,100})["\']', js_content)
print('\nGS service strings:')
for s in gs_strings[:30]:
    print(' ', s)

# Find all URLs
urls = re.findall(r'"(https?://[^"]{5,100})"', js_content)
print('\nHTTPS URLs in JS:')
for u in urls[:20]:
    print(' ', u)

# Look for variable assignments with URL patterns
var_urls = re.findall(r'(?:var|let|const)\s+\w+\s*=\s*["\'](https?://[^"\']{5,100})["\']', js_content)
print('\nURL variables:')
for v in var_urls[:10]:
    print(' ', v)

# Try to find the data loading function
data_funcs = re.findall(r'(?:load|fetch|get|retrieve|request)(?:Company|Business|Detail|Profile|Data|Content)\s*\([^)]*\)', js_content, re.IGNORECASE)
print('\nData functions:')
for f in data_funcs[:10]:
    print(' ', f)
