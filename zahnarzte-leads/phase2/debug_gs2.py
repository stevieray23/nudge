import urllib.request, json, re

url = 'https://www.gelbeseiten.de/gsbiz/dae6a367-d362-4c44-a93b-b67fc56eafa2'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

# Find all script tags with data
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, script in enumerate(scripts):
    script = script.strip()
    if len(script) > 100:
        # Check if it contains URLs
        if 'http' in script and ('zahn' in script.lower() or 'praxis' in script.lower() or 'www' in script.lower()):
            print(f'Script {i} ({len(script)} chars):')
            # Find URLs in script
            urls = re.findall(r'["\'](https?://[^"\']+)["\']', script)
            for u in urls[:10]:
                print(' ', u)
            print('Snippet:', script[:300])
            print('---')

# Also look for data-* attributes in the page
data_patterns = [
    r'data-website=["\']([^"\']+)["\']',
    r'data-href=["\']([^"\']+)["\']',
    r'data-url=["\']([^"\']+)["\']',
    r'"websiteUrl"\s*:\s*"([^"]+)"',
    r'"homepage"\s*:\s*"([^"]+)"',
    r'"url"\s*:\s*"(https?://[^"]+)"',
]
for pattern in data_patterns:
    matches = re.findall(pattern, html)
    if matches:
        print(f'Pattern {pattern[:40]}: {matches[:3]}')

# Print first 500 chars of body
body_match = re.search(r'<body[^>]*>(.*)', html, re.DOTALL | re.IGNORECASE)
if body_match:
    print('\n=== BODY START ===')
    print(body_match.group(1)[:2000])
