"""
Fast resumable Impressum crawler.
Uses web_fetch (fast) first, then falls back to Playwright for failures.
Saves progress after every 50 sites. Can resume on crash.
"""
import json
import re
import csv
import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import httpx

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2')
OUT_DIR = BASE.parent
WEBSITES_FILE = BASE / 'all_real_websites.json'
CHECKPOINT_FILE = BASE / 'crawl_checkpoint.json'
OUT_CSV = OUT_DIR / 'zahnarzte_final.csv'

# Bad email patterns to filter out
BAD_EMAILS = {
    'noreply', 'no-reply', 'no_reply', 'datenschutz', 'privacy', 'info@', 'kontakt@',
    'praxis@', 'service@', 'support@', 'team@', 'office@', 'mail@',
    'blzk@', 'kennstdueinen', 'jameda', 'usercentrics', 'usercentrics.com',
    'sentry.io', 'sentry-next', 'domain.com', 'google.com', 'lzk', 'kzvr',
    'lzkth', 'aekwl', 'zaek-sh', 'zaeksh', 'bezreg', 'brd.nrw', 'sozmi.landsh',
    'docinsider', 'jimdo', 'webnode', 'wix.com', 'sentry', 'facebook', 'instagram',
    'linkedin', 'cookie', 'consent', 'borlabs', 'tracking', 'marketing',
    'poststelle', 'redaktion', 'webmaster@', 'abstimmung', 'presse@', 'redaktion@',
    'datenschutzbeauftragte', 'lzkth', 'zahnarztboerse', 'dentale',
    # Dental chamber / KZV emails
    'kzvr.de', 'kzvs', 'zaek-sh', 'zaeksh', 'aeksh', 'zaekwl', 'kzvwl',
    'bezreg-koeln', 'bezreg', 'lzk', 'lzkth', 'aekwl', 'bezirksregierung',
    'landesza', 'kassenzahn', 'lzk-nrw',
}

# Generic practice-level email patterns
GENERIC_PREFIXES = {'info', 'kontakt', 'praxis', 'service', 'team', 'office', 'mail', 'termin', 'rezeption', 'empfang', 'sekretariat'}


def is_bad_email(email):
    if not email:
        return True
    e = email.lower()
    if any(b in e for b in BAD_EMAILS):
        return True
    # Check if it's a generic practice email (first part is generic)
    local = e.split('@')[0] if '@' in e else ''
    if local in GENERIC_PREFIXES:
        return True
    return False


def extract_name_from_text(text, website_url):
    """Try to extract dentist name from impressum text."""
    # Look for name patterns near "Inhaber", "Zahnarzt", "Dr."
    patterns = [
        r'(?:Inhaber[in]?|Inhaberin|Verantwortlich(?:er)?|Zahnarzt[in]?|Zahnärztin)\s*[:\s]*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})',
        r'(?:Gesch[äa]ftsf[üu]hrer[in]?)\s*[:\s]*([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)',
        r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)',
        r'Name\s*[:\s]*([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            name = m.group(1).strip()
            parts = name.split()
            if len(parts) >= 2:
                return parts[0], parts[-1]
            return '', name
    return '', ''


async def try_webfetch_impressum(url):
    """Try to get impressum via fast HTTP fetch."""
    base = url.rstrip('/')
    paths_to_try = [
        f'{base}/impressum',
        f'{base}/impressum/',
        f'{base}/impress',
        f'{base}/legal',
        f'{base}/rechtliches',
        f'{base}/kontakt',
        f'{base}/agb',
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'de-DE,de;q=0.9',
    }
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        for path in paths_to_try:
            try:
                r = await client.get(path, headers=headers)
                if r.status_code == 200 and r.text:
                    content = r.text
                    # Extract emails
                    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', content)
                    # Clean and filter
                    valid = [e for e in emails if not is_bad_email(e)]
                    if valid:
                        return path, valid[0], content
                    elif content and len(content) > 200:
                        return path, None, content
            except:
                pass
    return None, None, ''


