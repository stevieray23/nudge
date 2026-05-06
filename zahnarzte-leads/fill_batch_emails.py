"""
Fill in missing emails for batch leads by crawling their real clinic websites.
Process: for each batch entry without email -> find real clinic website -> crawl impressum.
"""
import asyncio, csv, re, json, httpx
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
HDRS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36','Accept-Language':'de-DE,de;q=0.9'}
IMPRESSUM = ['/impressum','/impressum/','/impress','/legal','/rechtliches','/kontakt']
SEM = asyncio.Semaphore(60)
PLATFORMS = ['golocal','stadtbranchenbuch','kennstdueinen','dastelefonbuch','dasoertliche','11880','jameda','docinsider','gsservice']
GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz'}
PUBLIC = {'gmail','yahoo','hotmail','outlook','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail','mail.de','freenet.de','live.de','msn.com'}
ASSOC = {'kzvh','kzvr','zaekwl','zaek','lzkth','lzkbw','lzk','bezreg','aekwl','aek','blzk','kzvs'}
CHAIN = {'alldent','dentalke','dentall','dentazoo','dentacon','dentaloft','dentalligator'}

def is_bad(e):
    if not e or '@' not in e: return True
    lo = e.lower()
    local = lo.split('@')[0]
    domain = lo.split('@')[1] if '@' in lo else ''
    if any(x in lo for x in ['.png','.jpg','.svg','data:image']): return True
    if any(a in domain for a in ASSOC): return True
    if any(a in domain for a in CHAIN): return True
    if any(a in local for a in ASSOC): return True
    if local in GENERIC:
        if any(p in domain for p in PUBLIC): return True
        if domain.endswith(('.de','.com','.net','.org','.info','.at','.ch')): return False
        return True
    return False

def is_platform(url):
    if not url: return True
    lo = url.lower()
    return any(p in lo for p in PLATFORMS) or 'gsservice' in lo

def clean_name(cn):
    if not cn: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Dr\.?\s*med\.?\s*dent\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Fachpraxis\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|Kieferorthopädie\s*|Zahnärztliche Praxis\s*)', '', cn, flags=re.I).strip()
    n = re.sub(r'[\.,]+$', '', n)
    p = n.split()
    return (p[0] if p else '', p[-1] if len(p) >= 2 else n)

async def get_real_website(gs_url, ctx):
    """Visit a Gelbe Seiten detail page and extract the real clinic website."""
    try:
        pg = await ctx.new_page()
        await pg.goto(gs_url, wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(1.5)
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
        return best
    except: return None

async def get_email_from_website(client, url):
    """Fast HTTP crawl of impressum page."""
    if not url or is_platform(url): return ''
    base = url.rstrip('/')
    for path in IMPRESSUM:
        try:
            r = await client.get(base + path, headers=HDRS, timeout=8.0, follow_redirects=True)
            if r.status_code == 200 and len(r.text) > 300:
                emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                for e in emails:
                    if not is_bad(e): return e
        except: pass
    return ''

async def main():
    # Collect all batch rows needing email
    all_rows = []
    batch_info = []
    for bf in sorted(BASE.glob('leads_batch_*.csv')):
        rows = list(csv.DictReader(open(bf, encoding='utf-8'), delimiter=';'))
        need_email = [r for r in rows if not r.get('email','').strip()]
        has_email = [r for r in rows if r.get('email','').strip()]
        batch_info.append({'file': bf.name, 'total': len(rows), 'need': len(need_email), 'has': len(has_email)})
        all_rows.extend(rows)
        print(f'{bf.name}: {len(rows)} rows, {len(need_email)} need email, {len(has_email)} have email')
    
    print(f'\nTotal: {len(all_rows)} rows, {sum(b["need"] for b in batch_info)} need email')
    
    # Find rows needing email that have a valid URL
    need_crawl = []
    for r in all_rows:
        if r.get('email','').strip(): continue  # already has email
        url = r.get('website','').strip()
        if url and not is_platform(url) and url.startswith('http'):
            need_crawl.append(r)
        else:
            # GS profile URL - needs real website extraction
            need_crawl.append(r)
    
    print(f'Need impressum crawl: {len(need_crawl)}')
    
    # De-duplicate URLs to crawl
    url_to_rows = {}
    for r in need_crawl:
        url = r.get('website','').strip()
        if url not in url_to_rows: url_to_rows[url] = []
        url_to_rows[url].append(r)
    
    unique_urls = list(url_to_rows.keys())
    print(f'Unique URLs to crawl: {len(unique_urls)}')
    
    # Step 1: Extract real websites from GS detail pages (batch in groups)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(user_agent=HDRS['User-Agent'], locale='de-DE')
        
        # Process GS URLs that need real website extraction
        gs_urls = [u for u in unique_urls if 'gelbeseiten' in u.lower() or is_platform(u)]
        direct_urls = [u for u in unique_urls if u not in gs_urls]
        print(f'GS URLs: {len(gs_urls)}, Direct URLs: {len(direct_urls)}')
        
        # Real website mapping
        real_website = {}
        for u in direct_urls:
            real_website[u] = u
        
        # Extract real websites from GS URLs in batches
        print('Extracting real websites from Gelbe Seiten detail pages...')
        for i in range(0, len(gs_urls), 5):
            chunk = gs_urls[i:i+5]
            tasks = [get_real_website(url, ctx) for url in chunk]
            results = await asyncio.gather(*tasks)
            for url, rw in zip(chunk, results):
                if rw and not is_platform(rw):
                    real_website[url] = rw
            print(f'  [{i+len(chunk)}/{len(gs_urls)}] done')
            await asyncio.sleep(0.5)
        
        await ctx.close()
        await browser.close()
    
    # Step 2: Crawl impressum for all unique real websites
    unique_real = list(set(real_website.values()))
    print(f'\nCrawling impressum for {len(unique_real)} unique real websites...')
    
    email_for_url = {}
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), limits=httpx.Limits(max_connections=60)) as client:
        tasks = [get_email_from_website(client, url) for url in unique_real]
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            em = await coro
            email_for_url[unique_real[i]] = em
            if (i+1) % 100 == 0:
                done = sum(1 for e in email_for_url.values() if e)
                print(f'  [{i+1}/{len(unique_real)}] {done} emails found')
    
    # Step 3: Update rows and save updated CSVs
    total_new_emails = 0
    for bf_info in batch_info:
        bf_name = bf_info['file']
        rows = list(csv.DictReader(open(BASE / bf_name, encoding='utf-8'), delimiter=';'))
        new_emails = 0
        for r in rows:
            if r.get('email','').strip(): continue  # keep existing
            url = r.get('website','').strip()
            real_url = real_website.get(url, url)
            em = email_for_url.get(real_url, '')
            if em:
                r['email'] = em
                # Update vorname/nachname if empty
                if not r.get('vorname','').strip():
                    vn, nn = clean_name(r.get('website',''))
                    if not r.get('vorname','').strip(): r['vorname'] = vn
                    if not r.get('nachname','').strip(): r['nachname'] = nn
                new_emails += 1
        # Save updated CSV
        out_path = BASE / f'filled_{bf_name}'
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
            writer.writeheader()
            writer.writerows(rows)
        print(f'Updated {bf_name}: +{new_emails} new emails, saved to filled_{bf_name}')
        total_new_emails += new_emails
    
    print(f'\nTotal new emails found: {total_new_emails}')
    print(f'Real websites extracted: {sum(1 for v in real_website.values() if v and v not in gs_urls)}')

if __name__ == '__main__':
    asyncio.run(main())
