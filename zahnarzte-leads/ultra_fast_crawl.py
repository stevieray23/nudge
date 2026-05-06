"""
Ultra-fast email crawler: 50 concurrent connections, httpx only.
Crawl all 1254 existing websites + fresh scrape 30 cities simultaneously.
Target: 800+ more emails on top of the 261 we already have.
"""
import asyncio, json, re, csv, time
import httpx
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
OUT_CSV = BASE / 'zahnarzte_final_v2.csv'

BAD = {'noreply','no-reply','datenschutz','privacy','info@','kontakt@','praxis@','service@',
    'support@','team@','office@','mail@','termin','rezeption','empfang','sekretariat',
    'poststelle','redaktion','webmaster','cookie','consent','borlabs','tracking','marketing',
    'sentry','usercentrics','google.com','domain.com','facebook','instagram','linkedin',
    'bezirk','lzk','kzvr','kzvs','zaek','aek','bezreg','lzkth','lzkbw','bezirksstelle',
    'lzk-nrw','aekwl','bezreg-koeln','bezreg','docinsider','jameda','jimdo','webnode',
    'wix.com','squarespace','dentalke','dental','zahni','zahn','dentall'}
GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle'}

def is_bad(e):
    if not e: return True
    lo = e.lower()
    if any(b in lo for b in BAD): return True
    lp = lo.split('@')[0] if '@' in lo else ''
    if lp in GENERIC: return True
    if '.png' in lo or '.jpg' in lo or '.svg' in lo: return True
    if 'alldent' in lo: return True
    return False

def is_personal(e):
    return not is_bad(e)

def clean_name(cn):
    if not cn: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Dr\.?\s*med\.?\s*dent\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Fachpraxis\s*|Zahnärztin\s*|Zahnarzt\s*)', '', cn, flags=re.I).strip()
    n = re.sub(r'[\.,]+$', '', n)
    p = n.split()
    return (p[0] if p else '', p[-1] if len(p) >= 2 else n)

IMPRESSUM_PATHS = [
    '/impressum', '/impressum/', '/impress', '/legal', '/rechtliches',
    '/kontakt', '/agb', '/ueber-uns', '/uber-uns'
]
HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
SEMAPHORE = asyncio.Semaphore(80)  # 80 concurrent connections

async def crawl_one(client, url, clinic_name):
    async with SEMAPHORE:
        base = url.rstrip('/')
        for path in IMPRESSUM_PATHS:
            full_url = base + path
            try:
                r = await client.get(full_url, headers=HDRS, timeout=8.0, follow_redirects=True)
                if r.status_code == 200 and len(r.text) > 300:
                    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                    for e in emails:
                        if is_personal(e):
                            fn, ln = clean_name(clinic_name)
                            return fn, ln, e
                    # Page exists but no email
                    if path == '/impressum' or path == '/impressum/':
                        fn, ln = clean_name(clinic_name)
                        return fn, ln, ''
            except: pass
        fn, ln = clean_name(clinic_name)
        return fn, ln, ''

