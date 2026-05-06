"""
Pure web_fetch-based paginating scraper.
1. Fetch page 1 of a city -> extract all pagination page URLs + listing URLs
2. Fetch each pagination page URL -> extract more listings
3. Extract real clinic websites from detail pages
4. Crawl impressum for emails
"""
import asyncio, csv, re, json, time
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
HDRS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36','Accept-Language':'de-DE,de;q=0.9'}

# Import shared tools
import sys
sys.path.insert(0, str(BASE))
try:
    from web_fetch_tool import fetch_url
    print("Using web_fetch_tool")
except:
    import os
    print("web_fetch_tool not available, using httpx")

async def fetch_page_text(url):
    """Fetch page text using httpx (since web_fetch is a tool, not a Python API)."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(25.0, connect=10.0), follow_redirects=True, headers=HDRS) as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.text
    except:
        pass
    return ''

def extract_gsbiz_urls(html):
    """Extract all /gsbiz/ detail URLs from a page."""
    if not html: return []
    matches = re.findall(r'href="(/gsbiz/[^"?#]+)', html)
    urls = []
    for m in matches:
        urls.append('https://www.gelbeseiten.de' + m)
    return list(dict.fromkeys(urls))

def extract_pagination_urls(html, city):
    """Extract all pagination page URLs from the page."""
    if not html: return []
    # Pattern: href="/suche/zahnarzt/{city}?page=N"
    # or href="/suche/zahnarzt/{city}/seite-N"
    patterns = [
        r'href="(/suche/zahnarzt/[^"?#]+\?page=\d+)"',
        r'href="(/suche/zahnarzt/[^"?#]+/seite-\d+)"',
    ]
    urls = []
    for pat in patterns:
        matches = re.findall(pat, html)
        for m in matches:
            if not m.startswith('http'):
                m = 'https://www.gelbeseiten.de' + m
            urls.append(m)
    return list(dict.fromkeys(urls))

# Email filter
GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz'}
PUBLIC = {'gmail.com','yahoo.com','hotmail.com','outlook.com','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com'}
BAD_EMAILS = {'sentry','usercentrics','cookiebot','kzvh','kzvr','zaek','aekwl','bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi','blzk','bezirksstelle','zahnarztboerse','dentale','google.com','facebook','instagram','linkedin','xing','twitter','bit.ly','domain.com','alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft','sentry.io','sentry-next.wixpress.com'}
CHAIN = {'alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft'}

def is_bad(e):
    if not e or '@' not in e: return True
    lo = e.lower(); local = lo.split('@')[0]; domain = lo.split('@')[1] if '@' in lo else ''
    if any(x in lo for x in ['.png','data:image','@2x','favicon']): return True
    if any(x in domain for x in BAD_EMAILS): return True
    if any(x in domain for x in CHAIN): return True
    if any(x in local for x in BAD_EMAILS): return True
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

async def get_real_website_http(gs_url):
    """Extract real website from GS detail page via HTTP."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=8.0), follow_redirects=True, headers=HDRS) as client:
            r = await client.get(gs_url)
            if r.status_code != 200: return '', None
            html = r.text
            # Look for "Zur Website" links or external website links
            links = re.findall(r'href="(https?://(?!www\.gelbeseiten)[^"?#]+)"', html)
            best = None
            for href in links:
                if any(b in href.lower() for b in ['facebook','instagram','linkedin','bing','google','yahoo','apple','docinsider','jimdo','webnode','golocal','stadtbranchenbuch','kennstdueinen','dastelefonbuch','11880']): continue
                if any(b in href.lower() for b in ['website','homepage']):
                    best = href.split('?')[0].split('#')[0]; break
                elif not best:
                    best = href.split('?')[0].split('#')[0]
            # Also look for the website in a specific div
            name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
            name = name_match.group(1).strip() if name_match else ''
            return name, best
    except:
        return '', None

async def get_email_http(website_url):
    """Fast HTTP crawl of impressum."""
    if not website_url: return ''
    import httpx
    paths = ['/impressum','/impressum/','/impress','/legal','/rechtliches','/kontakt']
    base = website_url.rstrip('/')
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), follow_redirects=True, limits=httpx.Limits(max_connections=60), headers=HDRS) as client:
        for path in paths:
            try:
                r = await client.get(base + path)
                if r.status_code == 200 and len(r.text) > 300:
                    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                    for e in emails:
                        if is_good(e): return e
            except: pass
    return ''

