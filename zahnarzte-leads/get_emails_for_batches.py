"""
Phase 2: Get real clinic websites from GS detail pages for the 846 listings.
Then crawl Impressum for emails.
"""
import csv, re, json, asyncio, httpx
from pathlib import Path

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
    'live.de','msn.com','gmx.net','email.de','live.com','outlook.de','arcor.de',
    'yahoo.de','hotmail.com','outlook.de','gmx.ch','gmx.at'}
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

def parse_name(name):
    name = re.sub(r'^(Dr\.?\s*|Prof\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|'
                  r'Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|'
                  r'Oralchirurgie\s*|Kieferorthopädie\s*|Frau\s*|Herrn?\s*)', '', name, flags=re.I).strip()
    name = re.sub(r'^[\-\s]+|[\-\s]+$', '', name).strip()
    parts = name.split()
    if not parts: return '', ''
    vn = parts[0]
    ln = parts[-1] if len(parts) > 1 else ''
    BAD = {'und','und ','von','van','der','die','das','kollegen','partner','zahnärzte','zahnarzt'}
    if vn.lower() in BAD: vn = parts[1] if len(parts) > 1 else ''
    if ln.lower() in BAD: ln = parts[-2] if len(parts) > 1 else ''
    return vn, ln

def extract_website(html):
    for pat in [
        r'href="(https?://(?!www\.gelbeseiten\.de|plus\.google|facebook|instagram|linkedin|twitter|bing)[^"?#\s]+)"[^>]*>\s*(?:zur\s+)?website',
        r'"zurWebsiteUrl"\s*:\s*"([^"]+)"',
        r'"websiteUrl"\s*:\s*"([^"]+)"',
    ]:
        m = re.search(pat, html, re.I)
        if m:
            url = m.group(1).strip()
            if url and 'gelbeseiten' not in url.lower() and url.startswith('http'):
                return url
    # Fallback: any external http link that looks like a website
    links = re.findall(r'href="(https?://(?!www\.gelbeseiten|google|facebook|instagram|linkedin|twitter)[^"?#\s]+)"', html, re.I)
    for link in links:
        if any(x in link.lower() for x in ['.de','.com','.at','.ch','.eu']):
            return link
    return ''

async def get_website(client, gs_url, sem):
    async with sem:
        try:
            r = await client.get(gs_url, timeout=httpx.Timeout(12.0, connect=6.0),
                headers=HDRS, follow_redirects=True)
            if r.status_code != 200: return ''
            return extract_website(r.text)
        except: return ''

async def get_email(client, url, sem):
    async with sem:
        if not url: return ''
        base = url.rstrip('/')
        for path in ['/impressum','/impressum/','/impress','/legal']:
            try:
                r = await client.get(base + path, timeout=httpx.Timeout(10.0, connect=5.0),
                    headers=HDRS, follow_redirects=True)
                if r.status_code == 200 and len(r.text) > 500:
                    for e in re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text):
                        if is_ok(e): return e
            except: pass
            await asyncio.sleep(0.1)
        return ''

