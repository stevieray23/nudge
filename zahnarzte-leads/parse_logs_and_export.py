"""
Parse the crawl logs to extract emails found, cross-reference with all_real_websites.json
to get clinic names, then export clean CSV.
"""
import re
import csv
import json
from pathlib import Path

BASE = Path(r'C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2')
WEBSITES_FILE = BASE / 'all_real_websites.json'
OUT_CSV = BASE.parent / 'zahnarzte_final.csv'

# Load all real websites
with open(WEBSITES_FILE, 'r', encoding='utf-8') as f:
    websites = json.load(f)

# Build URL -> website record lookup
url_to_record = {}
for w in websites:
    url_to_record[w['website']] = w
    # Also handle with/without trailing slash
    url_stripped = w['website'].rstrip('/')
    url_to_record[url_stripped] = w

print(f"Loaded {len(websites)} websites")

# The log output from the crawl - extract emails found per website
# Format: [N/1254] Crawling: https://www.xxx.de
#         >>> EMAIL: email | context
#         >>> No email found

# Parse from the log output (reconstructed from memory)
# We'll read the process log
log_entries = []

# Extract from the known crawl order
# The crawl went through websites in all_results order
# We can reconstruct from the log output shown in the session

# From the log output: parse EMAIL lines and their URLs
# The log format was:
# [N/1254] Crawling: https://URL
# >>> EMAIL: email | context
# OR
# >>> No email found

# From the session log, extract all EMAIL results
# We'll hardcode the known EMAIL results from the full log output

email_results = {
    # URL: email
}

# From the full crawl log output:
# Format: [N/1254] Crawling: URL
# >>> EMAIL: email | context

# Read the actual log from the process session
# We need to parse the log output. Let me check if there's a saved log.

import os
log_files = []
for f in os.listdir(BASE.parent):
    if 'log' in f.lower() or 'scrape' in f.lower():
        log_files.append(f)
print("Log/scrape files:", log_files)

print("\nParsing from known log data (already extracted from session output)")
print(f"Total websites to process: {len(websites)}")
print("\nNote: Full log parsing needed. Reading from session output...")
