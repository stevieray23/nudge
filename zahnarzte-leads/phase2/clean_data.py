#!/usr/bin/env python3
"""
Post-process enriched data: fix name parsing, remove bad emails, clean up.
"""

import json
import re

INPUT_FILE = r"C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_3_enriched.json"
OUTPUT_FILE = r"C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase2\batch_3_enriched.json"

# Emails that are definitely not personal
BAD_EMAILS = {
    "blzk@blzk.de",  # Bayerische Landeszahnärztekammer
    "info@blzk.de",
    "service@winlocal.de",  # KennstDuEinen third-party
}

# Suspicious technical emails (sentry, cloudflare, etc.)
TECH_EMAIL_PATTERNS = ["sentry", "cloudflare", "fastly", "akamai", "unbounce", "wixpress", "hubspot", "mailchimp"]

# German titles to strip from names
TITLE_PATTERN = re.compile(
    r'^(?:Dr\.?|Dr\.?\s+med\.?|Dr\.?\s+med\.?\s+dent\.?|Dr\.?\s+dent\.?|Prof\.?|'
    r'Med\.?\s+dent\.?|Med\.?\s+dent|'
    r'Dipl\.?[\-\s]?Stom\.?|Fachzahnarzt|FA|Zahnarzt|Zahnärztin)\.?\s*',
    re.IGNORECASE
)

# Praxis name prefixes to skip when looking for surnames
PRAXIS_PREFIXES = [
    "Zahnarztpraxis", "Praxis", "Zahnärzte", "Zahnarzt", "Zahnmedizin",
    "Kinderzahnarzt", "Kieferorthopäde", "Oralchirurgie", "Kinderkieferorthopädie",
    "DIEZAHNDESIGNER", "Fachzahnarzt", "Familien", "Gemeinschaftspraxis",
]

def is_bad_email(email):
    """Return True if email is not a useful personal email."""
    if not email:
        return True
    el = email.lower()
    if el in BAD_EMAILS:
        return True
    for p in TECH_EMAIL_PATTERNS:
        if p in el:
            return True
    return False

def is_generic_email(email):
    """Return True if email looks like a generic practice address."""
    if not email:
        return False
    el = email.lower()
    generic_prefixes = [
        "info@", "kontakt@", "service@", "praxis@", "termin@", "termine@",
        "rezeption@", "anmeldung@", "office@", "mail@", "post@",
    ]
    return any(el.startswith(p) for p in generic_prefixes)

def clean_name(name_str):
    """Clean up extracted name - remove titles, strip whitespace."""
    if not name_str:
        return ""
    name_str = name_str.strip()
    name_str = TITLE_PATTERN.sub("", name_str)
    return name_str.strip()

def is_valid_name(name_str):
    """Check if a name looks like a real person's name."""
    if not name_str or len(name_str) < 2:
        return False
    bad_words = ["Zahnarztpraxis", "Praxis", "Leistungen", "Philosophie", "Diese",
                 "Seiten", "Impressum", "Datenschutz", "Kontakt", "Startseite",
                 "Zahnarzt", "Zahnärztin", "Dr", "Home", "Info", "Service",
                 "Error", "Page", "Seite", "Zentrale"]
    for w in bad_words:
        if name_str.lower().startswith(w.lower()):
            return False
    return True

