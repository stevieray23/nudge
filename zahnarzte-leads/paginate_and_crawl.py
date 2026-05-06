"""
Paginating Gelbe Seiten scraper: get ALL pages (1-10) per city, extract real websites, crawl emails.
Saves progress every city so it can resume on crash.
"""
import asyncio, csv, re, json, time
import httpx
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
CHECKPOINT = BASE / 'paginate_checkpoint.json'
OUT_CSV = BASE / 'paginate_final.csv'
HDRS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36','Accept-Language':'de-DE,de;q=0.9'}

GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz'}
PUBLIC = {'gmail.com','yahoo.com','hotmail.com','outlook.com','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com'}
BAD_EMAILS = {'sentry','usercentrics','cookiebot','google.com','facebook','instagram','linkedin','xing','twitter','bit.ly','kzvh','kzvr','zaek','aekwl','bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi','blzk','bezirksstelle','zahnarztboerse','dentale','domain.com','alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft','sentry.io','sentry-next','exceptions.doctolib','wixpress.com'}
IMPRESSUM = ['/impressum','/impressum/','/impress','/legal','/rechtliches']
SEM = 60

def is_bad(e):
    if not e or '@' not in e: return True
    lo = e.lower()
    local = lo.split('@')[0]
    domain = lo.split('@')[1] if '@' in lo else ''
    if any(x in lo for x in ['.png','.jpg','.svg','data:image','@2x','@3x','favicon']): return True
    if any(x in domain for x in BAD_EMAILS): return True
    if any(x in local for x in BAD_EMAILS): return True
    if local in GENERIC:
        if any(p in domain for p in PUBLIC): return True
        if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch')): return False
        return True
    return False

def is_good(e):
    if not e or is_bad(e): return False
    lo = e.lower()
    local = lo.split('@')[0]
    domain = lo.split('@')[1] if '@' in lo else ''
    # Accept personal name patterns
    if '.' in local and len(local) >= 4: return True
    if '-' in local or '_' in local: return True
    if len(local) >= 3 and local[0].isupper(): return True
    # Accept named clinic domains
    if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch')) and len(domain.split('.')[0]) >= 3:
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

async def get_listing_urls(page, city, max_pages=8):
    """Paginate through Gelbe Seiten listing pages and return all detail URLs."""
    all_gs_urls = set()
    for pnum in range(1, max_pages+1):
        if pnum == 1:
            url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
        else:
            url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}/seite-{pnum}'
        try:
            await page.goto(url, wait_until='networkidle', timeout=25000)
            await asyncio.sleep(2.5)
            links = await page.query_selector_all('a[href*="/gsbiz/"]')
            found = 0
            for a in links:
                href = await a.get_attribute('href')
                if href and '/gsbiz/' in (href or ''):
                    if href.startswith('http'):
                        all_gs_urls.add(href)
                    else:
                        all_gs_urls.add('https://www.gelbeseiten.de' + href)
                    found += 1
            print(f'    [{city}] Page {pnum}: {found} listings')
            if found == 0:
                break  # No more results
        except Exception as e:
            print(f'    [{city}] Page {pnum} error: {e}')
            break
    return list(all_gs_urls)

async def get_real_website(gs_url, ctx):
    try:
        pg = await ctx.new_page()
        await pg.goto(gs_url, wait_until='domcontentloaded', timeout=20000)
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

async def main():
    # Load checkpoint
    done_cities = set()
    done_websites = set()
    email_records = []
    if CHECKPOINT.exists():
        data = json.load(open(CHECKPOINT, 'r', encoding='utf-8'))
        done_cities = set(data.get('done_cities', []))
        done_websites = set(data.get('done_websites', []))
        email_records = data.get('email_records', [])
        print(f'Resuming: {len(done_cities)} cities done, {len(done_websites)} websites done, {len(email_records)} emails found')
    
    CITIES = [
        'Frankfurt am Main','Bremen','Essen','Bochum','Bielefeld','Bonn',
        'Münster','Mannheim','Karlsruhe','Augsburg','Wiesbaden','Mönchengladbach',
        'Gelsenkirchen','Braunschweig','Aachen','Kiel','Chemnitz','Halle (Saale)',
        'Magdeburg','Freiburg im Breisgau','Krefeld','Mainz','Lübeck','Erfurt',
        'Dresden','Leipzig','Nürnberg','Stuttgart','Düsseldorf','Dortmund',
        'Berlin','Hamburg','Hannover','München','Köln'
    ]
    
    async def process_city(browser, city):
        if city in done_cities: return 0, 0
        ctx = await browser.new_context(user_agent=HDRS['User-Agent'], locale='de-DE')
        pg = await ctx.new_page()
        gs_urls = await get_listing_urls(pg, city, max_pages=8)
        await pg.close()
        new_sites = 0
        new_emails = 0
        for gs_url in gs_urls:
            if gs_url in done_websites: continue
            name, website = await get_real_website(gs_url, ctx)
            if website and not is_platform(website) and website not in done_websites:
                done_websites.add(website)
                new_sites += 1
                fn, ln = clean_name(name)
                # Crawl email
                async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), limits=httpx.Limits(max_connections=SEM)) as client:
                    em = await get_email(client, website)
                if em:
                    email_records.append({'vorname': fn, 'nachname': ln, 'email': em, 'website': website, 'city': city})
                    new_emails += 1
                    print(f'      EMAIL: {em} | {fn} {ln}')
            done_websites.add(gs_url)
            await asyncio.sleep(0.2)
        await ctx.close()
        # Save checkpoint
        with open(CHECKPOINT, 'w', encoding='utf-8') as f:
            json.dump({'done_cities': list(done_cities | {city}), 'done_websites': list(done_websites), 'email_records': email_records}, f, ensure_ascii=False)
        return new_sites, new_emails
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for i, city in enumerate(CITIES):
            if city in done_cities: continue
            print(f'[{i+1}/{len(CITIES)}] Processing: {city}')
            sites, emails = await process_city(browser, city)
            print(f'  [{city}] +{sites} websites, +{emails} emails. Running total: {len(email_records)} emails')
            await asyncio.sleep(0.5)
        await browser.close()
    
    # Save final CSV
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
        writer.writeheader()
        for r in email_records:
            writer.writerow({'vorname': r.get('vorname',''), 'nachname': r.get('nachname',''), 'email': r.get('email',''), 'adress': '', 'website': r.get('website','')})
    print(f'\nFinal: {len(email_records)} emails saved to {OUT_CSV}')

if __name__ == '__main__':
    asyncio.run(main())
