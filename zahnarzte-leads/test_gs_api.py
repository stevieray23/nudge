import re, httpx, json

# Try to find API endpoints in Gelbe Seiten HTML
url = 'https://www.gelbeseiten.de/suche/zahnarzt/berlin'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36', 'Accept': 'application/json, text/html, */*', 'Accept-Language': 'de-DE,de;q=0.9', 'X-Requested-With': 'XMLHttpRequest'}

r = httpx.get(url, headers=headers, timeout=15)
html = r.text

# Look for JSON data in script tags
json_patterns = re.findall(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', html, re.DOTALL)
print(f'JSON data found: {len(json_patterns)}')

# Look for API URLs
api_urls = re.findall(r'["\'](/api/[^"\']+)["\']', html)
print(f'API URLs: {api_urls[:10]}')

# Look for fetch/XHR URLs in scripts
fetch_urls = re.findall(r'fetch\(["\']([^"\']+)["\']', html)
print(f'Fetch URLs: {fetch_urls[:5]}')

# Look for GraphQL or query endpoints
gql = re.findall(r'endpoint["\']?\s*[:=]\s*["\']([^"\']+)["\']', html)
print(f'Endpoints: {gql[:5]}')

# Try to find any search API
search_api = re.findall(r'["\'](/ Branchenbuch Suche[^"\']+)["\']', html)
print(f'Search API: {search_api[:5]}')

# Check for JSON-LD
json_ld = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
print(f'JSON-LD blocks: {len(json_ld)}')

# Try a direct search API
api_search = 'https://www.gelbeseiten.de/api/1.0/search/zahnarzt/berlin'
r2 = httpx.get(api_search, headers=headers, timeout=10)
print(f'API search status: {r2.status_code}')
print(f'API search response: {r2.text[:500]}')
