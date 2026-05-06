"""
Parallel Pipeline - cities defined at runtime.
Run with: python3 parallel_batch_template.py
Cities passed as command-line args.
"""
import asyncio, re, csv, httpx, sys
from pathlib import Path
from playwright.async_api import async_playwright

CITIES = sys.argv[1].split(',') if len(sys.argv) > 1 else ['Berlin','Hamburg','Hannover','München','Köln']
AGENT_ID = sys.argv[2] if len(sys.argv) > 2 else 'agent_x'
OUT_DIR = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
CSV_OUT = OUT_DIR / f'leads_{AGENT_ID}.csv'

BAD = {'noreply','no-reply','datenschutz','privacy','info@','kontakt@','praxis@','service@',
    'support@','team@','office@','mail@','blzk@','kennstdueinen','jameda','usercentrics',
    'sentry.io','sentry-next','domain.com','google.com','lzk','kzvr','lzkth','aekwl','zaek-sh',
    'zaeksh','bezreg','brd.nrw','sozmi.landsh','docinsider','jimdo','webnode','wix.com',
    'cookie','consent','borlabs','tracking','marketing','poststelle','redaktion','webmaster@',
    'presse@','redaktion@','datenschutzbeauftragte','kzvr.de','kzvs','zaek-sh','zaeksh',
    'aeksh','zaekwl','kzvwl','bezreg-koeln','bezirk','lzk-nrw','lzkbw','bezirksstelle'}
GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat'}

def is_bad(e):
    if not e: return True
    lo = e.lower()
    if any(b in lo for b in BAD): return True
    lp = lo.split('@')[0] if '@' in lo else ''
    if lp in GENERIC: return True
    return False

def clean_name(cn):
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*)','',cn,flags=re.I).strip()
    p = n.split()
    return (p[0] if p else '', p[-1] if len(p)>=2 else n)

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
            if not href: continue
            if 'gelbeseiten' in href.lower(): continue
            bad_frag = ['facebook','instagram','linkedin','bing','google','yahoo','apple','docinsider','jimdo','webnode']
            if any(b in href.lower() for b in bad_frag): continue
            txt = (await a.inner_text() or '').lower()
            if any(k in txt for k in ['website','homepage','zur web','onlineshop']):
                best_url = href.split('?')[0].split('#')[0]
                break
            elif not best_url:
                best_url = href.split('?')[0].split('#')[0]
        await pg.close()
        return name, best_url
    except Exception as e:
        return '', None

async def get_email_via_http(website_url):
    base = website_url.rstrip('/')
    paths = [f'{base}/impressum', f'{base}/impressum/', f'{base}/impress', f'{base}/legal', f'{base}/rechtliches']
    hdrs = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36','Accept-Language':'de-DE,de;q=0.9'}
    async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as cl:
        for p in paths:
            try:
                r = await cl.get(p, headers=hdrs)
                if r.status_code==200 and r.text and len(r.text)>200:
                    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                    for e in emails:
                        if not is_bad(e): return p, e
                    return p, None  # page exists but no good email
            except: pass
    return None, None

async def scrape_city(browser, city):
    ctx = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        locale='de-DE'
    )
    pg = await ctx.new_page()
    records = []
    try:
        url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
        await pg.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        links = await pg.query_selector_all('a[href*="/gsbiz/"]')
        gs_urls = []
        for a in links:
            href = await a.get_attribute('href')
            if href and '/gsbiz/' in href:
                if href.startswith('http'):
                    gs_urls.append(href)
                else:
                    gs_urls.append('https://www.gelbeseiten.de' + href)
        gs_urls = list(dict.fromkeys(gs_urls))  # dedupe preserving order
        print(f'  [{city}] {len(gs_urls)} listings')
        for gs_url in gs_urls:
            name, website = await get_real_website(gs_url, ctx)
            if website:
                records.append({'clinic_name': name, 'city': city, 'website': website})
                print(f'    + {website}')
            await asyncio.sleep(0.2)
    except Exception as e:
        print(f'  [{city}] Error: {e}')
    finally:
        await ctx.close()
    return records

async def crawl_websites(records):
    results = []
    for i, r in enumerate(records):
        imp_url, email = await get_email_via_http(r['website'])
        fn, ln = clean_name(r['clinic_name'])
        if email and not is_bad(email):
            results.append({'vorname': fn, 'nachname': ln, 'email': email, 'adress': '', 'website': r['website']})
            print(f'    EMAIL: {email} | {fn} {ln}')
        else:
            results.append({'vorname': fn, 'nachname': ln, 'email': '', 'adress': '', 'website': r['website']})
        if (i+1) % 10 == 0:
            print(f'    [{i+1}/{len(records)}] crawled')
        await asyncio.sleep(0.15)
    return results

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        all_records = []
        for city in CITIES:
            print(f'=== Scraping {city} ===')
            recs = await scrape_city(browser, city)
            all_records.extend(recs)
            print(f'  [{city}] Got {len(recs)} real websites')
        await browser.close()
    print(f'Total real websites: {len(all_records)}')
    print(f'Crawling impressum for all {len(all_records)} websites...')
    results = await crawl_websites(all_records)
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
        w.writeheader()
        w.writerows(results)
    clean_emails = sum(1 for r in results if r['email'])
    print(f'Done! CSV: {CSV_OUT}')
    print(f'Clean emails: {clean_emails} / {len(results)} total')

if __name__ == '__main__':
    asyncio.run(main())