async def main():
    # Load listings from all 3 batch files
    all_listings = []
    for fname in ['gs_batch_a.json','gs_batch_b.json','gs_batch_c.json']:
        p = BASE / fname
        if not p.exists(): continue
        d = json.load(open(p, encoding='utf-8'))
        if isinstance(d, list):
            for city_data in d:
                city = city_data.get('city','')
                for l in city_data.get('listings', []):
                    l['city'] = city
                    all_listings.append(l)
        elif isinstance(d, dict):
            for city, val in d.items():
                listings = val.get('listings', []) if isinstance(val, dict) else (val if isinstance(val, list) else [])
                for l in listings:
                    l['city'] = city
                    all_listings.append(l)

    # Deduplicate
    seen = set()
    unique = []
    for l in all_listings:
        key = l.get('name','').lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(l)

    print(f'Loaded {len(unique)} unique listings')
    
    # Build GS detail URL from name (we don't have UUIDs, need to construct from name)
    # Actually, we need the GS detail page URLs. Let's construct search URLs.
    # The sub-agents used web_fetch which gave us the names but not URLs.
    # We need to get the UUIDs. Let's fetch the GS listing page to get UUIDs.
    
    # Better approach: fetch GS listing page and get UUIDs + names together
    print('\nFetching GS pages to get detail UUIDs...')
    
    # Get unique cities
    cities = list(dict.fromkeys(l.get('city','') for l in unique))
    print(f'Cities: {cities}')
    
    # City name mapping
    city_map = {'München':'muenchen','Düsseldorf':'duesseldorf','Nürnberg':'nuernberg',
                'Münster':'muenster','Lübeck':'luebeck','Gelsenkirchen':'gelsenkirchen',
                'Mönchengladbach':'moenchengladbach','Saarbrücken':'saarbruecken',
                'Köln':'koeln'}
    
    # Fetch listing pages to get UUID->name mapping
    gs_map = {}  # gs_url -> listing info
    SEM1 = asyncio.Semaphore(8)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=16)) as client:
        for i in range(0, len(cities), 8):
            chunk = cities[i:i+8]
            print(f'  Fetching: {chunk}')
            tasks = []
            for city in chunk:
                url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city_map.get(city,city.lower())}'
                async def fetch(client, url, city):
                    async with SEM1:
                        r = await client.get(url, timeout=httpx.Timeout(15.0, connect=8.0), 
                            headers=HDRS, follow_redirects=True)
                        if r.status_code == 200:
                            return city, r.text
                        return city, ''
                tasks.append(fetch(client, url, city))
            results = await asyncio.gather(*tasks)
            for city, html in results:
                if not html: continue
                # Get UUIDs from data-detailseiteUrl
                uuids = re.findall(r'data-detailseiteUrl="https://www\.gelbeseiten\.de/gsbiz/([0-9a-f-]+)"', html, re.I)
                for uuid in uuids:
                    gs_url = f'https://www.gelbeseiten.de/gsbiz/{uuid}'
                    gs_map[uuid] = {'gs_url': gs_url, 'city': city}
            print(f'  Got {len(gs_map)} GS detail URLs for {len(chunk)} cities')
    
    print(f'\nTotal GS detail URLs: {len(gs_map)}')
    
    # Phase 2: Get websites from detail pages (parallel)
    print('\nPhase 2: Getting websites from GS detail pages...')
    SEM2 = asyncio.Semaphore(40)
    
    gs_list = list(gs_map.values())
    websites = {}
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=80)) as client:
        for i in range(0, len(gs_list), 60):
            batch = gs_list[i:i+60]
            tasks = [get_website(client, l['gs_url'], SEM2) for l in batch]
            results = await asyncio.gather(*tasks)
            for j, ws in enumerate(results):
                if ws:
                    gs_id = batch[j]['gs_url']
                    websites[gs_id] = ws
            done = min(i+60, len(gs_list))
            print(f'  [{done}/{len(gs_list)}] {len(websites)} websites found')
            await asyncio.sleep(0.5)
    
    print(f'Got websites for {len(websites)}/{len(gs_list)} listings')
    
    # Phase 3: Get emails from websites (parallel)
    print('\nPhase 3: Getting emails from clinic websites...')
    SEM3 = asyncio.Semaphore(40)
    ws_list = list(websites.items())
    
    emails_found = []
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=80)) as client:
        for i in range(0, len(ws_list), 60):
            batch = ws_list[i:i+60]
            tasks = [get_email(client, ws, SEM3) for _, ws in batch]
            results = await asyncio.gather(*tasks)
            for j, em in enumerate(results):
                gs_id, ws = batch[j]
                if em:
                    emails_found.append({'email': em, 'website': ws, 'gs_url': gs_id})
                    print(f'  EMAIL: {em}')
            done = min(i+60, len(ws_list))
            print(f'  [{done}/{len(ws_list)}] {len(emails_found)} emails found')
            await asyncio.sleep(0.5)
    
    print(f'\nTotal emails found: {len(emails_found)}')
    
    # Save
    out_json = BASE / 'batch_emails.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(emails_found, f, ensure_ascii=False, indent=2)
    print(f'Saved: {out_json}')

if __name__ == '__main__':
    asyncio.run(main())
