import json
from pathlib import Path

base = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads')
merged = base / 'all_leads_merged.json'
out_dir = base / 'phase2'

with open(merged, 'r', encoding='utf-8') as f:
    all_leads = json.load(f)

# Leads WITH websites (have something to crawl)
with_websites = [r for r in all_leads if r.get('website','').strip() and r['website'].strip() not in ('https://www.gelbeseiten.de', '')]
print(f"With real websites: {len(with_websites)}")

# Leads WITHOUT websites (need lookup)
without_websites = [r for r in all_leads if r.get('website','').strip() == '' or r['website'].strip() == 'https://www.gelbeseiten.de']
print(f"Without websites (need lookup): {len(without_websites)}")

# Split into 5 batches
batch_size = (len(with_websites) + 4) // 5
batches = []
for i in range(5):
    batch = with_websites[i*batch_size : (i+1)*batch_size]
    batches.append(batch)
    print(f"Batch {i+1}: {len(batch)} leads")

# Save batches
for i, batch in enumerate(batches):
    out = out_dir / f'batch_{i+1}_websites.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"Saved batch {i+1}: {out}")

# Save lookup-needed list
lookup_out = out_dir / 'batch_lookup_needed.json'
with open(lookup_out, 'w', encoding='utf-8') as f:
    json.dump(without_websites, f, ensure_ascii=False, indent=2)
print(f"Saved lookup-needed ({len(without_websites)} leads): {lookup_out}")