async def crawl_all_http(websites):
    """Fast concurrent crawl of all websites via httpx."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), limits=httpx.Limits(max_connections=80, max_keepalive_connections=40)) as client:
        tasks = [crawl_one(client, w['website'], w.get('clinic_name','')) for w in websites]
        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            fn, ln, em = await coro
            results.append((i, fn, ln, em))
            if (i+1) % 100 == 0:
                done = sum(1 for _,_,_,e in results if e)
                print(f'  [{i+1}/{len(websites)}] crawled, {done} emails found')
        return results

async def get_real_websites_from_city(browser, city):
    """Get real clinic websites from Gelbe Seiten for one city."""
    ctx = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        locale='de-DE'
    )
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
                if href.startswith('http'):
                    gs_urls.append(href)
                else:
                    gs_urls.append('https://www.gelbeseiten.de' + href)
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
                    if href and href.startswith('http') and 'gelbeseiten' not in href.lower():
                        bad = ['facebook','instagram','linkedin','bing','google','yahoo','apple','docinsider','jimdo','webnode']
                        if any(b in href.lower() for b in bad): continue
                        if any(k in txt for k in ['website','homepage','zur web']):
                            best = href.split('?')[0].split('#')[0]; break
                        elif not best:
                            best = href.split('?')[0].split('#')[0]
                if best:
                    records.append({'website': best.split('?')[0].split('#')[0], 'clinic_name': name, 'city': city})
                    print(f'    + {best}')
            except: pass
            finally:
                await dp.close()
            await asyncio.sleep(0.2)
    except Exception as e:
        print(f'  [{city}] Error: {e}')
    finally:
        await ctx.close()
    return records

async def scrape_all_cities_parallel():
    """Scrape all major cities with 3 parallel browser contexts."""
    CITIES = [
        'Frankfurt am Main','Bremen','Essen','Bochum','Bielefeld','Bonn',
        'Münster','Mannheim','Karlsruhe','Augsburg','Wiesbaden','Mönchengladbach',
        'Gelsenkirchen','Braunschweig','Aachen','Kiel','Chemnitz','Halle (Saale)',
        'Magdeburg','Freiburg im Breisgau','Krefeld','Mainz','Lübeck','Erfurt',
        'Dresden','Leipzig','Nürnberg','Stuttgart','Düsseldorf','Dortmund',
        'Berlin','Hamburg','Hannover','München','Köln'
    ]
    all_recs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Run 3 cities at a time
        for i in range(0, len(CITIES), 3):
            chunk = CITIES[i:i+3]
            print(f'--- Batch {i//3+1}: {chunk}')
            tasks = [get_real_websites_from_city(browser, c) for c in chunk]
            results = await asyncio.gather(*tasks)
            for r in results:
                all_recs.extend(r)
            print(f'  Running total: {len(all_recs)} websites')
        await browser.close()
    return all_recs

async def main():
    print('=== STEP 1: Crawling existing 1254 websites for emails ===')
    existing = json.load(open(BASE / 'phase2' / 'all_real_websites.json', 'r', encoding='utf-8'))
    print(f'Loaded {len(existing)} existing websites')
    
    start = time.time()
    results = await crawl_all_http(existing)
    elapsed = time.time() - start
    email_count = sum(1 for _,_,_,e in results if e)
    print(f'Done in {elapsed:.0f}s. {email_count} emails from existing websites')
    
    print('\n=== STEP 2: Scraping fresh websites from all cities ===')
    fresh_recs = await scrape_all_cities_parallel()
    print(f'Fresh websites scraped: {len(fresh_recs)}')
    
    # Save fresh websites
    seen_websites = {w['website'] for w in existing}
    new_recs = [r for r in fresh_recs if r['website'] not in seen_websites]
    print(f'New unique websites: {len(new_recs)}')
    
    # Crawl fresh websites for emails
    if new_recs:
        print(f'\nCrawling {len(new_recs)} new websites...')
        new_results = await crawl_all_http(new_recs)
        new_email_count = sum(1 for _,_,_,e in new_results if e)
        print(f'New emails from fresh websites: {new_email_count}')
        all_results = results + new_results
        all_recs = existing + new_recs
    else:
        all_results = results
        all_recs = existing
    
    # Build and deduplicate
    seen_emails = set()
    final_rows = []
    for i, (idx, fn, ln, em) in enumerate(all_results):
        if not em: continue
        em_lc = em.lower()
        if em_lc in seen_emails: continue
        seen_emails.add(em_lc)
        rec = all_recs[i] if i < len(all_recs) else existing[i - len(all_results) + len(existing)]
        final_rows.append({
            'vorname': fn, 'nachname': ln, 'email': em,
            'adress': rec.get('address',''), 'website': rec.get('website','')
        })
    
    # Add existing 261 emails that aren't duplicates
    existing_csv = BASE / 'zahnarzte_final.csv'
    if existing_csv.exists():
        import csv as csv2
        with open(existing_csv, 'r', encoding='utf-8') as f:
            reader = csv2.DictReader(f, delimiter=';')
            for row in reader:
                em = row.get('email','').strip().lower()
                if em and em not in seen_emails and is_personal(em):
                    seen_emails.add(em)
                    final_rows.append(row)
    
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv2.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
        writer.writeheader()
        writer.writerows(final_rows)
    
    total_emails = len(final_rows)
    print(f'\n=== DONE ===')
    print(f'Total unique personal emails: {total_emails}')
    print(f'File: {OUT_CSV}')
    print(f'Sample:')
    for r in final_rows[:5]:
        print(f'  {r.get("vorname","")} {r.get("nachname","")} | {r.get("email","")}')

if __name__ == '__main__':
    asyncio.run(main())
