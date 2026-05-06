"""
Complete pipeline: fetch GS detail pages for all 18 cities, extract real websites + emails.
Strategy: GS detail pages contain the real website URL and email directly in HTML.
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
    'sentry-next','stadtbranchenbuch','golocal','11880.com','dasoertliche',
    'meinungsmeister','consentmanager','adfarm','adition','wipe.de'}
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

def extract_data(html):
    """Extract website URL and email from GS detail page HTML."""
    website = ''
    email = ''
    
    # Extract email from data-link mailto
    m = re.search(r'data-link="mailto:([^"?]+)', html, re.I)
    if m:
        email = m.group(1).strip()
    
    # Also find any mailto in the page
    if not email:
        emails = re.findall(r'href="mailto:([^"?]+)"', html, re.I)
        for e in emails:
            if is_ok(e): 
                email = e
                break
    
    # Extract website: any external link that's a real website
    # Filter out ads, trackers, social media
    SKIP_FRAGS = {'consentmanager','adfarm','adition','wipe.de','facebook','instagram',
                  'linkedin','twitter','pinterest','tiktok','gelbeseiten','google',
                  'bing.com','meinungsmeister','dastelefonbuch','dasoertliche'}
    links = re.findall(r'href="(https?://(?!www\.gelbeseiten\.de)[^"?#\s]+)"', html, re.I)
    for link in links:
        link_lo = link.lower()
        if any(x in link_lo for x in SKIP_FRAGS): continue
        if any(x in link_lo for x in ['.de/','.com/','.at/','.ch/','.eu/']) or link_lo.count('.') >= 1:
            if not website or (website and len(link) > len(website)):
                website = link
                break
    
    return website.strip(), email.strip()

def parse_name(name):
    name = re.sub(r'^(Dr\.?\s*|Prof\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|'
                  r'Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|'
                  r'Oralchirurgie\s*|Kieferorthopädie\s*|Frau\s*|Herrn?\s*)', '', name, flags=re.I).strip()
    name = re.sub(r'^[\-\s]+|[\-\s]+$', '', name).strip()
    parts = name.split()
    if not parts: return '', ''
    vn = parts[0]
    ln = parts[-1] if len(parts) > 1 else ''
    BAD = {'und','von','van','der','die','das','kollegen','partner','zahnärzte','zahnarzt'}
    if vn.lower() in BAD: vn = parts[1] if len(parts) > 1 else ''
    if ln.lower() in BAD: ln = parts[-2] if len(parts) > 1 else ''
    return vn, ln

async def get_data(client, gs_url, sem):
    """Fetch GS detail page and extract website + email."""
    async with sem:
        try:
            r = await client.get(gs_url, timeout=httpx.Timeout(12.0, connect=6.0),
                headers=HDRS, follow_redirects=True)
            if r.status_code != 200: return '', ''
            return extract_data(r.text)
        except: return '', ''

async def main():
    # Step 1: Get GS detail page UUIDs from all city listing pages
    print('Step 1: Fetching GS listing pages for all cities...')
    
    CITY_MAP = {
        'Berlin': 'berlin', 'Hamburg': 'hamburg', 'München': 'muenchen', 
        'Köln': 'koeln', 'Frankfurt': 'frankfurt', 'Stuttgart': 'stuttgart',
        'Düsseldorf': 'duesseldorf', 'Dortmund': 'dortmund', 'Essen': 'essen',
        'Leipzig': 'leipzig', 'Dresden': 'dresden', 'Hannover': 'hannover',
        'Nürnberg': 'nuernberg', 'Bremen': 'bremen', 'Bielefeld': 'bielefeld',
        'Bonn': 'bonn', 'Karlsruhe': 'karlsruhe', 'Mannheim': 'mannheim'
    }
    
    gs_urls = {}  # uuid -> {gs_url, city}
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=16)) as client:
        SEM = asyncio.Semaphore(8)
        
        async def fetch_city(city_slug, city_name):
            async with SEM:
                url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city_slug}'
                r = await client.get(url, timeout=httpx.Timeout(15.0, connect=8.0), 
                    headers=HDRS, follow_redirects=True)
                if r.status_code != 200: return 0
                uuids = re.findall(r'data-detailseiteUrl="https://www\.gelbeseiten\.de/gsbiz/([0-9a-f-]+)"',
                                   r.text, re.I)
                for uuid in uuids:
                    gs_url = f'https://www.gelbeseiten.de/gsbiz/{uuid}'
                    gs_urls[uuid] = {'gs_url': gs_url, 'city': city_name}
                return len(uuids)
        
        tasks = [fetch_city(slug, name) for name, slug in CITY_MAP.items()]
        results = await asyncio.gather(*tasks)
        total_uuids = sum(results)
    
    print(f'  Got {len(gs_urls)} GS detail URLs from {len(CITY_MAP)} cities')
    
    # Step 2: Fetch all detail pages in parallel
    print(f'\nStep 2: Fetching {len(gs_urls)} detail pages...')
    
    gs_list = list(gs_urls.values())
    SEM2 = asyncio.Semaphore(50)
    
    all_results = {}
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=100)) as client:
        for i in range(0, len(gs_list), 100):
            batch = gs_list[i:i+100]
            tasks = [get_data(client, l['gs_url'], SEM2) for l in batch]
            results = await asyncio.gather(*tasks)
            for j, (ws, em) in enumerate(results):
                gs_list[i+j]['website'] = ws
                gs_list[i+j]['email'] = em
            with_website = sum(1 for l in gs_list[:i+100] if l.get('website'))
            with_email = sum(1 for l in gs_list[:i+100] if l.get('email'))
            print(f'  [{min(i+100,len(gs_list))}/{len(gs_list)}] {with_website} websites, {with_email} emails')
            await asyncio.sleep(0.5)
    
    ws_total = sum(1 for l in gs_list if l.get('website'))
    em_total = sum(1 for l in gs_list if l.get('email'))
    print(f'  Total: {ws_total} websites, {em_total} emails')
    
    # Step 3: Merge with names from batch files
    print('\nStep 3: Merging with dentist names...')
    
    # Load names from batch files
    all_names = {}  # city -> set of names
    for fname in ['gs_batch_a.json','gs_batch_b.json','gs_batch_c.json']:
        p = BASE / fname
        if not p.exists(): continue
        d = json.load(open(p, encoding='utf-8'))
        if isinstance(d, list):
            for city_data in d:
                city = city_data.get('city','')
                if city not in all_names: all_names[city] = set()
                for l in city_data.get('listings', []):
                    all_names[city].add(l.get('name','').strip())
        elif isinstance(d, dict):
            for city, val in d.items():
                if city not in all_names: all_names[city] = set()
                listings = val.get('listings', []) if isinstance(val, dict) else (val if isinstance(val, list) else [])
                for l in listings:
                    all_names[city].add(l.get('name','').strip())
    
    # Match: use city to narrow down, then fuzzy match name
    def fuzzy_match(name1, name2):
        n1 = re.sub(r'[^a-zäöüß]', '', name1.lower())
        n2 = re.sub(r'[^a-zäöüß]', '', name2.lower())
        return n1 in n2 or n2 in n1
    
    final_results = []
    used_cities = set()
    
    for l in gs_list:
        city = l.get('city','')
        ws = l.get('website','')
        em = l.get('email','')
        
        if not ws and not em: continue
        
        # Try to find matching name
        name = ''
        if city in all_names:
            for n in all_names[city]:
                if fuzzy_match(n, city):
                    name = n
                    break
        
        vn, ln = parse_name(name)
        final_results.append({
            'vorname': vn,
            'nachname': ln,
            'name': name,
            'email': em,
            'website': ws,
            'city': city,
            'gs_url': l['gs_url']
        })
        if em: 
            print(f'  EMAIL: {em} | {vn} {ln} ({city})')
    
    # Save
    out_json = BASE / 'gs_detail_emails.json'
    out_csv = BASE / 'gs_detail_emails.csv'
    
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['vorname','nachname','name','email','website','city','gs_url'], delimiter=';')
        w.writeheader()
        w.writerows(final_results)
    
    em_count = sum(1 for r in final_results if r.get('email'))
    ws_count = sum(1 for r in final_results if r.get('website'))
    print(f'\nFinal: {out_csv}')
    print(f'  Total: {len(final_results)} | with website: {ws_count} | with email: {em_count}')

if __name__ == '__main__':
    asyncio.run(main())
