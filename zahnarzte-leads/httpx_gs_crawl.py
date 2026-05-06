"""
Complete parallel GS scraper using httpx.
1. Fetch listing pages for 35 cities (50 listings each = ~1750 leads)
2. Extract real clinic websites from GS detail pages
3. Crawl Impressum for emails
"""
import csv, re, json, asyncio, httpx
from pathlib import Path
from collections import OrderedDict

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9',
    'Referer': 'https://www.gelbeseiten.de/',
}

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

CITIES = [
    'Berlin','Hamburg','Muenchen','Koeln','Frankfurt','Stuttgart','Duesseldorf',
    'Dortmund','Essen','Leipzig','Dresden','Hannover','Nuernberg','Bremen',
    'Bielefeld','Bonn','Karlsruhe','Mannheim','Augsburg','Wiesbaden','Muenster',
    'Krefeld','Aachen','Magdeburg','Braunschweig','Chemnitz','Kiel','Erfurt',
    'Rostock','Luebeck','Paderborn','Heidelberg','Saarbruecken','Freiburg',
    'Mainz','Gelsenkirchen','Hagen','Moenchengladbach','Halle'
]

def parse_gs_page(html, city):
    """Extract listings from GS HTML. Returns list of (name, gs_detail_url)."""
    listings = []
    # Pattern: find all gsbiz UUID links + the name element near them
    # UUID pattern: /gsbiz/HEX-UUID
    uuid_pattern = r'/gsbiz/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    # Name pattern: appears as text inside/near the link
    # Strategy: find all UUID occurrences and extract surrounding text
    
    for m in re.finditer(uuid_pattern, html, re.I):
        uuid = m.group(1)
        pos = m.start()
        # Get surrounding context (500 chars before, 200 after)
        context_before = html[max(0, pos-500):pos]
        context_after = html[pos:pos+300]
        context = context_before + context_after
        
        # Extract the clinic name from the context
        # Usually the name appears as an aria-label or title attribute
        name_m = re.search(r'aria-label=["\']([^"\']+)["\']', context, re.I)
        if not name_m:
            name_m = re.search(r'data-testid="[^"]*name[^"]*"[^>]*>([^<]+)<', context, re.I)
        if not name_m:
            name_m = re.search(r'class="[^"]*entry[^"]*name[^"]*"[^>]*>\s*<[^>]*>\s*([^<\n]+)', context, re.I)
        if not name_m:
            # Try to find text between > and < that's 3+ chars before the link
            name_m = re.search(r'>\s*([A-ZÄÖÜ][a-zäöüß\-\s\.]{3,40})\s*</a>', context_before[-200:], re.I)
        
        name = name_m.group(1).strip() if name_m else ''
        name = re.sub(r'<[^>]+>', '', name).strip()
        name = re.sub(r'^(Dr\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|'
                     r'Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|'
                     r'Kieferorthopädie\s*)', '', name, flags=re.I).strip()
        
        if name and len(name) >= 3:
            gs_url = f'https://www.gelbeseiten.de/gsbiz/{uuid}'
            listings.append({'name': name, 'gs_url': gs_url, 'city': city})
    
    return listings

async def fetch_listings(client, city, sem):
    """Fetch one city page and parse listings."""
    async with sem:
        url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
        try:
            r = await client.get(url, timeout=httpx.Timeout(15.0, connect=8.0), 
                headers=HDRS, follow_redirects=True)
            if r.status_code != 200: return []
            return parse_gs_page(r.text, city)
        except Exception as ex:
            print(f'  ERROR {city}: {ex}')
            return []

async def get_website(client, gs_url, sem):
    """Extract real website from GS detail page."""
    async with sem:
        try:
            r = await client.get(gs_url, timeout=httpx.Timeout(15.0, connect=8.0),
                headers=HDRS, follow_redirects=True)
            if r.status_code != 200: return ''
            html = r.text
            # Look for website links
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
            # Fallback: find any external http link that's not gelbeseiten
            links = re.findall(r'href="(https?://(?!www\.gelbeseiten)[^"?#\s]+)"', html)
            for link in links:
                if link and not any(x in link for x in ['facebook','instagram','linkedin','youtube']):
                    return link
        except: pass
        return ''

async def get_email(client, website, sem):
    """Get email from clinic website impressum."""
    async with sem:
        if not website: return ''
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

async def main():
    # Phase 1: Fetch all city pages
    print(f'Phase 1: Fetching listings for {len(CITIES)} cities...')
    all_listings = []
    SEM1 = asyncio.Semaphore(8)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=16)) as client:
        for i in range(0, len(CITIES), 8):
            chunk = CITIES[i:i+8]
            print(f'  Batch: {chunk}')
            tasks = [fetch_listings(client, c, SEM1) for c in chunk]
            results = await asyncio.gather(*tasks)
            for city_listings in results:
                all_listings.extend(city_listings)
            print(f'  Total listings so far: {len(all_listings)}')
    
    # Deduplicate
    seen_urls = set()
    unique = []
    for l in all_listings:
        if l['gs_url'] not in seen_urls:
            seen_urls.add(l['gs_url'])
            unique.append(l)
    
    print(f'\n{len(unique)} unique listings from {len(CITIES)} cities')
    
    # Phase 2: Get websites (parallel, 30 at a time)
    print(f'\nPhase 2: Getting websites from GS detail pages...')
    SEM2 = asyncio.Semaphore(30)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=60)) as client:
        for i in range(0, len(unique), 50):
            batch = unique[i:i+50]
            tasks = [get_website(client, l['gs_url'], SEM2) for l in batch]
            websites = await asyncio.gather(*tasks)
            for j, ws in enumerate(websites):
                unique[i+j]['website'] = ws or ''
            done = min(i+50, len(unique))
            ws_count = sum(1 for l in unique[:done] if l.get('website'))
            print(f'  [{done}/{len(unique)}] {ws_count} websites found')
            await asyncio.sleep(0.5)  # Brief pause between batches
    
    ws_total = sum(1 for l in unique if l.get('website'))
    print(f'  Got websites for {ws_total}/{len(unique)} listings')
    
    # Phase 3: Get emails (parallel, 30 at a time)
    print(f'\nPhase 3: Getting emails from clinic websites...')
    SEM3 = asyncio.Semaphore(30)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=60)) as client:
        for i in range(0, len(unique), 50):
            batch = unique[i:i+50]
            tasks = [get_email(client, l.get('website',''), SEM3) for l in batch]
            emails = await asyncio.gather(*tasks)
            for j, em in enumerate(emails):
                if em:
                    unique[i+j]['email'] = em
                    print(f'  EMAIL: {em} | {unique[i+j]["name"]}')
            done = min(i+50, len(unique))
            em_count = sum(1 for l in unique[:done] if l.get('email'))
            print(f'  [{done}/{len(unique)}] {em_count} emails found')
            await asyncio.sleep(0.5)
    
    em_total = sum(1 for l in unique if l.get('email'))
    print(f'  Got emails for {em_total} listings')
    
    # Save
    out_json = BASE / 'httpx_leads.json'
    out_csv = BASE / 'httpx_leads.csv'
    
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['name','email','city','website','gs_url'], delimiter=';')
        w.writeheader()
        w.writerows(unique)
    
    print(f'\nSaved: {out_json} and {out_csv}')
    print(f'Final: {len(unique)} listings | {ws_total} websites | {em_total} emails')

if __name__ == '__main__':
    asyncio.run(main())
