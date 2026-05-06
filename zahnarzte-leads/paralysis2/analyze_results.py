import csv

path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\paralysis2\leads_agent2.csv'
rows = []
with open(path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

total = len(rows)
with_email = [r for r in rows if r.get('email', '').strip()]
print(f'Total rows: {total}')
print(f'Rows with email: {len(with_email)}')
print()
print('First 5 rows with emails:')
for r in with_email[:5]:
    print(f"  vorname={r.get('vorname','')}, nachname={r.get('nachname','')}, email={r.get('email','')}")
