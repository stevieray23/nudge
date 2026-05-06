#!/usr/bin/env python3
"""
Zahnarzt Email Scraper v3 - uses prosearch API + direct impressum scraping
"""
import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import random
import os
import json
import subprocess
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROSEARCH_SCRIPT = r'C:\Program Files\QClaw\resources\openclaw\config\skills\online-search\scripts\prosearch.cjs'
OUTPUT_DIR = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'google_emails_batch1.csv')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9',
}

SKIP_EMAILS = {
    'info@', 'kontakt@', 'praxis@', 'termine@', 'termin@',
    'service@', 'office@', 'hello@', 'mail@', 'post@',
    'feedback@', 'support@', 'admin@', 'webmaster@',
    'noreply@', 'no-reply@', 'appointment@', 'terminplanung@',
    'kontaktformular@', 'anmeldung@', 'sekretariat@',
    'empfang@', 'rezeption@', 'redaktion@',
}

IMPRESSUM_PATHS = [
    '/impressum', '/impressum/', '/impressum.html',
    '/legal', '/rechtliches', '/kontakt',
]

def prosearch(query):
    """Run prosearch and return list of {url, title, passage}"""
    cmd = ['node', PROSEARCH_SCRIPT, '--keyword=' + query, '--cnt=30']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        if not data.get('success'):
            return []
        return [
            {
                'url': doc.get('url', ''),
                'title': doc.get('title', ''),
                'passage': doc.get('passage', ''),
            }
            for doc in data.get('data', {}).get('docs', [])
            if doc.get('url', '').startswith('http')
        ]
    except Exception as e:
        print(f"    ProSearch error: {e}")
        return []


def extract_urls_from_results(results):
    """Extract and deduplicate URLs from search results"""
    seen = set()
    urls = []
    for r in results:
        url = r.get('url', '')
        if url and url not in seen and url.startswith('http'):
            seen.add(url)
            urls.append(r)
    return urls


def find_impressum_url(base_url):
    """Find Impressum page URL"""
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    
    # Try common paths
    for path in IMPRESSUM_PATHS:
        url = base + path
        try:
            resp = requests.head(url, headers=HEADERS, timeout=5, verify=False, allow_redirects=True)
            if resp.status_code == 200:
                ct = resp.headers.get('Content-Type', '')
                if 'text/html' in ct:
                    return url
        except:
            continue
    return None


def extract_emails(text):
    """Extract personal emails from text"""
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


def extract_dentist_name(text):
    """Extract dentist first and last name"""
    patterns = [
        r'(?:Zahnärztin|Zahnarzt|Dr\.?\s*(?:med\.?dent\.?)?|M\.?Sc\.?)\s+([A-ZÄÖÜ][a-zäöüß\-]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})',
        r'Ihr\s+Zahnarzt\s+(?:in\s+)?(?:[A-ZÄÖÜ][a-zäöüß]+\s+)?([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'Praxisinhaber(?:in)?\s*:?\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'(?:Inhaber|Inhaberin|Betreiber)\s*:?\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)\s*,?\s*(?:Zahnärztin|Zahnarzt|Dr\.?\s*(?:med\.?)?)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if isinstance(m, tuple) and len(m) == 2:
                vorname = m[0].strip()
                nachname = m[1].strip().split()[0]
                if 1 < len(vorname) < 30 and 1 < len(nachname) < 30:
                    return vorname, nachname
            elif isinstance(m, str):
                parts = m.split()
                if len(parts) >= 2:
                    return parts[0], parts[1]
    
    return None, None


def process_practice(url, city):
    """Fetch Impressum and extract data"""
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
        
        vorname, nachname = extract_dentist_name(text)
        
        return {
            'vorname': vorname or '',
            'nachname': nachname or '',
            'email': emails[0],
            'adress': city,
            'website': url,
        }
    except Exception as e:
        return None


def search_city(city):
    """Search for dentist practices in a city using multiple queries"""
    queries = [
        f'zahnarztpraxis {city} impressum',
        f'Zahnarzt {city} impressum E-Mail',
        f'zahnarztpraxis {city} email',
        f'"Zahnarztpraxis" {city} impressum',
        f'zahnaerzte {city} impressum site:.de',
    ]
    
    all_results = []
    for q in queries:
        results = prosearch(q)
        all_results.extend(results)
        time.sleep(0.5)
    
    # Deduplicate
    urls = extract_urls_from_results(all_results)
    return urls


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    cities = [
        'Frankfurt am Main', 'München', 'Köln', 'Hamburg', 'Berlin',
        'Stuttgart', 'Düsseldorf', 'Bremen', 'Leipzig', 'Dresden',
    ]
    
    all_data = []
    
    for city in cities:
        print(f"\n{'='*60}")
        print(f"City: {city}")
        print(f"{'='*60}")
        
        # Search
        print(f"  Searching...", end=' ')
        urls = search_city(city)
        print(f"found {len(urls)} URLs")
        
        # Process each URL
        for i, r in enumerate(urls):
            url = r.get('url', '')
            title = r.get('title', '')[:50]
            print(f"  [{i+1}/{len(urls)}] {title}...", end=' ')
            
            data = process_practice(url, city)
            if data:
                print(f"✓ {data['email']} ({data['vorname']} {data['nachname']})")
                all_data.append(data)
            else:
                print("✗")
            
            time.sleep(random.uniform(0.2, 0.6))
        
        # Save intermediate
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['vorname', 'nachname', 'email', 'adress', 'website'], delimiter=';')
            writer.writeheader()
            for row in all_data:
                writer.writerow(row)
        
        print(f"  City total: {sum(1 for d in all_data if d['adress'] == city)}")
        print(f"  Running total: {len(all_data)}")
    
    print(f"\n{'='*60}")
    print(f"DONE! Total: {len(all_data)} emails")
    print(f"File: {OUTPUT_FILE}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
