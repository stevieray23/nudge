import urllib.request, ssl, re, html as htmlmod, sys
sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_page(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'Error: {e}'

def to_text(html_content):
    text = re.sub(r'(?is)<style[^>]*>.*?</style>', ' ', html_content)
    text = re.sub(r'(?is)<script[^>]*>.*?</script>', ' ', text)
    text = re.sub(r'(?is)<!--.*?-->', ' ', text)
    text = re.sub(r'(?i)<br\s*/?\s*>', '\n', text)
    text = re.sub(r'(?i)</(p|div|h[1-6]|li|tr)>', '\n', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = htmlmod.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    return text.strip()

sites = {
    'Hennig': ('http://www.zahnarztpraxis-hennig.de/impressum/', 'Christoph Hennig'),
    'Kettel': ('https://www.zahnmedizin-kettel.de/impressum/', 'Ernst Kettel'),
    'Makowski': ('http://www.zahnarzt-makowski.de/impressum/', 'Andreas Makowski'),
    'Pantic': ('http://www.zahnarzt-pantic.de/impressum.html', 'Zoran Pantic'),
    'Hinz': ('https://www.praxis-b-hinz.de/', 'Barbara Hinz'),
    'Sternberg': ('http://www.zahnarzt-dr-sternberg.de/impressum/', 'Miroslav Sternberg'),
    'Lemonidis': ('http://www.zahnarzt-ostentor.de/impressum/', 'Konstantinos Lemonidis'),
    'Grebe': ('http://www.zahnmedizin-maerkerhaus.de/impressum/', 'Henning Grebe'),
}

for name, (url, expected) in sites.items():
    print(f'\n=== {name} (expected: {expected}) ===')
    content = get_page(url)
    if 'Error' in str(content[:20]):
        print(f'  {content}')
        continue
    text = to_text(content)
    # Print impressum section
    idx = text.lower().find('inhaber')
    if idx < 0:
        idx = text.lower().find('verantwort')
    if idx < 0:
        idx = text.lower().find('zahnarzt')
    if idx >= 0:
        section = text[max(0, idx-50):idx+600]
        print(f'  Section: {repr(section[:500])}')
    else:
        print(f'  Text (first 500): {repr(text[:500])}')
