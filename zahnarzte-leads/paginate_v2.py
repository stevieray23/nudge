"""
Optimized paginating scraper: 1 agent = 6 cities, each city = 8 pages.
Sequential to avoid context conflicts. Checkpoints after every city.
"""
import asyncio, csv, re, json, time, sys
import httpx
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
CITIES_STR = sys.argv[1] if len(sys.argv) > 1 else 'Berlin,Hamburg,Hannover,Munchen,Koln'
CITIES = [c.strip().replace('Munchen','München').replace('Koln','Köln').replace('Muenchen','München').replace('Nuernberg','Nürnberg') for c in CITIES_STR.split(',')]
BATCH_ID = sys.argv[2] if len(sys.argv) > 2 else 'batchA'
OUT_JSON = BASE / f'paginate_{BATCH_ID}.json'
CHECKPOINT = BASE / f'paginate_{BATCH_ID}_checkpoint.json'

HDRS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36','Accept-Language':'de-DE,de;q=0.9'}
IMPRESSUM = ['/impressum','/impressum/','/impress','/legal','/rechtliches','/kontakt']
SEM = 80

GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz'}
PUBLIC = {'gmail.com','yahoo.com','hotmail.com','outlook.com','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com'}
BAD_EMAILS = {'sentry','usercentrics','cookiebot','kzvh','kzvr','zaek','aekwl','bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi','blzk','bezirksstelle','zahnarztboerse','dentale','google.com','facebook','instagram','linkedin','xing','twitter','bit.ly','domain.com','alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft','sentry.io','sentry-next.wixpress.com'}

def is_bad(e):
    if not e or '@' not in e: return True
    lo = e.lower(); local = lo.split('@')[0]; domain = lo.split('@')[1] if '@' in lo else ''
    if any(x in lo for x in ['.png','data:image','@2x','favicon','logo']): return True
    if any(x in domain for x in BAD_EMAILS): return True
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
    if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch','.eu')) and len(domain.split('.')[0]) >= 3:
        return True
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
    return any(p in lo for p in ['golocal','stadtbranchenbuch','kennstdueinen','dastelefonbuch','dasoertliche','11880','jameda','docinsider','gsservice'])

async def get_pages(city, page):
    """Fetch one listing page URL and return all gsbiz detail URLs."""
    if page == 1:
        url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
    else:
        url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}/seite-{page}'
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=8.0), follow_redirects=True, headers=HDRS) as client:
        try:
            r = await client.get(url)
            if r.status_code != 200: return []
            text = r.text
            # Extract gsbiz URLs
            import re
            matches = re.findall(r'href="(/gsbiz/[^"?#]+)', text)
            gs_urls = []
            for m in matches:
                gs_urls.append('https://www.gelbeseiten.de' + m)
            # Check if this page has content
            if 'zahnarzt' in text.lower() or 'Zahnarzt' in text:
                return list(set(gs_urls))
            return []
        except:
            return []

async def get_real_website(gs_url, ctx):
    try:
        pg = await ctx.new_page()
        await pg.goto(gs_url, wait_until='domcontentloaded', timeout=18000)
        await asyncio.sleep(1.5)
        h1 = await pg.query_selector('h1')
        name = (await h1.inner_text()).strip() if h1 else ''
        all_links = await pg.query_selector_all('a[href]')
        best = None
        for al in all_links:
            href = await al.get_attribute('href')
            txt = (await al.inner_text() or '').lower()
            if not href or not href.startswith('http'): continue
            if 'gelbeseiten' in href.lower(): continue
            if is_platform(href): continue
            if any(b in href.lower() for b in ['facebook','instagram','linkedin','bing','google','yahoo','apple']): continue
            if any(b in txt for b in ['website','homepage','zur web','onlineshop']):
                best = href.split('?')[0].split('#')[0]; break
            elif not best:
                best = href.split('?')[0].split('#')[0]
        await pg.close()
        return name, best
    except:
        return '', None

async def get_email(client, url):
    if not url or is_platform(url): return ''
    base = url.rstrip('/')
    for path in IMPRESSUM:
        try:
            r = await client.get(base + path, headers=HDRS, timeout=8.0, follow_redirects=True)
            if r.status_code == 200 and len(r.text) > 300:
                emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                for e in emails:
                    if is_good(e): return e
        except: pass
    return ''

async def process_city(browser, city):
    all_gs = set()
    # Try up to 8 pages via HTTP
    for page in range(1, 9):
        gs_urls = await get_pages(city, page)
        if not gs_urls: break
        all_gs.update(gs_urls)
        print(f'    [{city}] Page {page}: +{len(gs_urls)} = {len(all_gs)} total')
        await asyncio.sleep(0.5)
    
    if not all_gs:
        print(f'  [{city}] No listings found!')
        return 0, 0
    
    ctx = await browser.new_context(user_agent=HDRS['User-Agent'], locale='de-DE')
    new_emails = 0
    new_websites = 0
    
    for gs_url in all_gs:
        name, website = await get_real_website(gs_url, ctx)
        if website and not is_platform(website):
            new_websites += 1
            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), limits=httpx.Limits(max_connections=SEM)) as client:
                em = await get_email(client, website)
            if em:
                new_emails += 1
                print(f'      EMAIL: {em} | {name[:40]}')
        await asyncio.sleep(0.15)
    
    await ctx.close()
    return new_websites, new_emails

async def main():
    print(f'Cities: {CITIES}')
    
    # Load checkpoint
    done_cities = set()
    email_records = []
    if CHECKPOINT.exists():
        try:
            data = json.load(open(CHECKPOINT, 'r', encoding='utf-8'))
            done_cities = set(data.get('done_cities', []))
            email_records = data.get('email_records', [])
            print(f'Resuming: {len(done_cities)} done, {len(email_records)} emails')
        except: pass
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for i, city in enumerate(CITIES):
            if city in done_cities:
                print(f'[{i+1}/{len(CITIES)}] SKIP {city} (done)')
                continue
            print(f'\n[{i+1}/{len(CITIES)}] Processing: {city}')
            t0 = time.time()
            sites, emails = await process_city(browser, city)
            elapsed = time.time() - t0
            print(f'  [{city}] +{sites} sites, +{emails} emails in {elapsed:.0f}s. Total: {len(email_records)+emails} emails')
            done_cities.add(city)
            # Save checkpoint
            with open(CHECKPOINT, 'w', encoding='utf-8') as f:
                json.dump({'done_cities': list(done_cities), 'email_records': email_records}, f, ensure_ascii=False)
        await browser.close()
    
    # Save output
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(email_records, f, ensure_ascii=False)
    print(f'\nDone! {len(email_records)} emails saved to {OUT_JSON}')

if __name__ == '__main__':
    asyncio.run(main())