async def scrape_city_semaphore(sem, city, gs_urls, seen_websites, all_emails):
    async with sem:
        new_websites = 0
        new_emails = 0
        for gs_url in gs_urls:
            name, website = await get_real_website_http(gs_url)
            if website and website not in seen_websites:
                seen_websites.add(website)
                new_websites += 1
                em = await get_email_http(website)
                if em:
                    fn, ln = clean_name(name)
                    all_emails.append({'vorname': fn, 'nachname': ln, 'email': em, 'website': website, 'city': city})
                    new_emails += 1
                    print(f'  EMAIL: {em} | {fn} {ln}')
            await asyncio.sleep(0.1)
        return new_websites, new_emails

async def process_city(city, max_pages=10):
    """Get all listings from all pages, then crawl all."""
    print(f'\n=== {city} ===')
    
    # Step 1: Fetch page 1 and extract pagination URLs
    page1_url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
    html1 = await fetch_page_text(page1_url)
    if not html1:
        print(f'  Failed to fetch page 1 for {city}')
        return 0, 0
    
    all_gs_urls = set(extract_gsbiz_urls(html1))
    pagination_urls = extract_pagination_urls(html1, city)
    
    # Fetch each pagination page
    for p_url in pagination_urls[:max_pages-1]:
        html = await fetch_page_text(p_url)
        if html:
            urls = extract_gsbiz_urls(html)
            all_gs_urls.update(urls)
            print(f'  Page {p_url}: +{len(urls)} listings = {len(all_gs_urls)} total')
        await asyncio.sleep(0.5)
    
    print(f'  Total listings: {len(all_gs_urls)}')
    
    # Step 2: Crawl all listings
    sem = asyncio.Semaphore(30)
    seen_websites = set()
    all_emails = []
    
    # Batch process
    gs_list = list(all_gs_urls)
    for batch_start in range(0, len(gs_list), 20):
        batch = gs_list[batch_start:batch_start+20]
        tasks = [scrape_city_semaphore(sem, city, batch, seen_websites, all_emails) for _ in [0]]
        # Actually process individually
        for gs_url in batch:
            if gs_url in seen_websites: continue
            name, website = await get_real_website_http(gs_url)
            if website and website not in seen_websites:
                seen_websites.add(website)
                em = await get_email_http(website)
                if em:
                    fn, ln = clean_name(name)
                    all_emails.append({'vorname': fn, 'nachname': ln, 'email': em, 'website': website, 'city': city})
                    print(f'  EMAIL: {em} | {fn} {ln}')
            if len(seen_websites) % 50 == 0:
                print(f'  ... {len(seen_websites)} websites processed, {len(all_emails)} emails')
            await asyncio.sleep(0.1)
        print(f'  Batch {batch_start//20+1}: {len(all_emails)} emails so far')
    
    return len(seen_websites), len(all_emails)

async def main():
    CITIES = [
        'Frankfurt am Main','Bremen','Essen','Bochum','Bielefeld','Bonn',
        'Münster','Mannheim','Karlsruhe','Augsburg','Wiesbaden','Mönchengladbach',
        'Gelsenkirchen','Braunschweig','Aachen','Kiel','Chemnitz','Halle (Saale)',
        'Magdeburg','Freiburg im Breisgau','Krefeld','Mainz','Lübeck','Erfurt',
        'Dresden','Leipzig','Nürnberg','Stuttgart','Düsseldorf','Dortmund',
        'Berlin','Hamburg','Hannover','München','Köln'
    ]
    
    total_emails = 0
    total_websites = 0
    
    for i, city in enumerate(CITIES):
        print(f'\n[{i+1}/{len(CITIES)}] {city}')
        t0 = time.time()
        sites, emails = await process_city(city, max_pages=8)
        elapsed = time.time() - t0
        total_websites += sites
        total_emails += emails
        print(f'  [{city}] {sites} websites, {emails} emails in {elapsed:.0f}s. Running total: {total_emails}')
        
        # Save checkpoint after each city
        with open(BASE / 'webfetch_checkpoint.json', 'w', encoding='utf-8') as f:
            json.dump({'total_emails': total_emails, 'total_websites': total_websites, 'last_city': city}, f)
    
    print(f'\nFinal: {total_websites} websites, {total_emails} emails')

if __name__ == '__main__':
    asyncio.run(main())
