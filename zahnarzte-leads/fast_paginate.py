"""
Fast Gelbe Seiten paginator with domcontentloaded (not networkidle).
- Loads page quickly, extracts all listing links
- Clicks next page buttons to paginate through 8 pages per city
- Extracts real websites from detail pages
- Crawls impressum for emails
"""
import asyncio, csv, re, json, time
import httpx
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
OUT_JSON = BASE / 'paginate_final.json'
HDRS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36','Accept-Language':'de-DE,de;q=0.9'}

# Email filter
GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz'}
PUBLIC = {'gmail.com','yahoo.com','hotmail','outlook.com','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com'}
BAD = {'sentry','usercentrics','cookiebot','kzvh','kzvr','zaek','aekwl','bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi','blzk','bezirksstelle','zahnarztboerse','dentale','google.com','facebook','instagram','linkedin','xing','twitter','bit.ly','domain.com','alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft','sentry.io','sentry-next'}
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
    return any(p in lo for p in ['golocal','stadtbranchenbuch','kennstdueinen','dastelefonbuch','dasoertliche','11880','jameda','docinsider','gsservice'])

async def get_real_website(gs_url, ctx):
    try:
        pg = await ctx.new_page()
        # domcontentloaded is MUCH faster than networkidle
        await pg.goto(gs_url, wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(1.5)
        h1 = await pg.query_selector('h1')
        name = (await h1.inner_text()).strip() if h1 else ''
        links = await pg.query_selector_all('a[href]')
        best = None
        for a in links:
            href = await a.get_attribute('href')
            txt = (await a.inner_text() or '').lower()
            if not href or not href.startswith('http'): continue
            if 'gelbeseiten' in href.lower(): continue
            if is_platform(href): continue
            if any(b in href.lower() for b in ['facebook','instagram','linkedin','bing','google','yahoo','apple','docinsider','jimdo','webnode']): continue
            if any(b in txt for b in ['website','homepage','zur web','onlineshop']):
                best = href.split('?')[0].split('#')[0]; break
            elif not best:
                best = href.split('?')[0].split('#')[0]
        await pg.close()
        return name, best
    except: return '', None

async def get_email(client, url):
    if not url or is_platform(url): return ''
    base = url.rstrip('/')
    paths = ['/impressum','/impressum/','/impress','/legal','/rechtliches','/kontakt']
    for path in paths:
        try:
            r = await client.get(base + path, headers=HDRS, timeout=8.0, follow_redirects=True)
            if r.status_code == 200 and len(r.text) > 300:
                emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                for e in emails:
                    if is_good(e): return e
        except: pass
    return ''

async def scrape_city(browser, city, max_pages=8):
    ctx = await browser.new_context(user_agent=HDRS['User-Agent'], locale='de-DE')
    pg = await ctx.new_page()
    all_gs = set()
    email_records = []
    seen_websites = set()
    
    try:
        await pg.goto(f'https://www.gelbeseiten.de/suche/zahnarzt/{city}', wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(2)
        
        for page_num in range(1, max_pages + 1):
            # Extract listing URLs from current page
            links = await pg.query_selector_all('a[href*="/gsbiz/"]')
            found = 0
            for a in links:
                href = await a.get_attribute('href')
                if href and '/gsbiz/' in (href or ''):
                    full = ('https://www.gelbeseiten.de' + href) if not href.startswith('http') else href
                    all_gs.add(full)
                    found += 1
            print(f'  [{city}] Page {page_num}: {found} listings (total: {len(all_gs)})')
            
            if page_num == max_pages: break
            
            # Try to go to next page
            next_clicked = False
            try:
                # Method 1: Look for page number links
                page_links = await pg.query_selector_all('a[href]')
                for pl in page_links:
                    href = await pl.get_attribute('href')
                    txt = await pl.inner_text()
                    if href and str(page_num + 1) in (txt or '') and ('seite' in (href or '') or 'page' in (href or '')):
                        if not href.startswith('http'):
                            href = 'https://www.gelbeseiten.de' + href
                        await pg.goto(href, wait_until='domcontentloaded', timeout=15000)
                        await asyncio.sleep(2)
                        next_clicked = True
                        break
            except: pass
            
            if not next_clicked:
                try:
                    # Method 2: Use URL pattern
                    next_url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}/seite-{page_num + 1}'
                    await pg.goto(next_url, wait_until='domcontentloaded', timeout=15000)
                    await asyncio.sleep(2)
                except: break
    except Exception as e:
        print(f'  [{city}] Error: {e}')
    finally:
        await ctx.close()
    
    # Crawl all listings
    print(f'  [{city}] Crawling {len(all_gs)} listings for websites and emails...')
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), limits=httpx.Limits(max_connections=60)) as client:
        for gs_url in all_gs:
            name, website = await get_real_website(gs_url, ctx)
            if website and not is_platform(website) and website not in seen_websites:
                seen_websites.add(website)
                em = await get_email(client, website)
                if em:
                    fn, ln = clean_name(name)
                    email_records.append({'vorname': fn, 'nachname': ln, 'email': em, 'website': website, 'city': city})
                    print(f'    EMAIL: {em} | {fn} {ln}')
            await asyncio.sleep(0.1)
    
    return email_records

async def main():
    CITIES = [
        'Frankfurt am Main','Bremen','Essen','Bochum','Bielefeld','Bonn',
        'Münster','Mannheim','Karlsruhe','Augsburg','Wiesbaden','Mönchengladbach',
        'Gelsenkirchen','Braunschweig','Aachen','Kiel','Chemnitz','Halle (Saale)',
        'Magdeburg','Freiburg im Breisgau','Krefeld','Mainz','Lübeck','Erfurt',
        'Dresden','Leipzig','Nürnberg','Stuttgart','Düsseldorf','Dortmund',
        'Berlin','Hamburg','Hannover','München','Köln'
    ]
    
    all_email_records = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for i, city in enumerate(CITIES):
            print(f'\n[{i+1}/{len(CITIES)}] {city}')
            t0 = time.time()
            records = await scrape_city(browser, city, max_pages=8)
            elapsed = time.time() - t0
            all_email_records.extend(records)
            print(f'  [{city}] +{len(records)} emails in {elapsed:.0f}s. Running total: {len(all_email_records)}')
            
            # Save checkpoint
            with open(BASE / 'paginate_checkpoint.json', 'w', encoding='utf-8') as f:
                json.dump({'total': len(all_email_records), 'last_city': city, 'records': all_email_records}, f, ensure_ascii=False)
        
        await browser.close()
    
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_email_records, f, ensure_ascii=False, indent=2)
    print(f'\nDONE: {len(all_email_records)} emails saved to {OUT_JSON}')

if __name__ == '__main__':
    asyncio.run(main())
