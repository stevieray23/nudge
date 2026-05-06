import urllib.request, re

url = 'https://www.bing.com/search?q=Sch%C3%B6nlebe+Hagen+Zahnarzt+Dresden+impressum'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
print('Bing size:', len(html))
# Find search result links - look for organic results
links = re.findall(r'href="([^"]+)"', html)
for l in links[:80]:
    if any(x in l.lower() for x in ['sch', 'zahn', 'dresden', 'praxis', 'hagen']):
        print('Link:', l[:120])
