import json
from pathlib import Path
BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
for f in sorted(BASE.glob('v2_batch*.json')):
    d = json.load(open(f, 'r', encoding='utf-8'))
    recs = d.get('records', [])
    res = d.get('results', [])
    emails_found = [r.get('em') or r.get('email') or '' for r in res]
    good = [e for e in emails_found if e]
    print(f.name)
    print(f'  Records: {len(recs)}, Emails found: {len(good)}')
    for e in good[:5]:
        print(f'    {e}')
