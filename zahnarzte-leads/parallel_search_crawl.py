"""
Lightweight Google search + impressum crawl.
Uses httpx to search and scrape, parallelized.
"""
import asyncio, csv, re, json, time, sys
import httpx
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chaze\zahnarzte-leads')
OUT_CSV = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\google_emails.csv')

HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
}

GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz'}
PUBLIC = {'gmail.com','yahoo.com','hotmail','outlook.com','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com'}
BAD = {'sentry','usercentrics','cookiebot','kzvh','kzvr','zaek','aekwl','bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi','blzk','bezirksstelle','zahnarztboerse','dentale','google.com','facebook','instagram','linkedin','xing','twitter','bit.ly','domain.com','alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft','sentry.io','sentry-next.wixpress.com'}
CHAIN = {'alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft'}

def is_bad(e):
    if not e or '@' not in e: return True
    lo = e.lower(); local = lo.split('@')[0]; domain = lo.split('@')[1] if '@' in lo else ''
    if any(x in lo for x in ['.png','data:image','@2x','favicon']): return True
    if any(x in domain for x in BAD): return True
    if any(x in domain for x in CHAIN): return True
    if any(x in local for x in BAD): return True
    if local in GENERIC:
        if any(p in domain for p in PUBLIC): return True
        if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch')): return False
        return True
    return False

def is_good(e):
    if not e or is_bad(e): return False
    lo = e.lower(); local = lo.split('@')[0]; domain = lo.split('@')[1] if '@' in lo else ''
    if '.' in local and len(local) >= 4: return True
    if '-' in local or '_' in local: return True
    if len(local) >= 3 and local[0].isupper(): return True
    if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch','.eu')) and len(domain.split('.')[0]) >= 3: return True
    return False

def clean_name(cn):
    if not cn: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|Kieferorthopädie\s*)','',cn,flags=re.I).strip()
    n = re.sub(r'[\.,]+$','',n)
    p = n.split()
    return (p[0] if p else '', p[-1] if len(p)>=2 else n)

def is_platform(url):
    if not url: return True
    lo = url.lower()
    return any(p in lo for p in ['golocal','stadtbranchenbuch','kennstdueinen','dastelefonbuch','dasoertliche','11880','jameda','docinsider'])

async def get_google_results(client, city, max_results=30):
    """Search Google for dentist impressum emails in a city."""
    query = f'site:.de Zahnarzt impressum email {city}'
    url = f'https://www.google.com/search?q={query}&num={max_results}'
    try:
        r = await client.get(url, headers=HDRS, timeout=httpx.Timeout(15.0, connect=8.0), follow_redirects=True)
        if r.status_code != 200: return []
        html = r.text
        # Extract result URLs
        urls = re.findall(r'href="(/url\?q=([^"&]+))"', html)
        websites = []
        for _, real_url in urls:
            real_url = real_url.strip()
            if real_url and 'google' not in real_url.lower():
                real_url = real_url.split('&')[0]
                import urllib.parse
                real_url = urllib.parse.unquote(real_url)
                if real_url.startswith('http') and not is_platform(real_url):
                    websites.append(real_url)
        return websites[:max_results]
    except Exception as e:
        return []

async def get_email(client, url):
    if not url or is_platform(url): return ''
    base = url.rstrip('/')
    paths = ['/impressum','/impressum/','/impress','/legal','/rechtliches','/kontakt']
    for path in paths:
        try:
            r = await client.get(base + path, headers=HDRS, timeout=httpx.Timeout(10.0, connect=5.0), follow_redirects=True)
            if r.status_code == 200 and len(r.text) > 300:
                emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                for e in emails:
                    if is_good(e): return e
        except: pass
    return ''

async def crawl_city(client, city):
    print(f'  Searching: {city}')
    websites = await get_google_results(client, city)
    print(f'  [{city}] Found {len(websites)} websites')
    emails_found = []
    for url in websites:
        em = await get_email(client, url)
        if em:
            fn, ln = clean_name(url)
            emails_found.append({'vorname': fn, 'nachname': ln, 'email': em, 'website': url})
            print(f'    EMAIL: {em} | {fn} {ln}')
        await asyncio.sleep(0.3)
    return emails_found

async def main():
    CITIES = [
        'Frankfurt am Main','Bremen','Essen','Bochum','Bielefeld','Bonn',
        'Münster','Mannheim','Karlsruhe','Augsburg','Wiesbaden','Mönchengladbach',
        'Gelsenkirchen','Braunschweig','Aachen','Kiel','Chemnitz','Halle',
        'Magdeburg','Freiburg','Krefeld','Mainz','Lübeck','Erfurt',
        'Dresden','Leipzig','Nürnberg','Stuttgart','Düsseldorf','Dortmund',
        'Berlin','Hamburg','Hannover','München','Köln'
    ]
    
    all_emails = []
    SEM = asyncio.Semaphore(5)  # 5 concurrent city searches
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0), limits=httpx.Limits(max_connections=10)) as client:
        for i in range(0, len(CITIES), 5):
            chunk = CITIES[i:i+5]
            print(f'\nBatch: {chunk}')
            tasks = [crawl_city(client, c) for c in chunk]
            results = await asyncio.gather(*tasks)
            for r in results:
                all_emails.extend(r)
            print(f'  Batch done. Running total: {len(all_emails)} emails')
    
    # Save
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
        w.writeheader()
        w.writerows(all_emails)
    print(f'\nFinal: {len(all_emails)} emails saved to {OUT_CSV}')

if __name__ == '__main__':
    asyncio.run(main())
