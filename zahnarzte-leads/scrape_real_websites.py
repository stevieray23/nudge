"""
Headless Playwright scraper for Gelbe Seiten Zahnärzte.
Extracts real clinic websites from listing pages by visiting detail pages.
"""
import asyncio
import json
import re
import time
from pathlib import Path
from playwright.async_api import async_playwright

CITIES = [
    'Frankfurt am Main', 'Bremen', 'Essen', 'Bochum', 'Bielefeld', 'Bonn',
    'Münster', 'Mannheim', 'Karlsruhe', 'Augsburg', 'Wiesbaden', 'Mönchengladbach',
    'Gelsenkirchen', 'Braunschweig', 'Aachen', 'Kiel', 'Chemnitz', 'Halle (Saale)',
    'Magdeburg', 'Freiburg im Breisgau', 'Krefeld', 'Mainz', 'Lübeck', 'Erfurt',
    'Dresden', 'Leipzig', 'Nürnberg', 'Stuttgart', 'Düsseldorf', 'Dortmund',
    'Berlin', 'Hamburg', 'Hannover', 'München', 'Köln'
]

OUT_FILE = Path(__file__).parent / 'phase2' / 'real_clinic_websites.json'
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

SEEN_WEBSITES = set()
all_websites = []


def clean_website(url):
    """Remove tracking params and extract real website."""
    if not url:
        return None
    url = url.strip()
    if 'gelbeseiten' in url.lower():
        return None
    # Remove common tracking params
    url = re.sub(r'[?&]utm_[^&]+', '', url)
    url = url.split('?')[0].split('#')[0]
    if url.startswith('//'):
        url = 'https:' + url
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    return url if url.startswith('https://') else f'https://{url}' if url.startswith('http') else None


async def scrape_city(browser, city, pages=5):
    """Scrape one city: paginate through listings and extract real clinic websites."""
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        locale='de-DE'
    )
    page = await context.new_page()
    results = []
    
    # Gelbe Seiten city search URL
    city_slug = city.replace(' ', '+').replace('(', '').replace(')', '')
    search_url = f'https://www.gelbeseiten.de/suche/zahnarzt/{city}'
    
    try:
        await page.goto(search_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        
        for page_num in range(1, pages + 1):
            print(f'  [{city}] Page {page_num}')
            
            # Extract listing links (detail page URLs)
            listing_links = await page.query_selector_all('a[href*="/gsbiz/"]')
            gs_urls = set()
            for a in listing_links:
                href = await a.get_attribute('href')
                if href and '/gsbiz/' in href:
                    full_url = 'https://www.gelbeseiten.de' + href if not href.startswith('http') else href
                    gs_urls.add(full_url)
            
            print(f'    Found {len(gs_urls)} listing links')
            
            # Visit each detail page to extract real clinic website
            for gs_url in gs_urls:
                try:
                    detail_page = await context.new_page()
                    await detail_page.goto(gs_url, wait_until='domcontentloaded', timeout=15000)
                    await asyncio.sleep(1.5)
                    
                    # Look for "Zur Website" or "Website" button -> real clinic URL
                    clinic_url = None
                    
                    # Method 1: Find button with website
                    website_btns = await detail_page.query_selector_all('a[href]')
                    for btn in website_btns:
                        href = await btn.get_attribute('href')
                        text = await btn.inner_text() or ''
                        if href and ('website' in text.lower() or 'homepage' in text.lower() or 'zur webseite' in text.lower()):
                            if 'gelbeseiten' not in href.lower():
                                clinic_url = clean_website(href)
                                break
                    
                    # Method 2: Scan all links for real clinic domains
                    if not clinic_url:
                        all_links = await detail_page.query_selector_all('a[href]')
                        for btn in all_links:
                            href = await btn.get_attribute('href')
                            if href and href.startswith('http') and 'gelbeseiten' not in href.lower():
                                cleaned = clean_website(href)
                                if cleaned and len(cleaned) > 10:
                                    # Prefer non-directory sites
                                    bad = ['facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com', 
                                           'bing.com', 'google.com', 'yahoo.com', 'apple.com', 
                                           'docinsider', 'jimdo', 'webnode', 'wix.com', 'squarespace.com']
                                    if not any(b in cleaned.lower() for b in bad):
                                        clinic_url = cleaned
                                        break
                    
                    # Method 3: Look in page text for URL patterns
                    if not clinic_url:
                        content = await detail_page.content()
                        url_pattern = re.findall(r'https?://(?!www\.gelbeseiten)[^\s<>"\'\)]+\.(de|com|org|net|info)', content)
                        if url_pattern:
                            clinic_url = f'https://{url_pattern[0]}'
                    
                    # Get clinic name from detail page
                    name_el = await detail_page.query_selector('h1')
                    clinic_name = await name_el.inner_text() if name_el else ''
                    
                    # Get address
                    addr_els = await detail_page.query_selector_all('[class*="address"]')
                    address = ''
                    for el in addr_els:
                        text = await el.inner_text()
                        if text and re.search(r'\d{4,5}', text):
                            address = text.strip()
                            break
                    
                    if clinic_url and clinic_url not in SEEN_WEBSITES:
                        SEEN_WEBSITES.add(clinic_url)
                        results.append({
                            'city': city,
                            'gs_url': gs_url,
                            'clinic_name': clinic_name.strip(),
                            'address': address,
                            'website': clinic_url
                        })
                        print(f'    [FOUND] {clinic_name.strip()} -> {clinic_url}')
                    
                    await detail_page.close()
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f'    Error detail page: {e}')
                    continue
            
            # Navigate to next page
            if page_num < pages:
                try:
                    # Try clicking next page button
                    next_btn = await page.query_selector('a[title*="nächste"], a[title*="weiter"], a[rel="next"]')
                    if next_btn:
                        await next_btn.click()
                        await page.wait_for_load_state('networkidle', timeout=20000)
                        await asyncio.sleep(2)
                    else:
                        # Try page number links
                        page_links = await page.query_selector_all('a[href]')
                        for pl in page_links:
                            href = await pl.get_attribute('href')
                            text = await pl.inner_text() or ''
                            if str(page_num + 1) in text and '/seite-' in (href or ''):
                                await pl.click()
                                await page.wait_for_load_state('networkidle', timeout=20000)
                                await asyncio.sleep(2)
                                break
                except Exception as e:
                    print(f'    Next page error: {e}')
                    break
                    
    except Exception as e:
        print(f'  City error [{city}]: {e}')
    finally:
        await context.close()
    
    return results


async def main():
    all_results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for city in CITIES:
            print(f'\nScraping: {city}')
            results = await scrape_city(browser, city, pages=3)
            all_results.extend(results)
            print(f'  Total so far: {len(all_results)}')
            await asyncio.sleep(1)
        
        await browser.close()
    
    # Save
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f'\n\nSaved {len(all_results)} real clinic websites to {OUT_FILE}')


if __name__ == '__main__':
    asyncio.run(main())
