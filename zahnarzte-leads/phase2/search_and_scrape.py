#!/usr/bin/env python3
"""
Zahnarzt Email Scraper - v2
Uses multiple search strategies and direct dentist directory access.
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import random
import os
from urllib.parse import urljoin, urlparse, quote
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
}

CITIES = [
    'Frankfurt am Main',
    'München',
    'Köln',
    'Hamburg',
    'Berlin',
    'Stuttgart',
    'Düsseldorf',
    'Bremen',
    'Leipzig',
    'Dresden',
]

OUTPUT_DIR = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'google_emails_batch1.csv')

SKIP_EMAILS = {
    'info@', 'kontakt@', 'praxis@', 'termine@', 'termin@',
    'service@', 'office@', 'hello@', 'mail@', 'post@',
    'feedback@', 'support@', 'admin@', 'webmaster@',
    'noreply@', 'no-reply@', 'appointment@', 'terminplanung@',
    'kontaktformular@', 'anmeldung@', 'sekretariat@',
    'empfang@', 'rezeption@',
}

IMPRESSUM_PATHS = [
    '/impressum', '/impressum.html', '/impressum.php',
    '/legal', '/rechtliches', '/kontakt', '/about',
    '/ueber-uns', '/ueber_uns', '/impressum/',
]


def search_duckduckgo(city, page=0):
    """Search DuckDuckGo HTML version"""
    query = f'site:.de "impressum" "zahnarztpraxis" {city}'
    offset = page * 10
    url = f'https://duckduckgo.com/html/?q={quote(query)}&s={(offset // 10) * 10}'
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        
        # DuckDuckGo HTML results
        for item in soup.select('.result'):
            link = item.select_one('.result__a')
            if link and link.get('href'):
                href = link.get('href', '')
                title = link.get_text(strip=True)
                if href.startswith('http') and 'duckduckgo' not in href:
                    results.append({'url': href, 'title': title})
        
        return results
    except Exception as e:
        print(f"    DDG error: {e}")
        return []


def search_serpapi(city, page=0):
    """Try using SerpAPI-style Google scraping via textise"""
    # This is a fallback - try textise
    query = f'site:.de zahnarztpraxis impressum {city}'
    url = f'https://www.google.com/search?q={quote(query)}&num=10&start={page * 10}&hl=de&lr=lang_de'
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        
        for item in soup.select('div.g'):
            link_elem = item.select_one('a')
            if link_elem:
                href = link_elem.get('href', '')
                title_elem = item.select_one('h3')
                title = title_elem.get_text() if title_elem else ''
                if href.startswith('/url?q='):
                    url_match = re.search(r'/url\?q=([^&]+)', href)
                    if url_match:
                        actual_url = requests.utils.unquote(url_match.group(1))
                        if actual_url.startswith('http') and 'google.com' not in actual_url:
                            results.append({'url': actual_url, 'title': title})
        
        return results
    except Exception as e:
        print(f"    Google error: {e}")
        return []


def search_bing(city, page=0):
    """Search Bing"""
    query = f'site:.de "impressum" "zahnarztpraxis" {city}'
    offset = page * 10
    url = f'https://www.bing.com/search?q={quote(query)}&first={offset + 1}&setlang=de'
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        
        # Try multiple selectors
        for item in soup.find_all('li', class_=re.compile('b_')):
            link = item.find('a')
            if link and link.get('href'):
                href = link.get('href', '')
                if href.startswith('http') and 'bing.com' not in href:
                    title = link.get_text(strip=True)
                    results.append({'url': href, 'title': title})
        
        return results
    except Exception as e:
        print(f"    Bing error: {e}")
        return []


def search_google_simple(city, page=0):
    """Simple Google search with various user agents"""
    query = f'site:.de zahnarztpraxis impressum {city}'
    url = f'https://www.google.com/search?q={quote(query)}&num=10&start={page * 10}'
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    ]
    
    headers = dict(HEADERS)
    headers['User-Agent'] = random.choice(user_agents)
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        
        for item in soup.select('div.g'):
            link_elem = item.select_one('a')
            if link_elem:
                href = link_elem.get('href', '')
                title_elem = item.select_one('h3')
                title = title_elem.get_text() if title_elem else ''
                if href.startswith('/url?q='):
                    url_match = re.search(r'/url\?q=([^&]+)', href)
                    if url_match:
                        actual_url = requests.utils.unquote(url_match.group(1))
                        if actual_url.startswith('http') and 'google.com' not in actual_url:
                            results.append({'url': actual_url, 'title': title})
        
        return results
    except Exception as e:
        return []


def search_directories(city):
    """Try German dentist directories"""
    # dentist.at is a directory
    city_slug = city.lower().replace('ü', 'ue').replace('ö', 'oe').replace('ä', 'ae').replace('ß', 'ss').replace(' ', '-')
    url = f'https://www.zahnarzt.at/{city_slug}/'
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = []
            for a in soup.select('a[href*="/zahnarzt/"]'):
                href = a.get('href', '')
                if href.startswith('http'):
                    results.append({'url': href, 'title': a.get_text(strip=True)})
            return results[:30]
    except:
        pass
    return []


def find_impressum_url(base_url):
    """Find Impressum page URL"""
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    
    for path in IMPRESSUM_PATHS:
        url = urljoin(base, path)
        try:
            resp = requests.head(url, headers=HEADERS, timeout=6, verify=False, allow_redirects=True)
            if resp.status_code == 200:
                ct = resp.headers.get('Content-Type', '')
                if 'text/html' in ct:
                    return url
        except:
            continue
    
    # Try to find a link on the homepage
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=8, verify=False)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                if 'impressum' in href or 'impressum' in text:
                    full_url = urljoin(base, link.get('href'))
                    return full_url
    except:
        pass
    
    return None


def extract_emails(text):
    """Extract email addresses"""
    email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    
    personal = []
    for email in emails:
        el = email.lower()
        if any(el.startswith(s) for s in SKIP_EMAILS):
            continue
        if len(email) > 65:
            continue
        personal.append(email.lower())
    
    return list(set(personal))


def extract_dentist_name(text, url):
    """Extract dentist's name from text"""
    patterns = [
        r'(?:Zahnärztin|Zahnarzt|Dr\.?\s*(?:med\.?)?|M\.?Sc\.?)\s+([A-ZÄÖÜ][a-zäöüß\-]+)\s+([A-ZÄÖÜ][a-zäöüß\-\s]+?)(?:\s|,|$)',
        r'Ihr\s+Zahnarzt\s+(?:in\s+)?(?:[A-ZÄÖÜ][a-zäöüß]+\s+)?([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'Praxisinhaber(?:in)?\s*:?\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)\s+Zahnärzt(?:in|e)',
        r'angestellt(?:er)?\s+Zahnarzt\s+([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if len(m) == 2:
                vorname = m[0].strip()
                nachname = m[1].strip().split()[0]
                if len(vorname) > 1 and len(nachname) > 1:
                    return vorname, nachname
    
    return None, None


