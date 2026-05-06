"""
Fast Gelbe Seiten detail page scraper using httpx.
Uses existing GS detail URLs + extracts real clinic websites from each page.
"""
import asyncio, csv, re, json, time
import httpx
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
}

GENERIC = {'info','kontakt','praxis','service','team','office','mail','termin','rezeption','empfang','sekretariat','poststelle','redaktion','webmaster','noreply','datenschutz'}
PUBLIC = {'gmail.com','yahoo.com','hotmail','outlook.com','web.de','t-online.de','gmx.de','aol.com','icloud.com','protonmail.com','mail.de','freenet.de','live.de','msn.com'}
BAD = {'sentry','usercentrics','cookiebot','kzvh','kzvr','zaek','aekwl','bezreg','lzkth','lzkbw','lzk','brd.nrw','sozmi','blzk','bezirksstelle','zahnarztboerse','dentale','google.com','facebook','instagram','linkedin','xing','twitter','bit.ly','domain.com','alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft','sentry.io','sentry-next'}
CHAIN = {'alldent','dentalke','dentall','dentazoo','dentacon','dentalligator','dentaloft'}
PLATFORM_FRAGS = ['golocal','stadtbranchenbuch','kennstdueinen','dastelefonbuch','dasoertliche','11880','jameda','docinsider','gsservice']

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

def is_platform(url):
    if not url: return True
    lo = url.lower()
    return any(p in lo for p in PLATFORM_FRAGS)

def clean_name(cn):
    if not cn: return '', ''
    n = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*|Gemeinschaftspraxis\s*|Facharzt\s*|Zahnärztin\s*|Zahnarzt\s*|Oralchirurgie\s*|Kieferorthopädie\s*)','',cn,flags=re.I).strip()
    n = re.sub(r'[\.,]+$','',n)
    p = n.split()
    return (p[0] if p else '', p[-1] if len(p)>=2 else n)

async def get_real_website_from_detail(client, gs_url):
    """Extract clinic name + real website from a GS detail page."""
    try:
        r = await client.get(gs_url, timeout=httpx.Timeout(15.0, connect=8.0), follow_redirects=True, headers=HDRS)
        if r.status_code != 200: return '', None
        html = r.text
        
        # Extract clinic name from h1
        name_match = re.search(r'<h1[^>]*>\s*<a[^>]*>([^<]+)</a>', html)
        if not name_match:
            name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        name = name_match.group(1).strip() if name_match else ''
        
        # Extract external website links
        # Priority 1: "Zur Website" buttons
        website_patterns = [
            r'href="(https?://(?!www\.gelbeseiten)[^"?#]+)"[^>]*>\s*<[^>]*>\s*(?:zur\s+)?website',
            r'"zurWebsiteUrl"\s*:\s*"([^"]+)"',
            r'"websiteUrl"\s*:\s*"([^"]+)"',
            r'data-website-url=["\']([^"\']+)["\']',
        ]
        for pat in website_patterns:
            m = re.search(pat, html, re.I)
            if m:
                url = m.group(1).strip()
                if url and 'gelbeseiten' not in url.lower() and not is_platform(url):
                    return name, url
        
        # Priority 2: Extract all external links and score them
        all_links = re.findall(r'href="(https?://[^"?#]+)"', html)
        best_url = None
        for url in all_links:
            if 'gelbeseiten' in url.lower(): continue
            if is_platform(url): continue
            if any(b in url.lower() for b in ['facebook','instagram','linkedin','bing','google','yahoo','apple']): continue
            # Score by domain quality
            domain = url.split('/')[2].lower() if '://' in url else ''
            if domain and not any(p in domain for p in PLATFORM_FRAGS):
                # Prefer specific domains over generic ones
                if any(k in url.lower() for k in ['website','homepage']):
                    return name, url.split('?')[0].split('#')[0]
                elif not best_url:
                    best_url = url.split('?')[0].split('#')[0]
        return name, best_url
    except:
        return '', None

async def get_email(client, website_url):
    """Fast impressum email extraction."""
    if not website_url or is_platform(website_url): return ''
    base = website_url.rstrip('/')
    paths = ['/impressum','/impressum/','/impress','/legal','/rechtliches','/kontakt']
    for path in paths:
        try:
            r = await client.get(base + path, timeout=httpx.Timeout(10.0, connect=5.0), follow_redirects=True, headers=HDRS)
            if r.status_code == 200 and len(r.text) > 300:
                emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
                for e in emails:
                    if is_good(e): return e
        except: pass
    return ''

async def main():
    # Collect ALL GS detail URLs from all data files
    all_gs_urls = []
    
    # From v2 batches
    for bf in sorted(BASE.glob('v2_batch*.json')):
        try:
            d = json.load(open(bf, 'r', encoding='utf-8'))
            for rec in d.get('records', []):
                url = rec.get('website','')
                if 'gelbeseiten' in url.lower():
                    all_gs_urls.append(url)
        except: pass
    
    # From leads_batch CSVs
    for bf in sorted(BASE.glob('leads_batch_*.csv')):
        try:
            with open(bf, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f, delimiter=';'):
                    url = row.get('website','')
                    if 'gelbeseiten' in url.lower():
                        all_gs_urls.append(url)
        except: pass
    
    # Deduplicate
    all_gs_urls = list(dict.fromkeys(all_gs_urls))
    print(f'Collected {len(all_gs_urls)} GS detail URLs')
    
    # Process in batches
    all_emails = []
    seen_websites = set()
    SEM = asyncio.Semaphore(30)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0), limits=httpx.Limits(max_connections=60), headers=HDRS) as client:
        for i, gs_url in enumerate(all_gs_urls):
            name, website = await get_real_website_from_detail(client, gs_url)
            
            if website and website not in seen_websites and not is_platform(website):
                seen_websites.add(website)
                em = await get_email(client, website)
                if em:
                    fn, ln = clean_name(name)
                    all_emails.append({'vorname': fn, 'nachname': ln, 'email': em, 'website': website})
                    print(f'  EMAIL: {em} | {fn} {ln}')
            
            if (i+1) % 50 == 0:
                print(f'  [{i+1}/{len(all_gs_urls)}] {len(all_emails)} emails found')
    
    # Save
    out = BASE / 'gs_detail_emails.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(all_emails, f, ensure_ascii=False, indent=2)
    
    print(f'\nTotal: {len(all_emails)} emails from {len(all_gs_urls)} GS detail pages')
    print(f'Saved: {out}')
    for r in all_emails[:5]:
        print(f'  {r["vorname"]} {r["nachname"]} | {r["email"]}')

if __name__ == '__main__':
    asyncio.run(main())
