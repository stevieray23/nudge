"""
Full Gelbe Seiten scraper: visits all 33 German cities, navigates detail pages
to extract real clinic websites, then crawls each for Impressum + personal email.
Output: final CSV ready to export.
"""
import asyncio
import csv
import json
import re
import time
from pathlib import Path
from playwright.async_api import async_playwright

# All target cities
CITIES = [
    'Frankfurt am Main', 'Bremen', 'Essen', 'Bochum', 'Bielefeld', 'Bonn',
    'Münster', 'Mannheim', 'Karlsruhe', 'Augsburg', 'Wiesbaden', 'Mönchengladbach',
    'Gelsenkirchen', 'Braunschweig', 'Aachen', 'Kiel', 'Chemnitz', 'Halle (Saale)',
    'Magdeburg', 'Freiburg im Breisgau', 'Krefeld', 'Mainz', 'Lübeck', 'Erfurt',
    'Dresden', 'Leipzig', 'Nürnberg', 'Stuttgart', 'Düsseldorf', 'Dortmund',
    'Berlin', 'Hamburg', 'Hannover', 'München', 'Köln'
]

OUT_DIR = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2')
OUT_DIR.mkdir(parents=True, exist_ok=True)
WEBSITES_OUT = OUT_DIR / 'all_real_websites.json'
FINAL_CSV = OUT_DIR.parent / 'zahnarzte_final.csv'

SEEN_WEBSITES = set()
seen_urls = set()

BAD_URL_FRAGS = [
    'facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'xing.com',
    'bing.com', 'google.com', 'yahoo.com', 'apple.com', 'docinsider', 'jimdo',
    'webnode', 'wix.com', 'squarespace.com', 'tumblr.com', 'pinterest.com',
    'amazonaws', 'cloudfront', 'bit.ly', 't.co', ' Yelp'
]

BAD_EMAIL_PATTERNS = [
    'noreply', 'no-reply', 'datenschutz', 'privacy', 'info@', 'kontakt@',
    'praxis@', 'service@', 'support@', 'team@', 'office@', 'mail@',
    'blzk@', 'zahnarztboerse', 'kennstdueinen', 'jameda', 'doctors'
]

GENERIC_EMAILS = {'info@', 'kontakt@', 'service@', 'praxis@', 'office@', 'mail@', 'team@'}


def clean_website(url):
    if not url:
        return None
    url = url.strip()
    if 'gelbeseiten' in url.lower():
        return None
    url = re.sub(r'[?&]utm_[^&]+', '', url)
    url = re.sub(r'[?&]fb_[^&]+', '', url)
    url = url.split('?')[0].split('#')[0]
    if url.startswith('//'):
        url = 'https:' + url
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    if not url.startswith('https://'):
        url = 'https://' + url
    if any(b in url.lower() for b in BAD_URL_FRAGS):
        return None
    return url


def extract_name_from_clinic(clinic_name):
    """Try to split a clinic name into first/last name."""
    name = clinic_name.strip()
    # Remove common prefixes/suffixes
    name = re.sub(r'^(Dr\.?\s*|Dr\.?\s*med\.?\s*|Zahnarztpraxis\s*|Praxis\s*)', '', name, flags=re.I)
    parts = name.split()
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return '', name


