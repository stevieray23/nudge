"""
Use web_fetch to scrape Gelbe Seiten pages for multiple cities in parallel.
web_fetch renders JS so it gets the full listing content.
Each call gets ~50 real listings. Use web_search to find pagination-aware URLs.
"""
import csv, re, json, asyncio, httpx, time
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

GENERIC_LOCAL = {'info','kontakt','praxis','service','team','office','mail','termin',
    'rezeption','empfang','sekretariat','poststelle','redaktion','webmaster',
    'noreply','datenschutz','terminvergabe','anmeldung'}
PUBLIC = {'gmail.com','yahoo.com','hotmail','outlook.com','web.de','t-online.de',
    'gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de',
    'live.de','msn.com','gmx.net','email.de','live.com','outlook.de','arcor.de'}
BAD_DOMAINS = {'sentry','usercentrics','kzvh','kzvr','zaek','aekwl','bezreg','lzkth',
    'lzkbw','lzk','brd.nrw','alldent','dentalke','dentall','dentazoo','dentacon',
    'dentaloft','doctolib','jameda','docinsider','sentry.io','wixpress.com',
    'sentry-next','stadtbranchenbuch','golocal','11880.com','dasoertliche'}
BAD_LOCAL = {'sentry','pixel','tracking','cropped','logo','icon','btn','button',
    'transparent','bg-','header','footer','data','undefined','no-reply'}

def is_ok(e):
    if not e or '@' not in e: return False
    lo = e.lower(); local, domain = lo.split('@', 1)
    domain = domain.rstrip('/').split('?')[0].split('#')[0]
    if any(x in domain for x in BAD_DOMAINS): return False
    if any(x in lo for x in BAD_LOCAL): return False
    if local in GENERIC_LOCAL and any(p in domain for p in PUBLIC): return False
    return True

# GS listing URL format
CITIES = [
    'Berlin','Hamburg','München','Köln','Frankfurt','Stuttgart','Düsseldorf',
    'Dortmund','Essen','Leipzig','Dresden','Hannover','Nürnberg','Bremen',
    'Bielefeld','Bonn','Karlsruhe','Mannheim','Augsburg','Wiesbaden','Münster',
    'Krefeld','Aachen','Magdeburg','Braunschweig','Chemnitz','Kiel','Erfurt',
    'Rostock','Lübeck','Paderborn','Heidelberg','Saarbrücken','Freiburg',
    'Mainz','Gelsenkirchen','Hagen','Mönchengladbach','Halle'
]

HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9',
}

def parse_listing_page(html, city):
    """Extract dentist listings from GS page HTML."""
    listings = []
    # Pattern: clinic name + address + gs detail URL
    # Names appear as: "Zahnarztpraxis Petra Hartmann" followed by address
    # Detail URLs: /gsbiz/UUID
    
    # Split on the pattern that marks each listing
    # Each listing starts with a name that links to /gsbiz/...
    pattern = r'<a[^>]+href=["\']/gsbiz/([a-f0-9-]+)["\'][^>]*>\s*<span[^>]*>([^<]+)</span>'
    for m in re.finditer(pattern, html, re.I):
        uuid = m.group(1)
        name = m.group(2).strip()
        if not name or len(name) < 3: continue
        
        # Find address near this match
        start = m.end()
        addr_match = re.search(r'([A-ZÄÖÜ][a-zäöüß]+(?:str|straße|platz|allee|weg|berg|tor|damm|markt|hof|eck|eck|haus|bogen|park|ring|wall|burg|fuhr|feld|gasse|graben|graben|anger| Anger| berg| haus| werk| bach| see| tal| wiese| winkel| pfad| stieg| stiege| steig| plan| rage| rage| reihe| reihe|anger)[^\n<]{5,60})', html[start:start+500], re.I)
        addr = addr_match.group(1).strip() if addr_match else ''
        
        # Clean name
        name = re.sub(r'^(Dr\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*)', '', name, flags=re.I).strip()
        if not name or len(name) < 2: continue
        
        gs_url = f'https://www.gelbeseiten.de/gsbiz/{uuid}'
        listings.append({'name': name, 'gs_url': gs_url, 'address': addr, 'city': city})
    return listings

