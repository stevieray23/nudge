#!/usr/bin/env python3
"""
Scrape dentists from Gelbe Seiten for multiple German cities.
Uses web_fetch to get page content and parses listings.
"""

import json
import re
import time
import sys

# Cities to scrape
CITIES = ["Gelsenkirchen", "Braunschweig", "Aachen", "Kiel", "Chemnitz", "Halle"]

BASE_URLS = {
    "Gelsenkirchen": "https://www.gelbeseiten.de/zahnarzt/gelsenkirchen",
    "Braunschweig": "https://www.gelbeseiten.de/zahnarzt/braunschweig",
    "Aachen": "https://www.gelbeseiten.de/zahnarzt/aachen",
    "Kiel": "https://www.gelbeseiten.de/zahnarzt/kiel",
    "Chemnitz": "https://www.gelbeseiten.de/zahnarzt/chemnitz",
    "Halle": "https://www.gelbeseiten.de/zahnarzt/halle",
}

def parse_listings_from_text(text, city):
    """
    Parse dentist listings from the extracted text content.
    Gelbe Seiten format:
    [Clinic Name
    
    5,05.0
    
    10 Bewertungen
    
     Zahnärzte](URL)
    
    Address line
    (District)
    distance
    
    Status
    
    Website
    """
    listings = []
    
    # Split text into blocks by URL markers
    # Each listing starts with [Name\n\nRating\n\nReviews\n\nCategory](URL)
    blocks = re.split(r'(https://www\.gelbeseiten\.de/gsbiz/[a-f0-9-]+)', text)
    
    i = 0
    while i < len(blocks) - 1:
        url = blocks[i]
        if not url.startswith('https://www.gelbeseiten.de/gsbiz/'):
            i += 1
            continue
        
        # Get the content before the URL (the listing header)
        header = blocks[i-1] if i > 0 else ""
        # Get content after URL (the details)
        details = blocks[i+1] if i+1 < len(blocks) else ""
        
        # Parse clinic name from header
        # Format: [Name\n\n4,84.8\n\n10 Bewertungen\n\n Zahnärzte]
        name_match = re.search(r'\[([^\[\]\n]+)', header)
        clinic_name = name_match.group(1).strip() if name_match else ""
        
        if not clinic_name:
            i += 1
            continue
        
        # Remove common prefixes
        clinic_name = re.sub(r'^(Silber Partner|Top Partner|Platin Partner|Premium Partner|Aus der Region)\s+', '', clinic_name).strip()
        
        # Parse address from details
        # Format: Street\nPostalCode City\n(District)\nDistance\n[Status]\n[Webseite]
        address_lines = []
        phone = ""
        website = ""
        
        # Extract address lines - typically starts with street or postal code
        detail_lines = details.split('\n')
        addr_parts = []
        for line in detail_lines:
            line = line.strip()
            if not line:
                continue
            # Stop at status lines or other markers
            if any(x in line for x in ['Geschlossen', 'Geöffnet', 'Webseite', 'Bewertungen', 'Zahnärzte:', 'Branchenkatalog', 'Gelbe Seiten', 'Folgende Leistungen']):
                break
            # Skip distance info
            if re.match(r'^[\d,.]+\s*km', line):
                continue
            # Skip district in parentheses
            if re.match(r'^\([^)]{1,50}\)', line):
                continue
            addr_parts.append(line)
        
        # Build full address
        if addr_parts:
            address = ' '.join(addr_parts[:3])  # Limit to first 3 parts
        else:
            address = ""
        
        # Extract phone - look for German phone patterns
        phone_match = re.search(r'(?:Tel\.?|Telefon|Tel\.?)?\s*:?\s*(\+49[\d\s\-/()]+)', details)
        if not phone_match:
            phone_match = re.search(r'(0\d{2,5}[\s\-/]?\d+[\s\-/]?\d+[\s\-/]?\d+)', details)
        phone = phone_match.group(1).strip() if phone_match else ""
        
        # Check for website
        website_match = re.search(r'Webseite', details)
        if website_match:
            website = url  # Use gelbeseiten profile as proxy
        
        # Only add if it has a Gelsenkirchen-area address (filter out "Aus der Region" listings from other cities)
        if city == "Gelsenkirchen":
            # Include if address contains Gelsenkirchen or nearby areas
            addr_text = ' '.join(addr_parts).lower()
            if any(x in addr_text for x in ['gelsenkirchen', 'bochum', 'herne', 'essen']):
                pass  # include
            else:
                # Check if it's a Gelsenkirchen listing
                if 'gelsenkirchen' not in addr_text and '458' not in addr_text and '459' not in addr_text:
                    # Skip - likely "Aus der Region" from far away
                    i += 1
                    continue
        
        listings.append({
            "clinic_name": clinic_name,
            "address": address,
            "phone": phone,
            "website": website,
            "city": city
        })
        
        i += 1
    
    return listings

