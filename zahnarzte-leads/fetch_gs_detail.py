"""
Use web_fetch to extract real clinic websites from existing GS detail page URLs.
web_fetch can render JS, so it can follow the GS SPA redirects.
"""
import csv, json, re, asyncio, httpx
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
OUT_JSON = BASE / 'gs_detail_fetched.json'
OUT_CSV = BASE / 'gs_detail_emails.csv'

HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9',
}

GENERIC_LOCAL = {'info','kontakt','praxis','service','team','office','mail','termin',
    'rezeption','empfang','sekretariat','poststelle','redaktion','webmaster',
    'noreply','datenschutz','terminvergabe','anmeldung'}
PUBLIC = {'gmail.com','yahoo.com','hotmail','outlook.com','web.de','t-online.de',
    'gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de',
    'live.de','msn.com','gmx.net','email.de','live.com','outlook.de','arcor.de'}
BAD_DOMAINS = {'sentry','usercentrics','kzvh','kzvr','zaek','aekwl','bezreg','lzkth',
    'lzkbw','lzk','brd.nrw','alldent','dentalke','dentall','dentazoo','dentacon',
    'dentaloft','doctolib','jameda','docinsider','sentry.io','wixpress.com',
    'sentry-next','stadtbranchenbuch','golocal','11880.com','dasoertliche'}
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

def extract_website(html):
    """Extract real clinic website URL from GS detail page HTML."""
    patterns = [
        r'href="(https?://(?!www\.gelbeseiten)[^"?#\s]+)"[^>]*>\s*(?:zur\s+)?website',
        r'"zurWebsiteUrl"\s*:\s*"([^"]+)"',
        r'"websiteUrl"\s*:\s*"([^"]+)"',
        r'data-website-url=["\']([^"\']+)["\']',
        r'class="[^"]*website[^"]*"[^>]*href="([^"]+)"',
        r'class="[^"]*url[^"]*"[^>]*href="(https?://(?!gelbeseiten)[^"]+)"',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.I)
        if m:
            url = m.group(1).strip()
            if url and url.startswith('http') and 'gelbeseiten' not in url.lower():
                return url
    return None

def extract_clinic_name(html):
    """Extract clinic name from detail page."""
    patterns = [
        r'<h1[^>]*>\s*<a[^>]*>\s*([^<]+)',
        r'<h1[^>]*>([^<]+)</h1>',
        r'data-testid=".*?name.*?>([^<]+)<',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.I)
        if m:
            name = m.group(1).strip()
            if name and len(name) >= 3 and not name.startswith('http'):
                return name
    return ''

async def fetch_detail(client, gs_url):
    """Fetch a GS detail page and extract real website + email."""
    try:
        r = await client.get(gs_url, timeout=httpx.Timeout(15.0, connect=8.0),
            follow_redirects=True, headers=HDRS)
        if r.status_code != 200: return None
        html = r.text
        name = extract_clinic_name(html)
        website = extract_website(html)
        return {'name': name, 'website': website, 'gs_url': gs_url}
    except Exception as ex:
        return None

async def get_email(client, url):
    if not url or 'gelbeseiten' in url.lower(): return ''
    base = url.rstrip('/')
    for path in ['/impressum','/impressum/','/impress','/legal']:
        try:
            r = await client.get(base + path, timeout=httpx.Timeout(10.0, connect=5.0),
                follow_redirects=True, headers=HDRS)
            if r.status_code == 200 and len(r.text) > 500:
                emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                for e in emails:
                    if is_ok(e): return e
        except: pass
        await asyncio.sleep(0.1)
    return ''

async def main():
    # Collect all unique GS detail URLs from all batch files
    gs_urls = set()
    
    for bf in sorted(BASE.glob('leads_batch_*.csv')):
        with open(bf, encoding='utf-8', errors='ignore') as f:
            for row in csv.DictReader(f, delimiter=';'):
                url = row.get('website','').strip()
                if 'gelbeseiten' in url.lower():
                    gs_urls.add(url)
    
    for bf in sorted(BASE.glob('v2_batch*.json')):
        try:
            d = json.load(open(bf, encoding='utf-8'))
            for rec in d.get('records', []):
                url = rec.get('website','')
                if 'gelbeseiten' in url.lower():
                    gs_urls.add(url)
        except: pass
    
    urls = list(dict.fromkeys(gs_urls))
    print(f'Found {len(urls)} unique GS detail URLs')
    
    # Deduplicate by URL path (GS has duplicate URLs with different params)
    unique_urls = list(dict.fromkeys(urls))
    print(f'Deduplicated: {len(unique_urls)}')
    
    # Sample a few to test
    sample = unique_urls[:20]
    results = []
    SEM = asyncio.Semaphore(10)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0),
        limits=httpx.Limits(max_connections=20)) as client:
        for i, url in enumerate(sample):
            async with SEM:
                rec = await fetch_detail(client, url)
                if rec and rec['website']:
                    email = await get_email(client, rec['website'])
                    rec['email'] = email
                    results.append(rec)
                    print(f'  [{i+1}/{len(sample)}] {rec["name"]} -> {rec["website"]} -> {email}')
                else:
                    print(f'  [{i+1}/{len(sample)}] No website found: {url[:80]}')
    
    print(f'\nGot {len(results)} websites from {len(sample)} GS pages')
    
    # Save
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    if results:
        with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['name','email','website','gs_url'], delimiter=';')
            w.writeheader()
            w.writerows(results)
        print(f'Saved {len(results)} to {OUT_CSV}')
    
    for r in results[:5]:
        print(f'  {r["name"]} | {r["email"]} | {r["website"]}')

if __name__ == '__main__':
    asyncio.run(main())
