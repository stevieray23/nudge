import urllib.request, ssl, re, html as htmlmod, sys
sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_meta_desc(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        content = resp.read().decode('utf-8', errors='ignore')
        m = re.search(r'<meta[^>]*(?:name|id)=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.I)
        if not m:
            m = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*(?:name|id)=["\']description["\']', content, re.I)
        return m.group(1)[:200] if m else 'NOT FOUND'
    except Exception as e:
        return f'Error: {e}'

# Check problematic sites
sites = {
    'praxis-b-hinz': 'http://www.praxis-b-hinz.de/impressum/',
    'dentaparks': 'https://www.dentaparks.de/impressum/',
    'zahnmedizin-kettel': 'https://www.zahnmedizin-kettel.de/impressum/',
    'zahnwandel': 'http://www.zahnwandel.de/kontakt/impressum/',
    'dortmund-kieferchirurgie': 'http://www.dortmund-kieferchirurgie.de/impressum/',
    'zz-do': 'https://zz-do.de/zahnarzt-dortmund-kruegerhaus/impressum/',
    'zahnarzt-pantic': 'http://www.zahnarzt-pantic.de/impressum.html',
    'zahnarzt-josephs': 'http://www.zahnarztpraxis-josephs.de/impressum.html',
    'zahnarzt-koegalerie': 'http://www.zahnarzt-koegalerie.de/',
    'dortmund-zahnarzt-mueller': 'http://www.dortmund-zahnarzt-mueller.de/impressum/',
    'zahnarzt-eckhardt': 'https://www.zahnarzt-eckhardt.de/impressum.html',
    'zahnarzt-ostentor': 'http://www.zahnarzt-ostentor.de/impressum/',
    'doc-zahnaerzte': 'https://doc-zahnaerzte.de/impressum/',
}

for name, url in sites.items():
    desc = get_meta_desc(url)
    print(f'{name}: {desc}')
    print()
