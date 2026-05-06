import json, os
from pathlib import Path

base = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase1')
files = [f for f in base.glob('agent*.json')]
all_records = []
seen = set()
raw_total = 0

for f in sorted(files):
    with open(f, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    raw_total += len(data)
    if isinstance(data, list):
        for r in data:
            key = (r.get('clinic_name','').strip(), r.get('address','').strip())
            if key not in seen and r.get('clinic_name','').strip():
                seen.add(key)
                all_records.append(r)

print(f"Files processed: {len(files)}")
print(f"Raw total records: {raw_total}")
print(f"Deduplicated: {len(all_records)}")

# Save merged
out = base.parent / 'all_leads_merged.json'
with open(out, 'w', encoding='utf-8') as fh:
    json.dump(all_records, fh, ensure_ascii=False, indent=2)
print(f"Saved: {out}")

# Count websites
websites = [r for r in all_records if r.get('website','').strip()]
print(f"Leads with website field: {len(websites)}")