def process_practice(url, city):
    """Process a single practice - find impressum and extract data"""
    # Find impressum
    impressum_url = find_impressum_url(url)
    if not impressum_url:
        return None
    
    try:
        resp = requests.get(impressum_url, headers=HEADERS, timeout=12, verify=False)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        body = soup.find('body') or soup
        text = body.get_text(separator=' ', strip=True)
        
        emails = extract_emails(text)
        if not emails:
            return None
        
        vorname, nachname = extract_dentist_name(text, url)
        
        return {
            'vorname': vorname or '',
            'nachname': nachname or '',
            'email': emails[0],
            'adress': city,
            'website': url,
        }
    except Exception as e:
        return None


def search_all_methods(city, page=0):
    """Try all search methods"""
    # Try Google first
    results = search_google_simple(city, page)
    print(f"    Google: {len(results)} results")
    
    if not results:
        results = search_bing(city, page)
        print(f"    Bing: {len(results)} results")
    
    if not results:
        results = search_duckduckgo(city, page)
        print(f"    DDG: {len(results)} results")
    
    return results


def process_city(city):
    """Process a single city"""
    print(f"\n{'='*60}")
    print(f"City: {city}")
    print(f"{'='*60}")
    
    all_results = []
    
    # Get results from multiple pages and methods
    for page in range(3):
        print(f"  Page {page+1}...", end=' ')
        
        results = search_all_methods(city, page)
        all_results.extend(results)
        print(f"cumulative: {len(all_results)}")
        
        if len(results) == 0:
            time.sleep(2)
        else:
            time.sleep(random.uniform(1, 2))
    
    # Deduplicate
    seen = set()
    unique = []
    for r in all_results:
        if r['url'] not in seen:
            seen.add(r['url'])
            unique.append(r)
    
    print(f"  Unique URLs: {len(unique)}")
    
    city_data = []
    for i, result in enumerate(unique):
        print(f"  [{i+1}/{len(unique)}] {result['url'][:70]}...", end=' ')
        
        data = process_practice(result['url'], city)
        if data:
            print(f"✓ EMAIL: {data['email']} ({data['vorname']} {data['nachname']})")
            city_data.append(data)
        else:
            print("✗")
        
        time.sleep(random.uniform(0.3, 0.8))
    
    print(f"  City total: {len(city_data)}")
    return city_data


def save_results(data, filename):
    """Save to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['vorname', 'nachname', 'email', 'adress', 'website'], delimiter=';')
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_data = []
    
    for city in CITIES:
        city_data = process_city(city)
        all_data.extend(city_data)
        
        save_results(all_data, OUTPUT_FILE)
        print(f"  Running total: {len(all_data)} emails saved")
    
    print(f"\n{'='*60}")
    print(f"DONE! Total: {len(all_data)} emails")
    print(f"File: {OUTPUT_FILE}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