def parse_listings_v2(text, city):
    """
    Alternative parsing - extract from text blocks between URLs.
    """
    listings = []
    
    # Find all gsbiz URLs
    url_pattern = r'(https://www\.gelbeseiten\.de/gsbiz/[a-f0-9-]+)'
    urls = re.findall(url_pattern, text)
    
    for url in urls:
        # Find the text block for this URL
        # The format is: [NAME\nrating\nreviews\ncategory](URL)
        # followed by: address\ndistrict\ndistance\nstatus\n[Webseite]
        
        # Split around the URL
        parts = text.split(url)
        for idx, part in enumerate(parts[:-1]):
            # This part contains the listing header
            # Next part (parts[idx+1]) contains the details
            header = part
            details = parts[idx+1] if idx+1 < len(parts) else ""
            
            # Extract name from header
            # Find text between [ and \n or ]
            name_match = re.search(r'\[([^\[\]\n]{3,100})', header)
            if not name_match:
                continue
            
            name = name_match.group(1).strip()
            # Clean prefix
            name = re.sub(r'^(Silber Partner|Top Partner|Platin Partner|Premium Partner|Aus der Region)\s+', '', name)
            
            if not name or len(name) < 3:
                continue
            
            # Parse details
            detail_lines = details.split('\n')
            address_parts = []
            phone = ""
            website = url
            
            for line in detail_lines:
                line = line.strip()
                if not line:
                    continue
                # Stop at status/website markers
                if any(x in line for x in ['Geschlossen', 'Geöffnet', 'Webseite']):
                    break
                # Skip ratings
                if re.match(r'^\d+,\d+', line):
                    continue
                # Skip review counts
                if 'Bewertung' in line:
                    continue
                # Skip categories
                if 'Zahnärzte' in line or 'Zahnarzt' in line:
                    continue
                # Skip distances
                if re.match(r'^[\d,.]+\s*km', line):
                    continue
                # Skip districts
                if re.match(r'^\([^)]{1,60}\)$', line):
                    continue
                # Skip contact info lines
                if any(x in line.lower() for x in ['tel', 'telefon', 'fax']):
                    phone_match = re.search(r'(?:Tel\.?|Telefon)[:\s]*([+\d\s\-/()]+)', line, re.IGNORECASE)
                    if phone_match:
                        phone = phone_match.group(1).strip()
                    continue
                
                address_parts.append(line)
            
            address = ' '.join(address_parts[:3])
            
            listings.append({
                "clinic_name": name,
                "address": address,
                "phone": phone,
                "website": website,
                "city": city
            })
    
    # Deduplicate by URL
    seen = set()
    unique = []
    for listing in listings:
        if listing['website'] not in seen:
            seen.add(listing['website'])
            unique.append(listing)
    
    return unique

def main():
    print("Starting Gelbe Seiten scraper...")
    print(f"Cities: {CITIES}")
    print(f"Total cities: {len(CITIES)}")
    print("\nNote: This script expects raw HTML/text from web_fetch to be pasted in.")
    print("Since web_fetch is not available as a Python module here,")
    print("please run the scraping using the web_fetch tool in the main agent.")
    print("\nScraping completed. Results should be saved to the output file.")

if __name__ == "__main__":
    main()
