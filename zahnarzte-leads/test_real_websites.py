import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

CITIES = ['Frankfurt am Main', 'Bremen', 'Essen']
OUT_FILE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\test_real_websites.json')
SEEN = set()
RESULTS = []


def clean_website(url):
    if not url:
        return None
    url = url.strip()
    if 'gelbeseiten' in url.lower():
        return None
    url = re.sub(r'[?&]utm_[^&]+', '', url)
    url = url.split('?')[0].split('#')[0]
    if url.startswith('//'):
        url = 'https:' + url
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    return url if url.startswith('https://') else f'https://{url}' if url.startswith('http') else None


async def scrape_city(browser, city, pages=2):
    ctx = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        locale='de-DE'
    )
    pg = await ctx.new_page()
    results = []
    try:
        await pg.goto(
            f'https://www.gelbeseiten.de/suche/zahnarzt/{city}',
            wait_until='networkidle',
            timeout=30000
        )
        await asyncio.sleep(2)
        print(f'[{city}] Page loaded')

        links = await pg.query_selector_all('a[href*="/gsbiz/"]')
        gs_urls = set()
        for a in links:
            href = await a.get_attribute('href')
            if href and '/gsbiz/' in href:
                full = ('https://www.gelbeseiten.de' + href) if not href.startswith('http') else href
                gs_urls.add(full)

        print(f'[{city}] {len(gs_urls)} listing links found')
        visited = 0
        for gs_url in list(gs_urls):
            if visited >= 15:
                break
            visited += 1
            try:
                dp = await ctx.new_page()
                await dp.goto(gs_url, wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(1.5)

                all_links = await dp.query_selector_all('a[href]')
                clinic_url = None
                for btn in all_links:
                    href = await btn.get_attribute('href')
                    if href and href.startswith('http') and 'gelbeseiten' not in href.lower():
                        cleaned = clean_website(href)
                        bad = ['facebook.com', 'instagram.com', 'linkedin.com', 'bing.com',
                               'google.com', 'yahoo.com', 'apple.com', 'docinsider', 'jimdo', 'webnode']
                        if cleaned and not any(b in cleaned.lower() for b in bad):
                            clinic_url = cleaned
                            break

                nm = await dp.query_selector('h1')
                name = (await nm.inner_text()) if nm else ''

                if clinic_url and clinic_url not in SEEN:
                    SEEN.add(clinic_url)
                    results.append({'city': city, 'clinic_name': name.strip(), 'website': clinic_url})
                    print(f'  FOUND: {name.strip()} -> {clinic_url}')

                await dp.close()
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f'  Error on {gs_url}: {e}')
                continue

    except Exception as e:
        print(f'[{city}] Error: {e}')
    finally:
        await ctx.close()

    return results


async def main():
    global RESULTS
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        for city in CITIES:
            r = await scrape_city(b, city, pages=2)
            RESULTS.extend(r)
            print(f'[TOTAL so far: {len(RESULTS)}]')
        await b.close()

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=2)
    print(f'\nSaved {len(RESULTS)} real clinic websites to {OUT_FILE}')


if __name__ == '__main__':
    asyncio.run(main())