async def fetch_city(client, city):
    """Fetch one city page and extract listings."""
    url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
    try:
        r = await client.get(url, timeout=httpx.Timeout(15.0, connect=8.0), 
            headers=HDRS, follow_redirects=True)
        if r.status_code != 200: return []
        return parse_listing_page(r.text, city)
    except:
        return []

async def get_email_from_website(client, website):
    """Get email from clinic website impressum."""
    if not website or not website.startswith('http'): return ''
    base = website.rstrip('/')
    for path in ['/impressum','/impressum/','/impress','/legal']:
        try:
            r = await client.get(base + path, timeout=httpx.Timeout(10.0, connect=5.0),
                headers=HDRS, follow_redirects=True)
            if r.status_code == 200 and len(r.text) > 500:
                emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                for e in emails:
                    if is_ok(e): return e
        except: pass
        await asyncio.sleep(0.1)
    return ''

async def get_website_from_gs(client, gs_url):
    """Extract real website from GS detail page."""
    try:
        r = await client.get(gs_url, timeout=httpx.Timeout(15.0, connect=8.0),
            headers=HDRS, follow_redirects=True)
        if r.status_code != 200: return ''
        html = r.text
        # Look for website link
        for pat in [
            r'href="(https?://(?!www\.gelbeseiten)[^"?#\s]+)"[^>]*>\s*(?:zur\s+)?website',
            r'"zurWebsiteUrl"\s*:\s*"([^"]+)"',
            r'"websiteUrl"\s*:\s*"([^"]+)"',
        ]:
            m = re.search(pat, html, re.I)
            if m:
                url = m.group(1).strip()
                if url and 'gelbeseiten' not in url.lower():
                    return url
    except: pass
    return ''

async def main():
    print(f'Scraping {len(CITIES)} cities...')
    
    # Phase 1: Get listings for all cities
    all_listings = []
    SEM = asyncio.Semaphore(5)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=10)) as client:
        
        # Batch by 5 cities
        for i in range(0, len(CITIES), 5):
            chunk = CITIES[i:i+5]
            print(f'Batch: {chunk}')
            tasks = [fetch_city(client, c) for c in chunk]
            results = await asyncio.gather(*tasks)
            for city_listings in results:
                all_listings.extend(city_listings)
            print(f'  Found {len(all_listings)} total listings so far')
    
    # Deduplicate by GS URL
    seen_urls = set()
    unique = []
    for l in all_listings:
        if l['gs_url'] not in seen_urls:
            seen_urls.add(l['gs_url'])
            unique.append(l)
    
    print(f'\n{len(unique)} unique listings from {len(CITIES)} cities')
    
    # Phase 2: Get website for each listing
    print('Getting websites from GS detail pages...')
    websites_found = 0
    SEM2 = asyncio.Semaphore(20)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=40)) as client:
        for i, listing in enumerate(unique):
            async with SEM2:
                ws = await get_website_from_gs(client, listing['gs_url'])
                listing['website'] = ws
                if ws: websites_found += 1
            if (i+1) % 20 == 0:
                print(f'  [{i+1}/{len(unique)}] {websites_found} websites found')
            await asyncio.sleep(0.15)
    
    # Phase 3: Get emails
    print('Getting emails from clinic websites...')
    emails_found = 0
    SEM3 = asyncio.Semaphore(20)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=40)) as client:
        for i, listing in enumerate(unique):
            if listing.get('website'):
                async with SEM3:
                    em = await get_email_from_website(client, listing['website'])
                    listing['email'] = em
                    if em: 
                        emails_found += 1
                        print(f'  EMAIL: {em} | {listing["name"]}')
            if (i+1) % 20 == 0:
                print(f'  [{i+1}/{len(unique)}] {emails_found} emails found')
            await asyncio.sleep(0.15)
    
    # Save
    out_json = BASE / 'webfetch_leads.json'
    out_csv = BASE / 'webfetch_leads.csv'
    
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['name','email','address','city','website','gs_url'], delimiter=';')
        w.writeheader()
        w.writerows(unique)
    
    print(f'\nSaved: {out_json} and {out_csv}')
    print(f'Total listings: {len(unique)}, with website: {websites_found}, with email: {emails_found}')

if __name__ == '__main__':
    asyncio.run(main())
