import json
from pathlib import Path
BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
all_listings = []
for f in ['gs_batch_a.json','gs_batch_b.json','gs_batch_c.json']:
    p = BASE / f
    if p.exists():
        d = json.load(open(p, encoding='utf-8'))
        if isinstance(d, list):
            print(f'{f}: {len(d)} items (list format)')
            all_listings.extend(d)
        elif isinstance(d, dict):
            for city, val in d.items():
                if isinstance(val, dict):
                    listings = val.get('listings', [])
                    for l in listings:
                        l['city'] = city
                    all_listings.extend(listings)
                    print(f'{f}[{city}]: {len(listings)} listings')
                elif isinstance(val, list):
                    all_listings.extend(val)
                    print(f'{f}[{city}]: {len(val)} listings (list)')
print(f'\nTotal listings: {len(all_listings)}')
if all_listings:
    print('Sample:')
    for l in all_listings[:5]:
        print(f'  {l}')
