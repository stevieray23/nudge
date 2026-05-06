"""
Ultra-fast city scraper - Group 2 (10 cities, 3 parallel browsers)
"""
import asyncio, json, re, csv, httpx
from pathlib import Path
from playwright.async_api import async_playwright

CITIES = ['Wiesbaden','Mönchengladbach','Gelsenkirchen','Braunschweig','Aachen','Kiel','Chemnitz','Halle (Saale)','Magdeburg','Freiburg im Breisgau']
BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
OUT = BASE / 'v2_batch2.json'
SEEN_FILE = BASE / 'v2_seen_websites.json'

if SEEN_FILE.exists():
    seen_websites = set(json.load(open(SEEN_FILE,'r',encoding='utf-8')))
else:
    seen_websites = set()

HDRS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36','Accept-Language':'de-DE,de;q=0.9'}
IMPRESSUM_PATHS = ['/impressum','/impressum/','/impress','/legal','/rechtliches','/kontakt']
SEM = asyncio.Semaphore(60)
BAD_EMAILS = {'noreply','no-reply','datenschutz','privacy','info@','kontakt@','praxis@','service@','support@','team@','office@','mail@','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','cookie','consent','borlabs','tracking','marketing','sentry','usercentrics','google.com','domain.com','bezirk','lzk','kzvr','kzvs','zaek','aek','bezreg','lzkth','lzkbw','bezirksstelle','lzk-nrw','aekwl','bezreg-koeln','bezreg','docinsider','jameda','jimdo','webnode','wix.com','squarespace','dentalke','dental','zahni','zahn','dentall','alldent'}
GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle'}
PLATFORMS = ['golocal','stadtbranchenbuch','kennstdueinen','dastelefonbuch','dasoertliche','11880','jameda','docinsider']

def is_bad(e):
    if not e: return True
    lo = e.lower()
    if any(b in lo for b in BAD_EMAILS): return True
    lp = lo.split('@')[0] if '@' in lo else ''
    if lp in GENERIC: return True
    if '.png' in lo or '.jpg' in lo or '.svg' in lo: return True
    return False

def is_personal(e):
    if not e or is_bad(e): return False
    lo = e.lower()
    if any(p in lo for p in PLATFORMS): return False
    lp = lo.split('@')[0]
    if '.' in lp and len(lp) > 4: return True
    if len(lp) >= 3 and lp[0].isupper() and any(c.islower() for c in lp): return True
    if re.match(r'^[a-z]+\.[a-z]+$', lo.split('@')[1] if '@' in lo else ''): return True
    return False

def clean_name(cn):
    if not cn: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Dr\.?\s*med\.?\s*dent\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Fachpraxis\s*|Zahnärztin\s*|Zahnarzt\s*)', '', cn, flags=re.I).strip()
    n = re.sub(r'[\.,]+$', '', n)
    p = n.split()
    return (p[0] if p else '', p[-1] if len(p) >= 2 else n)

def is_platform_url(url):
    if not url: return True
    lo = url.lower()
    return any(p in lo for p in PLATFORMS)

async def crawl_one(client, url, name):
    async with SEM:
        base = url.rstrip('/')
        for path in IMPRESSUM_PATHS:
            try:
                r = await client.get(base + path, headers=HDRS, timeout=8.0, follow_redirects=True)
                if r.status_code == 200 and len(r.text) > 300:
                    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                    for e in emails:
                        if is_personal(e):
                            fn, ln = clean_name(name)
                            return fn, ln, e
            except: pass
        fn, ln = clean_name(name)
        return fn, ln, ''

async def scrape_one_city(browser, city):
    ctx = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36', locale='de-DE')
    pg = await ctx.new_page()
    records = []
    try:
        await pg.goto(f'https://www.gelbeseiten.de/suche/zahnarzt/{city}', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        links = await pg.query_selector_all('a[href*="/gsbiz/"]')
        gs_urls = []
        for a in links:
            href = await a.get_attribute('href')
            if href and '/gsbiz/' in (href or ''):
                gs_urls.append(('https://www.gelbeseiten.de' + href) if not href.startswith('http') else href)
        gs_urls = list(dict.fromkeys(gs_urls))
        print(f'  [{city}] {len(gs_urls)} listings')
        for gs_url in gs_urls:
            dp = await ctx.new_page()
            try:
                await dp.goto(gs_url, wait_until='domcontentloaded', timeout=20000)
                await asyncio.sleep(1.5)
                h1 = await dp.query_selector('h1')
                name = (await h1.inner_text()).strip() if h1 else ''
                all_links = await dp.query_selector_all('a[href]')
                best = None
                for al in all_links:
                    href = await al.get_attribute('href')
                    txt = (await al.inner_text() or '').lower()
                    if href and href.startswith('http') and 'gelbeseiten' not in href.lower() and not is_platform_url(href):
                        bad = ['facebook','instagram','linkedin','bing','google','yahoo','apple','docinsider','jimdo','webnode','golocal','stadtbranchenbuch','kennstdueinen','dastelefonbuch','11880']
                        if any(b in href.lower() for b in bad): continue
                        if any(k in txt for k in ['website','homepage','zur web']) and not is_platform_url(href):
                            best = href.split('?')[0].split('#')[0]; break
                        elif not best and not is_platform_url(href):
                            best = href.split('?')[0].split('#')[0]
                if best and not is_platform_url(best) and best not in seen_websites:
                    records.append({'website': best.split('?')[0].split('#')[0], 'clinic_name': name, 'city': city})
                    print(f'    + {best}')
            except: pass
            finally: await dp.close()
            await asyncio.sleep(0.15)
    except Exception as e:
        print(f'  [{city}] Error: {e}')
    finally:
        await ctx.close()
    return records

async def main():
    print(f'Cities: {CITIES}')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        all_recs = []
        for i in range(0, len(CITIES), 3):
            chunk = CITIES[i:i+3]
            print(f'--- Batch {i//3+1}: {chunk}')
            tasks = [scrape_one_city(browser, c) for c in chunk]
            res = await asyncio.gather(*tasks)
            for r in res: all_recs.extend(r)
            print(f'  Running total: {len(all_recs)} websites')
        await browser.close()
    print(f'Total websites: {len(all_recs)}')
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), limits=httpx.Limits(max_connections=60)) as client:
        tasks = [crawl_one(client, r['website'], r['clinic_name']) for r in all_recs]
        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            fn, ln, em = await coro
            results.append((i, fn, ln, em))
            if (i+1) % 50 == 0:
                done = sum(1 for _,_,_,e in results if e)
                print(f'  [{i+1}/{len(all_recs)}] {done} emails')
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'records': all_recs, 'results': [{'fn':r[1],'ln':r[2],'em':r[3]} for r in results]}, f, ensure_ascii=False)
    print(f'Saved: {OUT} | Emails: {sum(1 for r in results if r[3])}')

if __name__ == '__main__':
    asyncio.run(main())
