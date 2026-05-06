import requests, re
from bs4 import BeautifulSoup

# Try DuckDuckGo for website lookup
query = 'Zahnarztpraxis Hagen Schonlebe Dresden'
url = 'https://duckduckgo.com/html/?q=' + requests.utils.quote(query)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'de-DE,de;q=0.9'
}
r = requests.get(url, headers=headers, timeout=10)
print(f'DuckDuckGo status: {r.status_code}')

# Extract result URLs from DDG HTML
matches = re.findall(r'href="(https?://[^"]+)"', r.text)
print(f'Href matches: {len(matches)}')
real_urls = [m for m in matches if m and 'duckduckgo' not in m and 'google' not in m.lower()]
for m in real_urls[:10]:
    print(f'  {m}')
