import csv

path = r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\paralysis4\leads_agent4.csv'

with open(path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

total = len(rows)
with_email = [r for r in rows if r.get('email', '').strip()]

print(f'Total rows: {total}')
print(f'Rows with non-empty email: {len(with_email)}')
print()
print('First 5 rows with emails:')
for r in with_email[:5]:
    print(f'  vorname={repr(r.get("vorname",""))}, nachname={repr(r.get("nachname",""))}, email={repr(r.get("email",""))}')
