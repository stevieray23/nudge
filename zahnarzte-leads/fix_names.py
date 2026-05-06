"""
Fix names in FINAL_LEADS_v2.csv by crawling Impressum pages.
Uses existing website URLs to extract real owner/dentist names.
"""
import csv, re, json, asyncio, httpx
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
IN = BASE / 'FINAL_LEADS_v2.csv'
OUT = BASE / 'ZAHNARZTE_LEADS_FINAL.csv'

HDRS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'de-DE,de;q=0.9',
}

async def get_impressum_name(client, url):
    """Try to extract dentist/owner name from Impressum page."""
    if not url or not url.startswith('http'): return ''
    base = url.rstrip('/')
    paths = ['/impressum','/impressum/','/impress','/legal','/rechtliches']
    for path in paths:
        try:
            r = await client.get(base + path, timeout=httpx.Timeout(12.0, connect=6.0),
                                  follow_redirects=True, headers=HDRS)
            if r.status_code == 200 and len(r.text) > 500:
                html = r.text
                # Pattern 1: "Inhaber: Dr. Vorname Nachname" (most common)
                m = re.search(r'(?:Inhaber[in]?|Betreiber[in]?|Verantwortlich[erin]?|Geschäftsführer[in]?|'
                              r'Dentist[in]?|Zahnärzt[in]?)\s*[:\.]?\s*(Dr\.?\s*)?([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+)',
                              html, re.I)
                if m: return m.group(2).strip()
                # Pattern 2: "Dr. Vorname Nachname" standalone
                m = re.search(r'(?<![a-zäöüß])(Dr\.?\s+(?:med\.?\s*)?[A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)',
                              html, re.I)
                if m: return m.group(0).strip()
                # Pattern 3: "Vorname Nachname" with title removal
                m = re.search(r'(?:Praxisinhaber[in]?|Anschrift\s*\n?\s*)(Dr\.?\s*)?'
                              r'([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)', html, re.I)
                if m: return m.group(2).strip()
                # Pattern 4: just two capitalized words on a line (risky but useful)
                lines = re.findall(r'^([A-ZÄÖÜ][a-zäöüß\-]+(?:\s+[A-ZÄÖÜ][a-zäöüß\-]+){1,3})$', html, re.M)
                for line in lines:
                    w = line.split()
                    if len(w) == 2 and len(w[0]) > 1 and len(w[1]) > 2:
                        return line
        except: pass
    return ''

async def fix_names():
    # Load existing rows
    with open(IN, encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter=';'))
    print(f'Loaded {len(rows)} rows')

    # Find rows that need fixing (name is empty or placeholder)
    BAD_NAMES = {'ihres','vertrauens','nan','none','undefined','Ihres','Vertrauens',
                 'None','nan','anfrage','anmeldung','abrechnung'}
    needs_fix = []
    for i, r in enumerate(rows):
        vn = r.get('vorname','').strip().lower()
        ln = r.get('nachname','').strip().lower()
        if vn in BAD_NAMES or ln in BAD_NAMES or not vn:
            needs_fix.append(i)

    print(f'Need to fix: {len(needs_fix)} rows')
    if not needs_fix:
        # All good, just copy to OUT
        with open(OUT, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
            w.writeheader()
            w.writerows(rows)
        print(f'All names OK. Saved {len(rows)} to {OUT}')
        return

    # Crawl Impressum for missing names (limit to 100 to stay fast)
    limit = min(len(needs_fix), 100)
    SEM = asyncio.Semaphore(20)

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0),
                                   limits=httpx.Limits(max_connections=40)) as client:
        for idx in range(limit):
            i = needs_fix[idx]
            url = rows[i].get('website','')
            if not url: continue
            async with SEM:
                name = await get_impressum_name(client, url)
                if name:
                    parts = name.split()
                    rows[i]['vorname'] = parts[0] if parts else ''
                    rows[i]['nachname'] = parts[-1] if len(parts) > 1 else name
                    print(f'  Fixed: {rows[i]["vorname"]} {rows[i]["nachname"]} <- {url}')
            await asyncio.sleep(0.2)

    # Save
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
        w.writeheader()
        w.writerows(rows)
    print(f'\nSaved {len(rows)} rows to {OUT}')
    fixed = sum(1 for i in needs_fix[:limit] if rows[i].get('vorname','').strip().lower() not in BAD_NAMES)
    print(f'Fixed {fixed}/{limit} names')

asyncio.run(fix_names())