async def extract_website_from_detail(ctx, gs_url):
    """Visit a GS detail page and extract the real clinic website URL."""
    try:
        pg = await ctx.new_page()
        await pg.goto(gs_url, wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(2)

        clinic_url = None
        clinic_name = ''
        address = ''

        # Get page title / h1 for name
        h1 = await pg.query_selector('h1')
        if h1:
            clinic_name = (await h1.inner_text()).strip()

        # Get address
        addr = await pg.query_selector('[class*="address"], [class*="adresse"]')
        if addr:
            address = (await addr.inner_text()).strip()

        # Find the "Zur Website" link - usually the most prominent external link
        all_links = await pg.query_selector_all('a[href]')
        candidates = []
        for btn in all_links:
            href = await btn.get_attribute('href')
            if not href or not href.startswith('http'):
                continue
            if 'gelbeseiten' in href.lower():
                continue
            if any(b in href.lower() for b in BAD_URL_FRAGS):
                continue
            text = await btn.inner_text() or ''
            # Score: prefer buttons labelled "Zur Website", "Website", "Homepage"
            score = 0
            text_lower = text.lower()
            if 'website' in text_lower or 'webseite' in text_lower or 'homepage' in text_lower:
                score = 10
            elif 'zur' in text_lower and len(text.strip()) < 30:
                score = 5
            elif href.endswith('.de') or href.endswith('.com') or href.endswith('.net'):
                score = 1
            candidates.append((score, href, text.strip()))

        # Sort by score descending, take highest scoring
        candidates.sort(reverse=True)
        if candidates:
            clinic_url = clean_website(candidates[0][1])
        else:
            # Fallback: any clean URL
            for _, href, _ in candidates:
                c = clean_website(href)
                if c:
                    clinic_url = c
                    break

        await pg.close()
        return clinic_name, address, clinic_url

    except Exception as e:
        return '', '', None


async def extract_impressum_from_clinic(ctx, website_url, clinic_name):
    """Visit a clinic website and extract owner name + personal email from Impressum."""
    try:
        pg = await ctx.new_page()
        await pg.goto(website_url, wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(2)

        impressum_url = None
        vorname, nachname, email = '', '', ''
        impressum_found = False

        # Look for Impressum link
        all_links = await pg.query_selector_all('a[href]')
        impressum_candidates = []
        for btn in all_links:
            href = await btn.get_attribute('href')
            text = (await btn.inner_text() or '').lower()
            if href and any(k in text for k in ['impressum', 'impress', 'legal', 'rechtliches', 'anbieter']):
                if href.startswith('http'):
                    impressum_candidates.append(href)
                elif href.startswith('/'):
                    base = website_url.rstrip('/')
                    impressum_candidates.append(base + href)
        if impressum_candidates:
            impressum_url = impressum_candidates[0]

        # Try common impressum paths
        base = website_url.rstrip('/')
        paths_to_try = [f'{base}/impressum', f'{base}/impressum/', f'{base}/impress', f'{base}/legal',
                        f'{base}/rechtliches', f'{base}/kontakt']
        for path in paths_to_try:
            if not impressum_url:
                try:
                    r = await pg.goto(path, wait_until='domcontentloaded', timeout=10000)
                    if r and r.status < 400:
                        impressum_url = path
                        impressum_found = True
                        break
                except:
                    pass

        if impressum_url and impressum_url != website_url:
            try:
                await pg.goto(impressum_url, wait_until='domcontentloaded', timeout=10000)
                await asyncio.sleep(1.5)
                impressum_found = True
            except:
                pass

        # Extract from page content
        content = await pg.inner_text('body')
        html = await pg.content()

        # Extract emails: look for pattern like name@domain.de but exclude generic
        raw_emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', html)
        emails_found = []
        for e in raw_emails:
            e_lower = e.lower()
            if any(b in e_lower for b in BAD_EMAIL_PATTERNS):
                continue
            if e_lower.startswith('info@') or e_lower.startswith('kontakt@') or e_lower.startswith('praxis@'):
                continue
            emails_found.append(e)

        # Personal email = first non-generic email
        if emails_found:
            email = emails_found[0]

        # Extract owner name from impressum
        # Look for "Inhaber", "Geschäftsführer", "Zahnarzt", patterns
        name_patterns = [
            r'(?:Inhaber[in]?|Inhaberin|Verantwortlich(?:er)?|Gesch[äa]ftsf[üu]hrer[in]?|Zahnarzt[^*]*|Zahnärztin[^*]*)[:\s]+([A-ZÄÖÜ][a-zA-ZÄÖÜäöüß]+(?:\s+[A-ZÄÖÜ][a-zA-ZÄÖÜäöüß]+){1,3})',
            r'(?:Dr\.?\s*(?:med\.?\s*)?(?:dent\.?\s*)?)([A-ZÄÖÜ][a-zA-ZÄÖÜäöüß]+\s+[A-ZÄÖÜ][a-zA-ZÄÖÜäöüß]+)',
            r'(?:Name|Namen)[:\s]+([A-ZÄÖÜ][a-zA-ZÄÖÜäöüß]+\s+[A-ZÄÖÜ][a-zA-ZÄÖÜäöüß]+)',
        ]
        owner_name = ''
        for pat in name_patterns:
            m = re.search(pat, content, re.I)
            if m:
                owner_name = m.group(1).strip()
                break

        if owner_name:
            parts = owner_name.split()
            if len(parts) >= 2:
                vorname, nachname = parts[0], parts[-1]
            else:
                nachname = owner_name

        # Fallback: clinic name split
        if not vorname and clinic_name:
            fn, ln = extract_name_from_clinic(clinic_name)
            if fn:
                vorname = fn
            if ln:
                nachname = ln

        await pg.close()
        return vorname, nachname, email, impressum_found

    except Exception as e:
        return '', '', '', False


async def scrape_city(browser, city, pages=5):
    """Scrape one city: paginate GS listings, get real website URLs."""
    ctx = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        locale='de-DE'
    )
    pg = await ctx.new_page()
    city_results = []
    total_listings = 0

    try:
        city_slug = city.replace(' ', '-').lower()
        # GS search URL format
        search_url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
        await pg.goto(search_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)

        for page_num in range(1, pages + 1):
            if page_num > 1:
                try:
                    # Try pagination via URL
                    next_url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}/seite-{page_num}'
                    await pg.goto(next_url, wait_until='networkidle', timeout=25000)
                    await asyncio.sleep(2)
                except Exception:
                    break

            # Extract all listing detail links
            listing_links = await pg.query_selector_all('a[href*="/gsbiz/"]')
            gs_urls = []
            for a in listing_links:
                href = await a.get_attribute('href')
                if href and '/gsbiz/' in href:
                    full = ('https://www.gelbeseiten.de' + href) if not href.startswith('http') else href
                    gs_urls.append(full)

            gs_urls = list(set(gs_urls))
            total_listings += len(gs_urls)
            print(f'  [{city}] Page {page_num}: {len(gs_urls)} listings')

            for gs_url in gs_urls:
                url_key = gs_url
                if url_key in seen_urls:
                    continue
                seen_urls.add(url_key)

                name, addr, clinic_url = await extract_website_from_detail(ctx, gs_url)
                if clinic_url and clinic_url not in SEEN_WEBSITES:
                    SEEN_WEBSITES.add(clinic_url)
                    city_results.append({
                        'city': city,
                        'gs_url': gs_url,
                        'clinic_name': name,
                        'address': addr,
                        'website': clinic_url
                    })
                    print(f'    + Website: {clinic_url} ({name[:40]})')

                await asyncio.sleep(0.3)

    except Exception as e:
        print(f'  [{city}] Error: {e}')
    finally:
        await ctx.close()

    print(f'  [{city}] Total: {len(city_results)} real websites from {total_listings} listings')
    return city_results