async def try_playwright_impressum(browser, url):
    """Fallback: use Playwright to get impressum."""
    ctx = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        locale='de-DE'
    )
    page = await ctx.new_page()
    result_email = None
    result_name = ('', '')
    impressum_url = None
    
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(1.5)
        
        # Try clicking impressum link
        impressum_links = []
        all_links = await page.query_selector_all('a[href]')
        for a in all_links:
            href = await a.get_attribute('href')
            text = (await a.inner_text() or '').lower()
            if href and any(k in text for k in ['impressum', 'impress', 'legal', 'rechtliches', 'anbieter']):
                if href.startswith('http'):
                    impressum_links.append(href)
                elif href.startswith('/'):
                    impressum_links.append(url.rstrip('/') + href)
        
        # Try direct paths
        base = url.rstrip('/')
        for path in [f'{base}/impressum', f'{base}/impress', f'{base}/legal', f'{base}/rechtliches']:
            if not impressum_links:
                try:
                    r = await page.goto(path, wait_until='domcontentloaded', timeout=8000)
                    if r and r.status < 400:
                        impressum_links.append(path)
                        impressum_url = path
                        break
                except:
                    pass
        
        if impressum_links:
            impressum_url = impressum_links[0]
            try:
                await page.goto(impressum_url, wait_until='domcontentloaded', timeout=10000)
                await asyncio.sleep(1.5)
            except:
                pass
        
        content = await page.inner_text('body')
        html = await page.content()
        
        # Extract emails
        emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', html)
        valid = [e for e in emails if not is_bad_email(e)]
        if valid:
            result_email = valid[0]
        
        result_name = extract_name_from_text(content, url)
        
    except Exception as e:
        pass
    finally:
        await ctx.close()
    
    return result_name[0], result_name[1], result_email


async def crawl_all_fast():
    """Main: try webfetch first, playwright fallback for failures."""
    with open(WEBSITES_FILE, 'r', encoding='utf-8') as f:
        websites = json.load(f)
    
    # Load checkpoint if exists
    checkpoint = {}
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        print(f"Resuming from checkpoint: {len(checkpoint)} already done")
    
    results = []
    pw = None
    
    for i, w in enumerate(websites):
        url = w['website']
        
        if url in checkpoint:
            results.append(checkpoint[url])
            continue
        
        vorname = checkpoint.get(url + '_v', '')
        nachname = checkpoint.get(url + '_n', '')
        email = checkpoint.get(url + '_e', '')
        
        # Try webfetch first (fast)
        imp_url, fetched_email, content = await try_webfetch_impressum(url)
        
        if fetched_email and not email:
            email = fetched_email
        elif fetched_email and email and is_bad_email(email):
            email = fetched_email
        
        # Extract name from content
        if content and not vorname and not nachname:
            vorname, nachname = extract_name_from_text(content, url)
        
        # If no email from webfetch, try playwright
        if not email:
            if pw is None:
                pw = await async_playwright().start()
                browser = await pw.chromium.launch(headless=True)
            vn, nn, em = await try_playwright_impressum(browser, url)
            if vn: vorname = vn
            if nn: nachname = nn
            if em and not email: email = em
        
        record = {
            'clinic_name': w.get('clinic_name', ''),
            'city': w.get('city', ''),
            'address': w.get('address', ''),
            'website': url,
            'vorname': vorname,
            'nachname': nachname,
            'email': email,
        }
        checkpoint[url] = record
        checkpoint[url + '_v'] = vorname
        checkpoint[url + '_n'] = nachname
        checkpoint[url + '_e'] = email
        results.append(record)
        
        if (i + 1) % 25 == 0:
            # Save checkpoint
            with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False)
            with open(CHECKPOINT_FILE.parent / 'checkpoint_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False)
            print(f"[{i+1}/{len(websites)}] Checkpoint saved. Email found: {sum(1 for r in results if r.get('email') and not is_bad_email(r.get('email','')))}")
        
        await asyncio.sleep(0.3)
    
    if pw:
        await pw.stop()
    
    # Save final
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False)
    with open(CHECKPOINT_FILE.parent / 'checkpoint_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False)
    
    return results


def export_csv(results):
    """Export clean CSV."""
    clean = []
    for r in results:
        email = r.get('email', '').strip()
        if email and not is_bad_email(email):
            vorname = r.get('vorname', '').strip() or extract_first_name(r.get('clinic_name', ''))
            nachname = r.get('nachname', '').strip() or extract_last_name(r.get('clinic_name', ''))
            clean.append({
                'vorname': vorname,
                'nachname': nachname,
                'email': email,
                'adress': r.get('address', ''),
                'website': r.get('website', ''),
            })
    
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['vorname', 'nachname', 'email', 'adress', 'website'], delimiter=';')
        writer.writeheader()
        writer.writerows(clean)
    
    print(f"\n=== FINAL EXPORT ===")
    print(f"Total records: {len(results)}")
    print(f"With clean emails: {len(clean)}")
    print(f"CSV saved to: {OUT_CSV}")


def extract_first_name(clinic_name):
    name = clinic_name.strip()
    name = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*)', '', name, flags=re.I)
    parts = name.split()
    if len(parts) >= 2:
        return parts[0]
    return ''


def extract_last_name(clinic_name):
    name = clinic_name.strip()
    name = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*)', '', name, flags=re.I)
    parts = name.split()
    if len(parts) >= 2:
        return parts[-1]
    return name


if __name__ == '__main__':
    results = asyncio.run(crawl_all_fast())
    export_csv(results)
