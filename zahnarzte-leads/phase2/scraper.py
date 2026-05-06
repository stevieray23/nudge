#!/usr/bin/env python3
"""
Zahnarzt (Dentist) Email Scraper
Searches Google for dentist practices in German cities, visits Impressum pages,
and extracts personal emails, dentist names, and practice info.
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import random
import os
from urllib.parse import urljoin, urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'de-DE,de;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
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

# Common Impressum page paths
IMPRESSUM_PATHS = [
    '/impressum',
    '/impressum.html',
    '/impressum.php',
    '/legal',
    '/rechtliches',
    '/kontakt',
    '/about',
    '/about-us',
    '/ueber-uns',
]

# Generic email patterns to skip
SKIP_EMAILS = {
    'info@', 'kontakt@', 'praxis@', 'termine@', 'termin@',
    'service@', 'office@', 'hello@', 'post@', 'mail@',
    'feedback@', 'support@', 'admin@', 'webmaster@', 'no-reply@',
    'noreply@', 'appointment@', 'terminplanung@',
}

def search_google(practice_url):
    """Try to get Google cached version of a site if direct fetch fails"""
    try:
        # Try Google cache
        cache_url = f'https://webcache.googleusercontent.com/search?q=cache:{practice_url}'
        resp = requests.get(cache_url, headers=HEADERS, timeout=10, verify=False, allow_redirects=True)
        if resp.status_code == 200 and 'impressum' in resp.text.lower():
            return resp.text
    except:
        pass
    return None

def find_impressum_url(base_url):
    """Find the Impressum page URL"""
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    
    # Try common paths
    for path in IMPRESSUM_PATHS:
        url = urljoin(base, path)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8, verify=False, allow_redirects=True)
            if resp.status_code == 200:
                content_type = resp.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    return url
        except:
            continue
    return None

def extract_emails(text):
    """Extract email addresses from text, filtering generic ones"""
    # Find all email-like patterns
    email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    
    personal_emails = []
    for email in emails:
        email_lower = email.lower()
        # Filter out generic emails
        if any(email_lower.startswith(skip) for skip in SKIP_EMAILS):
            continue
        # Filter out very long emails (likely spam traps)
        if len(email) > 60:
            continue
        personal_emails.append(email.lower())
    
    return list(set(personal_emails))

def extract_dentist_names(text):
    """Try to extract dentist first and last name"""
    # Look for patterns like "Zahnarzt Vorname Nachname" or "Dr. Vorname Nachname"
    patterns = [
        r'(?:Zahnärztin|Zahnarzt|Dr\.?\s*(?:med\.?)?)\s+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})',
        r'(?:Ihr\s+)?Zahnarzt(?:in)?\s+(?:Frankfurt|München|Köln|Hamburg|Berlin|Stuttgart|Düsseldorf|Bremen|Leipzig|Dresden)?\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'Praxisinhaber(?:in)?\s*:?\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'MSc\s+([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'Dr\.?\s*(?:med\.?)?\s+([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the first match
            m = matches[0]
            if len(m) == 2:
                return m[0], m[1]
            elif len(m) == 1 and isinstance(m[0], str):
                parts = m[0].split()
                if len(parts) >= 2:
                    return parts[0], ' '.join(parts[1:])
    
    return None, None

def process_impressum(impressum_url, practice_url, city):
    """Process an Impressum page and extract data"""
    try:
        resp = requests.get(impressum_url, headers=HEADERS, timeout=12, verify=False)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Also get raw text from body if available
        body = soup.find('body')
        if body:
            text = body.get_text(separator=' ', strip=True)
        
        emails = extract_emails(text)
        
        if not emails:
            return None
        
        # Get dentist name
        vorname, nachname = extract_dentist_names(text)
        
        # If no structured name found, try to get it from title
        if not vorname:
            title = soup.find('title')
            if title:
                vorname, nachname = extract_dentist_names(title.get_text())
        
        return {
            'vorname': vorname or '',
            'nachname': nachname or '',
            'email': emails[0] if emails else '',
            'adress': city,
            'website': practice_url,
            'all_emails': ';'.join(emails),
        }
    except Exception as e:
        print(f"  Error processing {impressum_url}: {e}")
        return None

def get_google_results(city, page=0):
    """Get Google search results for a city"""
    query = f'site:.de Zahnarztpraxis impressum {city}'
    start = page * 10
    url = f'https://www.google.com/search?q={requests.utils.quote(query)}&num=10&start={start}'
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        results = []
        for item in soup.select('div.g'):
            link_elem = item.select_one('a')
            if link_elem:
                href = link_elem.get('href', '')
                title_elem = item.select_one('h3')
                title = title_elem.get_text() if title_elem else ''
                
                if href and href.startswith('http'):
                    # Skip Google results, cached links, etc.
                    if 'google.com' not in href and 'webcache' not in href:
                        results.append({'url': href, 'title': title})
        
        return results
    except Exception as e:
        print(f"  Error searching Google for {city}: {e}")
        return []

def process_city(city):
    """Process a single city - search and scrape"""
    print(f"\n{'='*60}")
    print(f"Processing city: {city}")
    print(f"{'='*60}")
    
    results = []
    
    # Get results from first 3 pages
    for page in range(3):
        print(f"  Page {page+1}...", end=' ')
        page_results = get_google_results(city, page)
        print(f"found {len(page_results)} results")
        results.extend(page_results)
        time.sleep(random.uniform(1.5, 3.0))
    
    # Deduplicate by URL
    seen = set()
    unique_results = []
    for r in results:
        if r['url'] not in seen:
            seen.add(r['url'])
            unique_results.append(r)
    
    print(f"  Total unique URLs: {len(unique_results)}")
    
    city_data = []
    for i, result in enumerate(unique_results):
        print(f"  [{i+1}/{len(unique_results)}] {result['url'][:80]}...", end=' ')
        
        # Find impressum page
        impressum_url = find_impressum_url(result['url'])
        
        if impressum_url:
            print(f"Impressum found. ", end='')
            data = process_impressum(impressum_url, result['url'], city)
            if data:
                print(f"EMAIL: {data['email']}")
                city_data.append(data)
            else:
                print("No email found")
        else:
            print("No Impressum page found")
        
        time.sleep(random.uniform(0.5, 1.5))
    
    print(f"  City total: {len(city_data)} emails")
    return city_data

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_data = []
    
    for city in CITIES:
        city_data = process_city(city)
        all_data.extend(city_data)
        
        # Save intermediate results
        save_results(all_data)
        print(f"\n  Running total: {len(all_data)} emails")
    
    print(f"\n{'='*60}")
    print(f"DONE! Total emails collected: {len(all_data)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print(f"{'='*60}")
    
    save_results(all_data)

def save_results(data):
    """Save results to CSV"""
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['vorname', 'nachname', 'email', 'adress', 'website'], delimiter=';')
        writer.writeheader()
        for row in data:
            writer.writerow({
                'vorname': row.get('vorname', ''),
                'nachname': row.get('nachname', ''),
                'email': row.get('email', ''),
                'adress': row.get('adress', ''),
                'website': row.get('website', ''),
            })

if __name__ == '__main__':
    main()
