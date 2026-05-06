import csv, json
from pathlib import Path
BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

sources = [
    ('zahnarzte_final.csv', 'csv'),
    ('phase2/checkpoint_results.json', 'json'),
    ('v2_batch1.json', 'json'),
    ('v2_batch2.json', 'json'),
    ('v2_batch3.json', 'json'),
    ('leads_batch_1.csv', 'csv'),
    ('leads_batch_2.csv', 'csv'),
    ('leads_batch_3.csv', 'csv'),
    ('leads_batch_4.csv', 'csv'),
    ('leads_batch_5.csv', 'csv'),
    ('leads_batch_6.csv', 'csv'),
    ('paralysis1/leads_agent1.csv', 'csv'),
    ('paralysis2/leads_agent2.csv', 'csv'),
    ('paralysis3/leads_agent3.csv', 'csv'),
    ('paralysis4/leads_agent4.csv', 'csv'),
    ('paralysis5/leads_agent5.csv', 'csv'),
]

total_rows = 0
total_emails = 0
for fname, ftype in sources:
    f = BASE / fname
    if not f.exists():
        print(f'MISSING: {fname}')
        continue
    emails = 0
    rows = 0
    if ftype == 'csv':
        with open(f, 'r', encoding='utf-8') as fh:
            for row in csv.DictReader(fh, delimiter=';'):
                rows += 1
                if row.get('email', '').strip():
                    emails += 1
    else:
        try:
            data = json.load(open(f, 'r', encoding='utf-8'))
            if isinstance(data, list):
                recs = data
                res = []
            else:
                recs = data.get('records', [])
                res = data.get('results', [])
            rows = len(recs)
            if res:
                emails = sum(1 for r in res if isinstance(r, dict) and (r.get('em') or r.get('email')))
            else:
                emails = sum(1 for r in recs if isinstance(r, dict) and r.get('email'))
        except Exception as e:
            print(f'Error {fname}: {e}')
            continue
    total_rows += rows
    total_emails += emails
    print(f'  {fname}: {rows} rows, {emails} emails')

print(f'TOTAL: {total_rows} rows, {total_emails} emails')
