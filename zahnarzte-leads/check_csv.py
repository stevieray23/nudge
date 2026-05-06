import csv

path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\paralysis1\leads_agent1.csv'
with open(path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print('Total rows:', len(rows))

rows_with_email = [r for r in rows if r.get('email', '').strip()]
print('Rows with email:', len(rows_with_email))

if rows_with_email:
    print('First 5 with email:')
    for r in rows_with_email[:5]:
        print(f'  {r.get("vorname","")} {r.get("nachname","")} | {r.get("email","")}')
else:
    print('No rows with emails found.')
    if rows:
        print('First 3 rows (all columns):')
        for r in rows[:3]:
            print(' ', dict(r))
