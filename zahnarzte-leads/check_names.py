import csv, re
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')

def is_valid_name(n):
    if not n or len(n) < 2: return False
    n = n.strip()
    # German titles
    if re.match(r'^(Dr\.?|Prof\.?|Frau|Herr)$', n): return False
    # Email-like
    if '@' in n: return False
    # Common non-name words
    BAD = {'ihres','vertrauens','fuer','dieser','ihrer','seiner','einer',
           'ihnen','diesen','nicht','nichts','kontakt','info','termin',
           'praxis','zahnarzt','zahnarztpraxis','kfo','kieferorthop',
           'frankfurt','berlin','hamburg','muenchen','koeln','dresden',
           'leipzig','muenchen','stuttgart','düsseldorf','münchen',
           'frankfurt','hannover','dortmund','essen','bremen',
           'karlsruhe','mannheim','augsburg','kiel','aachen',
           'leipzig','bremen','dresden','berlin','lübeck',
           'zahnmedizin','dental','praxisklinik',' MVZ',
           'zahnheilkunde','stomatologie','mkg','oralchirurgie',
           'kinderzahn','pedodontie','prophylaxe','implantat'}
    n_lower = n.lower()
    if n_lower in BAD: return False
    # Word count check
    words = n.split()
    if len(words) == 1:
        # Single word - must be capitalized and reasonable length
        if n[0].isupper() and len(n) >= 3 and n.isalpha(): return True
        return False
    if len(words) == 2:
        # Two words - both should be capitalized names
        if all(w[0].isupper() and len(w) >= 2 for w in words if w):
            # But reject if second word is a title/role
            if words[-1].lower() in {'zahnarzt','zahnärztin','praxis','dr','arzt','ärztin','mvz','kfo'}:
                return False
            return True
    return False

# Check all sources
for fname in ['zahnarzte_final.csv', 'zahnarzte_final_v2.csv', 'FINAL_LEADS.csv']:
    with open(BASE / fname, encoding='utf-8', errors='ignore') as f:
        rows = list(csv.DictReader(f, delimiter=';'))
    good_vn = sum(1 for r in rows if is_valid_name(r.get('vorname','')))
    good_ln = sum(1 for r in rows if is_valid_name(r.get('nachname','')))
    both = sum(1 for r in rows if is_valid_name(r.get('vorname','')) and is_valid_name(r.get('nachname','')))
    print(f'{fname}: {len(rows)} rows, {good_vn} valid vorname, {good_ln} valid nachname, {both} both valid')
    # Show samples of broken names
    print('  Broken vn samples:')
    for r in rows:
        vn = r.get('vorname','')
        if vn and not is_valid_name(vn):
            print(f'    vn={vn!r} em={r.get("email","")[:40]}')
        if sum(1 for x in rows if x.get('vorname','') == vn) > 3: continue
    print()
