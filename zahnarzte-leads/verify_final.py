import csv, re
from pathlib import Path
from collections import Counter

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
with open(BASE / 'ZAHNARZTE_LEADS_FINAL.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f, delimiter=';'))

print(f'Total: {len(rows)} leads')
print()

# Check for corrupt/bad emails
BAD_EMAILS = {'favicon','no-reply','noreply','example','test'}
corrupt = [r for r in rows if any(x in r['email'].lower() for x in ['.png','.jpg','.webp','@2x','favicon','data:'])]
print(f'Corrupt (image filenames in email): {len(corrupt)}')
for r in corrupt:
    print(f'  REMOVE: {r["email"]}')

# Stats
named_local = [r for r in rows if '.' in r['email'].lower().split('@')[0] or '-' in r['email'].lower().split('@')[0] or r['email'].lower().split('@')[0].startswith('dr.')]
named_personal = [r for r in rows if r['nachname'] and len(r['nachname']) >= 3]
print(f'\nNamed-local (email has . or -): {len(named_local)}')
print(f'With nachname (3+ chars): {len(named_personal)}')

# Domain breakdown
domains = Counter(r['email'].lower().split('@')[1] for r in rows)
print(f'\nDomain breakdown (top 20):')
for d, n in domains.most_common(20):
    print(f'  {d}: {n}')

# Top quality sample: real .de personal emails
print('\nTop quality: personal email + .de domain')
count = 0
for r in rows:
    em = r['email'].lower()
    local, domain = em.split('@')
    is_personal = '.' in local or '-' in local or local.startswith('dr.')
    if domain.endswith('.de') and is_personal and r['nachname'] and len(r['nachname']) >= 3:
        vn = r['vorname'] or ''; ln = r['nachname'] or ''
        ws = r['website'][:55] if r['website'] else ''
        print(f'  {vn} {ln} | {em} | {ws}')
        count += 1
        if count >= 25: break

# Write clean CSV without corrupt rows
clean = [r for r in rows if not any(x in r['email'].lower() for x in ['.png','.jpg','.webp','@2x','favicon','data:'])]
out = BASE / 'ZAHNARZTE_LEADS_FINAL.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['vorname','nachname','email','adress','website'], delimiter=';')
    w.writeheader(); w.writerows(clean)
print(f'\nWrote {len(clean)} clean leads to {out}')