def fix_clinic_name_vorname_nachname(clinic_name):
    """Parse clinic_name (German format: [Prefix] Surname FirstName [Title]) 
    into vorname/nachname."""
    # Remove city/neighborhood from address in parentheses
    name_part = clinic_name
    name_part = re.sub(r'\s*\(.*\)', '', name_part)
    name_part = name_part.strip()
    
    # Split into tokens
    tokens = name_part.split()
    
    result_vorname = ""
    result_nachname = ""
    
    # Filter out prefix tokens
    meaningful_tokens = []
    for t in tokens:
        skip = False
        for p in PRAXIS_PREFIXES:
            if t.lower().startswith(p.lower()):
                skip = True
                break
        if not skip:
            meaningful_tokens.append(t)
    
    if len(meaningful_tokens) == 0:
        return "", ""
    
    # Check if first meaningful token looks like surname (starts with capital, longer)
    # In German: "Meier Kerstin" = surname first, "Dr. Kerstin Meier" = first name first
    
    if len(meaningful_tokens) >= 2:
        first = meaningful_tokens[0]
        second = meaningful_tokens[1]
        second_clean = TITLE_PATTERN.sub("", second)
        
        # If second token has "Dr." title, it's a name (first name comes after)
        if re.match(r'^Dr\.?$', second, re.IGNORECASE):
            # Dr. is a title, name is in later tokens
            remaining = meaningful_tokens[1:]
            if len(remaining) >= 2:
                # remaining: [Dr., FirstName, LastName] or [Dr., LastName, FirstName]
                name_tokens = [t for t in remaining if not re.match(r'^Dr\.?$', t, re.IGNORECASE)]
                if len(name_tokens) >= 2:
                    result_vorname = clean_name(name_tokens[0])
                    result_nachname = clean_name(name_tokens[-1])
                elif len(name_tokens) == 1:
                    result_nachname = clean_name(name_tokens[0])
        else:
            # Both first and second are names
            first_clean = TITLE_PATTERN.sub("", first)
            second_clean = TITLE_PATTERN.sub("", second)
            
            # Heuristic: if second token looks like a first name (common German first names)
            common_first_names = [
                "Kerstin", "Antje", "Wadim", "Alexander", "Matthias", "Christine",
                "Heike", "Matthias", "Gabriele", "Gerald", "Doris", "Andrea",
                "Anne", "Ernst", "Martin", "Johannes", "Alexander", "Jürgen",
                "Konstantinos", "Uwe", "Eva", "Sebastian", "Viktor", "Klaus",
                "Susanne", "Thomas", "Reinhard", "Christian", "Regina", "Roland",
                "Stefanie", "Markus", "Klaus", "Peter", "Mark", "Nicole",
                "Michael", "Wolfgang", "Georgios", "Norbert", "Aysu", "Martin",
                "Birgit", "Stefan", "Daniel", "Katrin", "Ioanna", "Tomislav",
                "Thilo", "Marc", "Andreas", "Michael",
            ]
            
            if second_clean in common_first_names:
                result_vorname = second_clean
                result_nachname = first_clean
            else:
                # First token is surname (German style: Surname FirstName)
                result_vorname = second_clean
                result_nachname = first_clean
    
    elif len(meaningful_tokens) == 1:
        result_nachname = clean_name(meaningful_tokens[0])
    
    return result_vorname, result_nachname

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    fixed_count = 0
    email_fixed_count = 0
    
    for entry in data:
        # ─ Fix email quality ─
        old_email = entry.get("email", "")
        
        if old_email and is_bad_email(old_email):
            entry["email"] = ""
            entry["email_found"] = False
            entry["notes"] = (entry.get("notes", "") + " Bad email removed: " + old_email).strip()
            email_fixed_count += 1
        
        # ─ Fix name quality ─
        vorname = entry.get("vorname", "").strip()
        nachname = entry.get("nachname", "").strip()
        
        # Check if names are garbage (from wrong page sections)
        if not is_valid_name(vorname) or not is_valid_name(nachname):
            # Try to parse from clinic_name
            parsed_v, parsed_n = fix_clinic_name_vorname_nachname(entry.get("clinic_name", ""))
            
            if parsed_n:
                nachname = parsed_n
            if parsed_v:
                vorname = parsed_v
            
            if not is_valid_name(nachname):
                nachname = ""
            if not is_valid_name(vorname):
                vorname = ""
            
            entry["vorname"] = vorname
            entry["nachname"] = nachname
            fixed_count += 1
        
        # ─ Specific known fixes ─
        cn = entry.get("clinic_name", "")
        
        # Manikas Konstantinos → vorname=Konstantinos, nachname=Manikas
        if "Manikas" in cn and "Konstantinos" in cn:
            entry["vorname"] = "Konstantinos"
            entry["nachname"] = "Manikas"
        
        # Bohner Martin → vorname=Martin, nachname=Bohner
        if "Bohner" in cn and "Martin" in cn:
            entry["vorname"] = "Martin"
            entry["nachname"] = "Bohner"
        
        # Sühendan Aysu → vorname=Aysu, nachname=Sühendan
        if "Aysu" in cn:
            entry["vorname"] = "Aysu"
            entry["nachname"] = "Sühendan"
        
        # Dr. Roland Botar → vorname=Roland, nachname=Botar
        if "Botar" in cn:
            entry["vorname"] = "Roland"
            entry["nachname"] = "Botar"
        
        # Michael Schwarz (Stuttgart) - already correct
        if "Schwarz" in cn and "Michael" in cn:
            entry["vorname"] = "Michael"
            entry["nachname"] = "Schwarz"
        
        # Andrea Dittmar - already correct
        if "Dittmar" in cn:
            entry["vorname"] = "Andrea"
            entry["nachname"] = "Dittmar"
        
        # Martin Rießner → vorname=Ernst-Martin or Martin, nachname=Rießner
        if "Rießner" in cn:
            entry["vorname"] = "Martin"
            entry["nachname"] = "Rießner"
        
        # Johannes Greger
        if "Greger" in cn:
            entry["vorname"] = "Johannes"
            entry["nachname"] = "Greger"
        
        # Alexander Bühler
        if "Bühler" in cn:
            entry["vorname"] = "Alexander"
            entry["nachname"] = "Bühler"
        
        # Jürgen Tomaschautzki
        if "Tomaschautzki" in cn:
            entry["vorname"] = "Jürgen"
            entry["nachname"] = "Tomaschautzki"
        
        # Uwe Beck
        if "Beck" in cn and "Uwe" in cn:
            entry["vorname"] = "Uwe"
            entry["nachname"] = "Beck"
        
        # Eva Buchele
        if "Buchele" in cn:
            entry["vorname"] = "Eva"
            entry["nachname"] = "Buchele"
        
        # Viktor Rabe → vorname=Viktor, nachname=Rabe
        if "Rabe" in cn and "Viktor" in cn:
            entry["vorname"] = "Viktor"
            entry["nachname"] = "Rabe"
        
        # Thomas Wölfel
        if "Wölfel" in cn:
            entry["vorname"] = "Thomas"
            entry["nachname"] = "Wölfel"
        
        # Thomas Reinhold
        if "Reinhold" in cn and "Thomas" in cn:
            entry["vorname"] = "Thomas"
            entry["nachname"] = "Reinhold"
        
        # Hannelore Reinhold
        if "Reinhold" in cn and "Hannelore" in cn:
            entry["vorname"] = "Hannelore"
            entry["nachname"] = "Reinhold"
        
        # Reinhard Wießner
        if "Wießner" in cn:
            entry["vorname"] = "Reinhard"
            entry["nachname"] = "Wießner"
        
        # Christian Berndt
        if "Berndt" in cn:
            entry["vorname"] = "Christian"
            entry["nachname"] = "Berndt"
        
        # Stefanie Wißmüller
        if "Wißmüller" in cn:
            entry["vorname"] = "Stefanie"
            entry["nachname"] = "Wißmüller"
        
        # Klaus Wagner
        if "Wagner" in cn and "Klaus" in cn:
            entry["vorname"] = "Klaus"
            entry["nachname"] = "Wagner"
        
        # Peter Bilek
        if "Bilek" in cn:
            entry["vorname"] = "Peter"
            entry["nachname"] = "Bilek"
        
        # Wolfgang Singer
        if "Singer" in cn:
            entry["vorname"] = "Wolfgang"
            entry["nachname"] = "Singer"
        
        # Georgios Xygas
        if "Xygas" in cn:
            entry["vorname"] = "Georgios"
            entry["nachname"] = "Xygas"
        
        # Norbert Woppmann
        if "Woppmann" in cn:
            entry["vorname"] = "Norbert"
            entry["nachname"] = "Woppmann"
        
        # Matthias Hoffmann
        if "Hoffmann" in cn and "Matthias" in cn:
            entry["vorname"] = "Matthias"
            entry["nachname"] = "Hoffmann"
        
        # Stefan Benker
        if "Benker" in cn:
            entry["vorname"] = "Stefan"
            entry["nachname"] = "Benker"
        
        # Marc A. Mauch
        if "Mauch" in cn:
            entry["vorname"] = "Marc"
            entry["nachname"] = "Mauch"
        
        # Andreas Franger
        if "Franger" in cn:
            entry["vorname"] = "Andreas"
            entry["nachname"] = "Franger"
        
        # Mark Schmeer
        if "Schmeer" in cn and "Mark" in cn:
            entry["vorname"] = "Mark"
            entry["nachname"] = "Schmeer"
        
        # Nicole Bauer
        if "Bauer" in cn and "Nicole" in cn:
            entry["vorname"] = "Nicole"
            entry["nachname"] = "Bauer"
        
        # Heerklotz
        if "Heerklotz" in cn:
            entry["vorname"] = "Heerklotz"
            entry["nachname"] = ""
        
        # Dr. Sebastian Heger → vorname=Sebastian, nachname=Heger
        if "Heger" in cn:
            entry["vorname"] = "Sebastian"
            entry["nachname"] = "Heger"
        
        # Leidhold Christine
        if "Leidhold" in cn and "Christine" in cn:
            entry["vorname"] = "Christine"
            entry["nachname"] = "Leidhold"
        
        # West Gerald
        if "West" in cn and "Gerald" in cn:
            entry["vorname"] = "Gerald"
            entry["nachname"] = "West"
        
        # Gaitzsch Heike / Matthias
        if "Gaitzsch" in cn:
            if "Heike" in cn:
                entry["vorname"] = "Heike"
            elif "Matthias" in cn:
                entry["vorname"] = "Matthias"
            entry["nachname"] = "Gaitzsch"
        
        # G. Michael Wittmann
        if "Wittmann" in cn:
            entry["vorname"] = "Michael"
            entry["nachname"] = "Wittmann"
        
        # Dietrich / Martin
        if "Dietrich" in cn and "Klaus" in cn:
            entry["vorname"] = "Klaus"
            entry["nachname"] = "Dietrich"
        if "Martin" in cn and "Susanne" in cn:
            entry["vorname"] = "Susanne"
            entry["nachname"] = "Martin"
        
        # Birgit Fuchs-Bräu → vorname=Birgit, nachname=Fuchs-Bräu
        if "Fuchs-Bräu" in cn:
            entry["vorname"] = "Birgit"
            entry["nachname"] = "Fuchs-Bräu"
        
        # Elsler
        if "Elsler" in cn:
            entry["notes"] = (entry.get("notes", "") + " Multi-dentist practice - no single owner").strip()
        
        # Dr. Kaller & Hennig
        if "Kaller" in cn or "Hennig" in cn:
            entry["notes"] = (entry.get("notes", "") + " Multi-dentist practice").strip()
    
    # Save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Summary
    emails_found = sum(1 for r in data if r.get("email_found"))
    personal_emails = sum(1 for r in data if r.get("email") and r.get("email"))
    impressum_found = sum(1 for r in data if r.get("impressum_found"))
    
    print(f"Data cleaning complete.")
    print(f"  Total leads: {len(data)}")
    print(f"  Impressum found: {impressum_found}")
    print(f"  Emails found (any): {emails_found}")
    print(f"  Emails remaining: {personal_emails}")
    print(f"  Bad emails removed: {email_fixed_count}")
    print(f"  Names fixed: {fixed_count}")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
