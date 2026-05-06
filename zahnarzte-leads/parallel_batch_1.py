"""
Parallel Pipeline Agent 1: Frankfurt, Bremen, Essen, Bochum, Bielefeld, Bonn
Full pipeline: GelbeSeiten scrape -> real website extraction -> impressum crawl -> CSV
"""
import asyncio, json, re, csv, time, httpx
from pathlib import Path
from playwright.async_api import async_playwright

CITIES = ['Frankfurt am Main', 'Bremen', 'Essen', 'Bochum', 'Bielefeld', 'Bonn']
OUT_DIR = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\paralysis1')
OUT_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUT = OUT_DIR / 'leads_agent1.csv'

BAD_EMAILS = {'noreply','no-reply','datenschutz','privacy','info@','kontakt@','praxis@','service@',
    'support@','team@','office@','mail@','blzk@','kennstdueinen','jameda','usercentrics',
    'sentry.io','sentry-next','domain.com','google.com','lzk','kzvr','lzkth','aekwl','zaek-sh',
    'zaeksh','bezreg','brd.nrw','sozmi.landsh','docinsider','jimdo','webnode','wix.com',
    'cookie','consent','borlabs','tracking','marketing','poststelle','redaktion','webmaster@',
    'presse@','redaktion@','datenschutzbeauftragte','lzkth','zahnarztboerse','dentale',
    'kzvr.de','kzvs','zaek-sh','zaeksh','aeksh','zaekwl','kzvwl','bezreg-koeln','lzk','aekwl'}
GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat'}

def is_bad(e):
    if not e: return True
    lo = e.lower()
    if any(b in lo for b in BAD_EMAILS): return True
    lp = lo.split('@')[0] if '@' in lo else ''
    if lp in GENERIC: return True
    return False

def clean_name(cn):
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*)','',cn,flags=re.I).strip()
    p = n.split()
    return (p[0] if len(p)>=1 else '', p[-1] if len(p)>=2 else n)

async def get_real_website(gs_url, ctx):
    try:
        pg = await ctx.new_page()
        await pg.goto(gs_url, wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(2)
        h1 = await pg.query_selector('h1')
        name = (await h1.inner_text()).strip() if h1 else ''
        links = await pg.query_selector_all('a[href]')
        best_url = None
        for a in links:
            href = await a.get_attribute('href')
            txt = (await a.inner_text() or '').lower()
            if href and href.startswith('http') and 'gelbeseiten' not in href.lower():
                bad = ['facebook','instagram','linkedin','bing','google','yahoo','apple','docinsider','jimdo','webnode']
                if any(b in href.lower() for b in bad): continue
                if 'website' in txt or 'homepage' in txt or 'zur ' in txt:
                    best_url = href.split('?')[0].split('#')[0]; break
                elif not best_url:
                    best_url = href.split('?')[0].split('#')[0]
        await pg.close()
        return name, best_url
    except: return '', None

async def get_email_via_http(website_url):
    base = website_url.rstrip('/')
    paths = [f'{base}/impressum', f'{base}/impressum/', f'{base}/impress', f'{base}/legal', f'{base}/rechtliches']
    hdrs = {'User-Agent':'Mozilla/5.0','Accept-Language':'de-DE,de;q=0.9'}
    async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as cl:
        for p in paths:
            try:
                r = await cl.get(p, headers=hdrs)
                if r.status_code==200 and r.text:
                    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                    for e in emails:
                        if not is_bad(e): return p, e
                    if len(r.text)>500: return p, None
            except: pass
    return None, None

async def scrape_city(browser, city):
    ctx = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36', locale='de-DE')
    pg = await ctx.new_page()
    records = []
    try:
        url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
        await pg.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        links = await pg.query_selector_all('a[href*="/gsbiz/"]')
        gs_urls = list({('https://www.gelbeseiten.de'+a.get_attribute('href')) if not a.get_attribute('href').startswith('http') else a.get_attribute('href') for a in links if '/gsbiz/' in (a.get_attribute('href') or '')})
        print(f'[{city}] {len(gs_urls)} listings')
        for gs_url in gs_urls:
            name, website = await get_real_website(gs_url, ctx)
            if website:
                records.append({'clinic_name':name,'city':city,'website':website})
                print(f'  + {website}')
            await asyncio.sleep(0.3)
    except Exception as e:
        print(f'[{city}] Error: {e}')
    finally:
        await ctx.close()
    return records

async def crawl_websites(records):
    results = []
    for i,r in enumerate(records):
        imp_url, email = await get_email_via_http(r['website'])
        fn, ln = clean_name(r['clinic_name'])
        if email and not is_bad(email):
            results.append({'vorname':fn,'nachname':ln,'email':email,'adress':'','website':r['website']})
            print(f'  EMAIL: {email} | {fn} {ln}')
        else:
            results.append({'vorname':fn,'nachname':ln,'email':'','adress':'','website':r['website']})
        if (i+1)%10==0: print(f'  [{i+1}/{len(records)}] crawled')
        await asyncio.sleep(0.2)
    return results

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        all_records = []
        for city in CITIES:
            print(f'=== Scraping {city} ===')
            recs = await scrape_city(browser, city)
            all_records.extend(recs)
            print(f'[{city}] {len(recs)} real websites')
        await browser.close()
    print(f'Total websites: {len(all_records)}')
    results = await crawl_websites(all_records)
    with open(CSV_OUT,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
        w.writeheader()
        w.writerows(results)
    print(f'Done. CSV: {CSV_OUT}')
    print(f'Clean emails: {sum(1 for r in results if r["email"])}')

if __name__=='__main__':
    asyncio.run(main())
