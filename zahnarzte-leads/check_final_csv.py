import csv
with open(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\zahnarzte_final.csv','r',encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    rows = list(reader)
total = len(rows)
emails = [r for r in rows if r.get('email','').strip()]
print(f'Total rows: {total}')
print(f'Rows with clean email: {len(emails)}')
print('Sample emails:')
for r in emails[:8]:
    vn = r.get('vorname','')
    nn = r.get('nachname','')
    em = r.get('email','')
    ws = r.get('website','')
    print(f'  {vn} {nn} | {em} | {ws}')