async def main():
    all_results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for city in CITIES:
            print(f'\n>>> Scraping: {city}')
            results = await scrape_city(browser, city, pages=5)
            all_results.extend(results)
            print(f'>>> [{city}] Done. Running total: {len(all_results)}')
            await asyncio.sleep(1)

        await browser.close()

    # Save websites JSON
    with open(WEBSITES_OUT, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f'\n\nSaved {len(all_results)} websites to {WEBSITES_OUT}')

    # Now crawl each website for Impressum + email
    print(f'\n=== Phase 2b: Crawling {len(all_results)} clinic websites for Impressum ===\n')
    final_records = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for i, rec in enumerate(all_results):
            print(f'[{i+1}/{len(all_results)}] Crawling: {rec["website"]}')
            ctx = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
                locale='de-DE'
            )
            vorname, nachname, email, impressum_found = await extract_impressum_from_clinic(
                ctx, rec['website'], rec['clinic_name']
            )
            await ctx.close()

            rec['vorname'] = vorname
            rec['nachname'] = nachname
            rec['email'] = email
            rec['impressum_found'] = impressum_found

            if email:
                print(f'  >>> EMAIL: {email} | {vorname} {nachname}')
            else:
                print(f'  >>> No email found')

            final_records.append(rec)
            await asyncio.sleep(0.5)

        await browser.close()

    # Write final CSV
    csv_path = FINALE_CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['vorname', 'nachname', 'email', 'address', 'website'], delimiter=';')
        writer.writeheader()
        for r in final_records:
            writer.writerow({
                'vorname': r.get('vorname', ''),
                'nachname': r.get('nachname', ''),
                'email': r.get('email', ''),
                'address': r.get('address', ''),
                'website': r.get('website', '')
            })

    print(f'\n\nFinal CSV saved: {csv_path}')
    print(f'Total records: {len(final_records)}')
    print(f'With emails: {sum(1 for r in final_records if r.get("email"))}')
    print(f'With impressum: {sum(1 for r in final_records if r.get("impressum_found"))}')


if __name__ == '__main__':
    asyncio.run(main())
