#!/usr/bin/env python3
"""
Zahnarzte Lead Enrichment - Phase 2
Visits dentist clinic websites from Gelbe Seiten and extracts Impressum data.
"""

import json
import re
import time
import urllib.request
import urllib.parse
import ssl
import sys
from html.parser import HTMLParser

# ─── Setup ────────────────────────────────────────────────────────────────────
BATCH_FILE = r"C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_3_websites.json"
OUTPUT_FILE = r"C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_3_enriched.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.gelbeseiten.de/",
}

IMPRESSUM_PATHS = [
    "/impressum",
    "/impressum/",
    "/impressum.html",
    "/legal",
    "/legal/",
    "/rechtliches",
    "/rechtliches/",
    "/anbieter",
    "/anbieterkennzeichnung",
]

ctx = ssl.create_default_context()

def fetch(url, timeout=15):
    """Fetch a URL and return (html, error)."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            return content, None
    except Exception as e:
        return "", str(e)

class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = {}
        self.current_text = []
        self.in_a = False
        self._pending_href = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            self.in_a = True
            self.current_text = []
            self._pending_href = href
    
    def handle_data(self, data):
        if self.in_a:
            self.current_text.append(data.strip())
    
    def handle_endtag(self, tag):
        if tag == "a" and self.in_a:
            text = " ".join(self.current_text).strip().lower()
            if text and self._pending_href:
                self.links[text] = self._pending_href
            self.in_a = False

def extract_links(html):
    parser = LinkExtractor()
    try:
        parser.feed(html)
    except:
        pass
    return parser.links

def find_clinic_url(gs_html, gs_url):
    """Find the real clinic website from a Gelbe Seiten listing."""
    
    patterns = [
        r'href=["\'](https?://(?!www\.gelbeseiten)[^"\']+)["\'][^>]*>(?:zur |Zur |)?Website',
        r'data-website=["\']([^"\']+)["\']',
        r'"website"\s*:\s*"([^"]+)"',
    ]
    
    for p in patterns:
        m = re.search(p, gs_html, re.IGNORECASE)
        if m:
            url = m.group(1)
            if url and "gelbeseiten" not in url.lower() and url.startswith("http"):
                return url
    
    json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
    for match in re.finditer(json_ld_pattern, gs_html, re.DOTALL):
        try:
            data = json.loads(match.group(1))
            for item in (data if isinstance(data, list) else [data]):
                url = item.get("url", "")
                if url and "gelbeseiten" not in url.lower() and url.startswith("http"):
                    return url
        except:
            pass
    
    url_pattern = r'href=["\'](https?://(?!www\.gelbeseiten)(?!a\.delivery)(?!tags\.)(?!ad13)(?!imagesrv)(?!adfarm)(?!cdn)[^"\']{5,80})["\']'
    for m in re.finditer(url_pattern, gs_html):
        url = m.group(1)
        if any(kw in url.lower() for kw in ["zahnarzt", "zahnaerzt", "praxis", "dr.", "clinic", "kfo"]):
            return url
    
    return None

def extract_impressum(html, base_url):
    """Extract owner name and personal email from Impressum page."""
    result = {
        "found": False,
        "email": "",
        "email_found": False,
        "vorname": "",
        "nachname": "",
        "notes": "",
    }
    
    if not html or len(html) < 200:
        return result
    
    result["found"] = True
    
    # Email extraction
    all_emails = re.findall(r'[\w.\-]+@[\w.\-]+\.[a-zA-Z]{2,}', html)
    seen = set()
    unique_emails = []
    for e in all_emails:
        el = e.lower()
        if el not in seen:
            seen.add(el)
            unique_emails.append(e)
    
    generic_prefixes = [
        "info@", "kontakt@", "service@", "termin@", "booking@",
        "termine@", "rezeption@", "praxis@", "office@", "anmeldung@",
        "mail@", "post@", "hello@", "web@", "admin@", "support@",
        "noreply@", "no-reply@", "datenschutz@", "presse@", "marketing@"
    ]
    
    personal_email = ""
    generic_email = ""
    
    for email in unique_emails:
        el = email.lower()
        is_generic = any(el.startswith(p) for p in generic_prefixes)
        if is_generic:
            if not generic_email:
                generic_email = email
        else:
            if not personal_email:
                personal_email = email
    
    result["email"] = personal_email or generic_email or ""
    result["email_found"] = bool(result["email"])
    
    # Name extraction
    text_only = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    text_only = re.sub(r'<style[^>]*>.*?</style>', ' ', text_only, flags=re.DOTALL)
    text_only = re.sub(r'<[^>]+>', ' ', text_only)
    text_only = re.sub(r'\s+', ' ', text_only)
    
    name_patterns = [
        r'(?:Inhaber(?:in)?|Geschäftsführer(?:in)?|Vertreten durch|Betreiber)[:\s]+(?:Dr\.?\s*(?:med\.?\s*(?:dent\.?)?)?\s*)?([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'\b(?:Dr\.?\s*(?:med\.?\s*(?:dent\.?)?|med\.?)\s+)?([A-ZÄÖÜ][a-zäöüß]{2,})\s+([A-ZÄÖÜ][a-zäöüß]{2,})\b',
        r'(?:Zahnarzt|Zahnärztin|Fachzahnarzt)[^<]{0,50}Dr\.?\s*([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)',
    ]
    
    for pattern in name_patterns:
        m = re.search(pattern, text_only)
        if m:
            vorname = m.group(1).strip()
            nachname = m.group(2).strip()
            if vorname and nachname and len(vorname) > 1 and len(nachname) > 1:
                result["vorname"] = vorname
                result["nachname"] = nachname
                break
    
    return result

def log(msg):
    print(msg)
    sys.stdout.flush()

def main():
    with open(BATCH_FILE, "r", encoding="utf-8") as f:
        batch = json.load(f)
    
    results = []
    total = len(batch)
    emails_found = 0
    
    for i, lead in enumerate(batch, 1):
        log(f"\n[{i}/{total}] {lead['clinic_name']}")
        
        entry = {
            "clinic_name": lead["clinic_name"],
            "address": lead["address"],
            "city": lead["city"],
            "website": lead["website"],
            "vorname": "",
            "nachname": "",
            "email": "",
            "impressum_found": False,
            "email_found": False,
            "notes": "",
        }
        
        gs_html, gs_err = fetch(lead["website"])
        if gs_err:
            log(f"  [!] GS error: {gs_err}")
            entry["notes"] = f"GS fetch error: {gs_err}"
            results.append(entry)
            continue
        
        clinic_url = find_clinic_url(gs_html, lead["website"])
        if not clinic_url:
            log(f"  [!] No clinic URL found on Gelbe Seiten")
            entry["notes"] = "No clinic website found on Gelbe Seiten"
            results.append(entry)
            continue
        
        log(f"  -> Clinic URL: {clinic_url}")
        time.sleep(0.8)
        
        imp_url = ""
        clinic_html = ""
        
        root_html, _ = fetch(clinic_url)
        if root_html:
            clinic_html = root_html
            links = extract_links(root_html)
            
            imp_link = None
            for link_text, link_url in links.items():
                if any(kw in link_text for kw in ["impressum", "impress", "rechtliches", "legal", "anbieter", "angaben"]):
                    imp_link = link_url
                    break
            
            if imp_link:
                if imp_link.startswith("/"):
                    parsed = urllib.parse.urlparse(clinic_url)
                    imp_link = f"{parsed.scheme}://{parsed.netloc}{imp_link}"
                elif not imp_link.startswith("http"):
                    imp_link = urllib.parse.urljoin(clinic_url, imp_link)
                
                imp_html, _ = fetch(imp_link)
                if imp_html:
                    clinic_html = imp_html
                    imp_url = imp_link
                    log(f"  -> Found impressum at: {imp_url}")
        
        if not imp_url:
            parsed = urllib.parse.urlparse(clinic_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            
            for path in IMPRESSUM_PATHS:
                test_url = base + path
                test_html, test_err = fetch(test_url)
                if not test_err and test_html and len(test_html) > 500:
                    clinic_html = test_html
                    imp_url = test_url
                    log(f"  -> Found impressum at: {imp_url}")
                    break
        
        if clinic_html and len(clinic_html) > 200:
            imp_data = extract_impressum(clinic_html, imp_url or clinic_url)
            entry["impressum_found"] = imp_data["found"]
            entry["email_found"] = imp_data["email_found"]
            entry["email"] = imp_data["email"]
            entry["vorname"] = imp_data["vorname"]
            entry["nachname"] = imp_data["nachname"]
            if imp_url:
                entry["notes"] = f"Impressum: {imp_url}"
            
            if imp_data["email_found"]:
                emails_found += 1
                log(f"  [+] EMAIL: {imp_data['email']} | Name: {imp_data['vorname']} {imp_data['nachname']}")
            else:
                log(f"  [-] No personal email | Name: {imp_data['vorname']} {imp_data['nachname']} | Impressum found: {imp_data['found']}")
        else:
            entry["notes"] += "Could not fetch clinic page; "
            log(f"  [!] No clinic content fetched")
        
        results.append(entry)
        time.sleep(0.8)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    log(f"\n{'='*60}")
    log(f"Done! Processed: {total}")
    log(f"Impressum pages found: {sum(1 for r in results if r['impressum_found'])}")
    log(f"Emails found: {emails_found}")
    log(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
