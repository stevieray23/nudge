"""
Gelbe Seiten dentist parser — v4
Strategy: detect dentist names by German name patterns, not by filtering streets.
"""
import json, re
from pathlib import Path

OUT = Path(r"C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase1\agent1_frankfurt_bremen.json")

# ── helpers ──────────────────────────────────────────────────────────────
DENTIST_KW = {'zahnarzt', 'praxis', 'mvz', 'dr.', 'dr ', 'dres', 'dent', 'dent.',
              'kieferorthop', 'implantolog', 'oralchirurg', 'mkg', 'gmbh', 'part'}
BAD_TOKENS = {
    'Zahnärzte', 'Zahnärztinnen', 'Webseite', 'Geöffnet', 'Geschlossen',
    'Bewertungen', 'Bewertung',
    'Platin Partner', 'Gold Partner', 'Bronze Partner', 'Premium Partner',
    'Basic Partner', 'Silber Partner', 'Top Partner',
    'Business', 'Economy', 'Aus der Region',
}
BAD_PREFIXES = ('– ',)
RATING_RE = re.compile(r'^\d,\d\s+\d+\.\d+$')
DIST_RE = re.compile(r'^\d+[,\.]\d+\s*km$')
POSTAL_RE = re.compile(r'^\d{5}\s')

def is_meta(line: str) -> bool:
    s = line.strip()
    if not s: return True
    if s in BAD_TOKENS: return True
    if any(s.startswith(p) for p in BAD_PREFIXES): return True
    if RATING_RE.match(s): return True
    if DIST_RE.match(s): return True
    if POSTAL_RE.match(s): return True
    return False

def is_dentist_name(line: str) -> bool:
    """
    True if this line looks like a dentist practice name in German.
    Detects: Dr., Praxis, MVZ, group names, Zahnarzt keywords.
    Rejects: single street addresses like 'Am Markt 11,' or 'Kaiserstr. 23,'
    """
    s = line.strip()
    if not s: return False
    sl = s.lower()
    # Must contain a dentist keyword (except common words that appear everywhere)
    has_dentist_kw = any(kw in sl for kw in DENTIST_KW)
    # Street-only pattern: a single word with a number and nothing else dental
    # e.g. "Kaiserstr. 23," or "Am Markt 11,"
    # Matches: starts with cap letter word, contains a number, no dental keyword
    street_only = (
        re.match(r'^[A-ZÄÖÜ][a-zäöüß\s\-]+[\d\-]+,?\s*$', s) and
        not has_dentist_kw and
        not re.search(r'dr\.', sl)
    )
    if street_only:
        return False
    return has_dentist_kw

def find_name(lines, addr_idx: int) -> str | None:
    """Walk backwards from addr_idx; first dentist name wins."""
    for off in range(1, 10):
        idx = addr_idx - off
        if idx < 0: break
        l = lines[idx].strip()
        if not l or is_meta(l): continue
        if is_dentist_name(l):
            return l
    return None

def addr_lines(lines, start: int) -> list[str]:
    out = []
    for j in range(start, min(start + 5, len(lines))):
        nxt = lines[j].strip()
        if not nxt: break
        if RATING_RE.match(nxt): break
        if DIST_RE.match(nxt): break
        if nxt in ('Webseite', 'Geöffnet', 'Geschlossen'): break
        if nxt.startswith('–'): break
        if j > start and POSTAL_RE.match(nxt): break  # next listing
        if nxt in BAD_TOKENS: break
        out.append(nxt)
        if len(out) >= 4: break
    return out

def parse(raw: str, city: str) -> list[dict]:
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    recs = []
    i = 0
    while i < len(lines):
        if POSTAL_RE.match(lines[i]):
            al = addr_lines(lines, i)
            name = find_name(lines, i)
            if name:
                recs.append({
                    "clinic_name": name,
                    "address": ' '.join(al),
                    "phone": "",
                    "website": "",
                    "city": city
                })
            i += max(len(al), 1)
        else:
            i += 1
    return recs

# ── raw data (inline) ───────────────────────────────────────────────────
RAW = {
    "Frankfurt am Main": """
Platin Partner
Blei Thomas Dr. med. dent.
 Zahnärzte
Rebgärten 52-54,
 60431 Frankfurt am Main
 (Ginnheim)
 3,6 km
 Geöffnet
 – Schließt um 14:00
 Webseite
Platin Partner
Chamsiddin Khaled DDS/ Uni. Bat. Praxis für Oralchirurgie Frankfurt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Reuterweg 98,
 60323 Frankfurt am Main
 (Westend-Nord)
 1,5 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Aus der Region
Dr. John-Paul Mc Caffrey Zahnarzt
 4,9 4.9
 7 Bewertungen
 Zahnärzte
Hessenring 120,
 61348 Bad Homburg
Gold Partner
Marian Calin Dr. medic. Stom.
 4,0 4.0
 10 Bewertungen
 Zahnärzte
Kaiserstr. 23,
 60311 Frankfurt am Main
 (Innenstadt)
 452 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Gold Partner
Steinert Mark
 Zahnärzte
Kurhessenstr. 4,
 60431 Frankfurt am Main
 (Eschersheim)
 5,2 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Bronze Partner
Bender Thilo A. Zahnarzt
 Zahnärzte
Eiserne Hand 20,
 60318 Frankfurt am Main
 (Nordend-West)
 1,3 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Bronze Partner
Bilow Anja
 2,6 2.6000001
 1 Bewertung
 Zahnärzte
Mercatorstr. 33,
 60316 Frankfurt am Main
 (Nordend-West)
 1,3 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Bronze Partner
Brück, Stefanie Dr. med. dent. , Wegener Katlin Dr. med. dent.
 Zahnärzte
Weißadlergasse 15,
 60311 Frankfurt am Main
 (Altstadt)
 170 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Aus der Region
Dr. med. dent. Peter R. Köppert Zahnarzt & Zahntechniker
 Zahnärzte
Lindenstr. 34,
 63303 Dreieich
 (Sprendlingen)
 9,5 km
Premium Partner
Dr. Milanovic Sandra - Zahnarztpraxis
 Zahnärzte
Blauländchenstr. 4,
 65931 Frankfurt am Main
 (Zeilsheim)
 13,4 km
 Webseite
Bronze Partner
Emmrich Heike
 Zahnärzte
Sandweg 113,
 60316 Frankfurt am Main
 (Nordend-Ost)
 1,7 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Bronze Partner
Löffler Heiko Dr. med. dent. & Reister Daniel
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Fürstenbergerstr. 223,
 60323 Frankfurt am Main
 (Westend-Nord)
 1,6 km
 Geöffnet
 – Schließt um 20:30
 Webseite
Premium Partner
Zahnarztpraxis Dr. Hakimi und Kollegen
 4,0 4.0
 3 Bewertungen
 Zahnärzte
Oeder Weg 52-54,
 60318 Frankfurt am Main
 1,1 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Kubitzky W. Dr., Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Eichendorffstr. 50,
 60320 Frankfurt am Main (Dornbusch)
 (Dornbusch)
 3,5 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Pimentola John Zahnarzt
 Zahnärzte
Brentanostr. 18a,
 60325 Frankfurt am Main
 (Westend-Süd)
 1,5 km
Nautilus-Praxis
 Zahnärzte
Berger Str. 130,
 60385 Frankfurt am Main
 (Nordend-Ost)
 2 km
 Geöffnet
 – Schließt um 20:00
 Webseite
Gäbler Marco Dr.med.dent. u. Codreanu R.
 5,0 5.0
 7 Bewertungen
 Zahnärzte
Liebfrauenberg 37,
 60313 Frankfurt am Main
 144 m
Gäbler Marco Dr.med.dent. u. Codreanu R. Zahnärzte
 5,0 5.0
 7 Bewertungen
 Zahnärzte
Liebfrauenberg 37,
 60313 Frankfurt am Main
 (Altstadt)
 144 m
 Geöffnet
 – Schließt um 20:00
AllDent MVZ GmbH
 4,1 4.1
 70 Bewertungen
 Zahnärzte
Kaiserstr. 1,
 60311 Frankfurt am Main
 (Innenstadt)
 252 m
 Geöffnet
 – Schließt um 21:00
 Webseite
Gilles Dr. u. Fay Dr. Zahnärzte
 5,0 5.0
 8 Bewertungen
 Zahnärzte
An der Hauptwache 5,
 60313 Frankfurt am Main
 (Innenstadt)
 281 m
 Geöffnet
 – Schließt um 21:00
 Webseite
Boulaaouin Derin Dr.
 4,8 4.8
 135 Bewertungen
 Zahnärzte
Zeil 65,
 60313 Frankfurt am Main
Boulaaouin Derin Dr. Zahnarztpraxis
 4,8 4.8
 135 Bewertungen
 Zahnärzte
Zeil 65,
 60313 Frankfurt am Main
 (Innenstadt)
 493 m
 Geöffnet
 – Schließt um 20:00
 Webseite
Padilla Alfonso Dr.med.dent.
 4,9 4.9
 49 Bewertungen
 Zahnärzte
Goethestr. 25,
 60313 Frankfurt am Main
 (Innenstadt)
 557 m
 Geöffnet
 – Schließt um 20:00
 Webseite
Stamm Eric Dr.med.dent. Zahnarztpraxis
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Steinweg 10,
 60313 Frankfurt am Main
 (Innenstadt)
 305 m
 Webseite
A1 Dr. Weinreich
 5,0 5.0
 12 Bewertungen
 Zahnärzte
Opernplatz 4,
 60313 Frankfurt am Main
 692 m
Avci-Groß Özlem Dr. Zahnarztpraxis
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Hasengasse 23,
 60311 Frankfurt am Main
 (Altstadt)
 340 m
 Webseite
Dentaloft MVZ GmbH
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Kaiserstr. 14,
 60311 Frankfurt am Main
 (Innenstadt)
 370 m
 Webseite
Magin Susanne Dr.
 4,8 4.8
 37 Bewertungen
 Zahnärzte
Bockenheimer Anlage 38,
 60322 Frankfurt am Main
 794 m
Holstein Svetlana Zahnarztpraxis
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Steinweg 7,
 60313 Frankfurt am Main
 (Innenstadt)
 272 m
Yavuz Filiz Dr.med.dent. Zahnarztpraxis
 5,0 5.0
 1 Bewertung
 Zahnärzte
Kornmarkt 7,
 60311 Frankfurt am Main
 (Altstadt)
 102 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Weidlich Sabine Dr. u. Klockenkämper Johanna Dr. Zahnärztinnen
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Kaiserhofstr. 10,
 60313 Frankfurt am Main
 (Innenstadt)
 566 m
 Geöffnet
 – Schließt um 21:00
Schöneich Bernd Dr.med.dent. & Kollegen, Zahnärzte
 4,9 4.9
 71 Bewertungen
 Zahnärzte
Querstr. 2,
 60322 Frankfurt am Main
 (Nordend-West)
 978 m
 Geschlossen
 – Öffnet um 15:00
 Webseite
Homsi Claudia u. Jeschke Katja Dr.med.dent. Zahnarztpraxis
 4,8 4.8
 13 Bewertungen
 Zahnärzte
Oeder Weg 34,
 60318 Frankfurt am Main
 (Nordend-West)
 959 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Zaghian Sahar Zahnarztpraxis
 4,7 4.7000003
 22 Bewertungen
 Zahnärzte
Hans-Thoma-Str. 30,
 60596 Frankfurt am Main
 (Sachsenhausen)
 1,1 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Tschackert Dr. & Kollegen Zahnarzt
 4,4 4.4
 8 Bewertungen
 Zahnärzte
Goethestr. 23,
 60313 Frankfurt am Main
 (Innenstadt)
 539 m
 Geöffnet
 – Schließt um 17:00
 Webseite
Dr. Z MVZ GmbH
 5,0 5.0
 1 Bewertung
 Zahnärzte
Zeil 83,
 60313 Frankfurt am Main
 (Altstadt)
 350 m
 Webseite
Krumholz E. Dr. Zahnarzt
 4,8 4.8
 4 Bewertungen
 Zahnärzte
Hochstr. 47,
 60313 Frankfurt am Main
 (Innenstadt)
 653 m
 Webseite
Enciso-Arias Rubin u. Cioch Carolina Dr. Gemeinschaftspraxis
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Oeder Weg 2-4,
 60318 Frankfurt am Main
 (Nordend-West)
 753 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Schmidt D. Dr. Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Zeil 77,
 60313 Frankfurt am Main
 (Innenstadt)
 400 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Klein Filip Dr.med.dent. u. Wagner Katharina Dr.med.dent. Zahnärzte
 5,0 5.0
 1 Bewertung
 Zahnärzte
Goethestr. 3,
 60313 Frankfurt am Main
 (Innenstadt)
 402 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Krstic Milivoj Dr. Zahnärzte
 5,0 5.0
 1 Bewertung
 Zahnärzte
Goethestr. 4-8,
 60313 Frankfurt am Main
 (Innenstadt)
 433 m
 Geöffnet
 – Schließt um 17:00
Karnstedt Volkmar Dr. Zahnarztpraxis
 4,9 4.9
 237 Bewertungen
 Zahnärzte
Oberlindau 51,
 60323 Frankfurt am Main
 1,2 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Hirschbeck Thomas u. Behl-Kilb Anja Zahnarztpraxis
 4,6 4.6
 5 Bewertungen
 Zahnärzte
Große Friedberger Str. 44-46,
 60313 Frankfurt am Main
 (Innenstadt)
 707 m
Hakim Aesthetic Orthodontics Kieferorthopäde
 5,0 5.0
 1 Bewertung
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Zeil 81,
 60313 Frankfurt am Main
 (Innenstadt)
 505 m
 Webseite
Dr. Catharina Steuer-Müller und Dr. Christine Kirchmann Kinderzahnheilkunde
 4,6 4.6
 25 Bewertungen
 Zahnärzte
Barckhausstr. 1,
 60325 Frankfurt am Main
 (Westend-Süd)
 1,3 km
 Webseite
ENDOPUR Praxis-Klinik für Endodontologie
 5,0 5.0
 17 Bewertungen
 Zahnärzte
Barckhausstr. 1,
 60325 Frankfurt am Main
 (Westend-Süd)
 1,3 km
 Geöffnet
 – Schließt um 17:00
 Webseite
""",
    "Bremen": """
Business
Boronowsky Stephan
 Zahnärzte
Am Markt 11,
 28195 Bremen
 (Altstadt)
 129 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Business
Gemeinschaftspraxis Dybvik-Nielsen p.p. GbR
 4,9 4.9
 65 Bewertungen
 Zahnärzte
Geschwister-Scholl-Str. 4,
 28327 Bremen
 (Neue Vahr Südost)
 6,4 km
 Geöffnet
 – Schließt um 20:00
 Webseite
Business
Gojnic Blazo Dr.
 5,0 5.0
 7 Bewertungen
 Zahnärzte
Friedrich-Ebert-Str. 116,
 28201 Bremen
 (Südervorstadt)
 1,2 km
 Geöffnet
 – Schließt um 16:30
 Webseite
Business
Krüger Anke Charlotte Dr. med dent.
 Zahnärzte
Hemmstr. 202,
 28215 Bremen
 (Weidedamm)
 2,2 km
 Webseite
Business
Saathoff Hendrik Dr. med. dent.
 Zahnärzte
Schifferstr. 21,
 28217 Bremen
 (Utbremen)
 2,1 km
Business
Stoltenburg Dirk
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Lausanner Straße 36,
 28325 Bremen
 (Tenever)
 9,7 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Economy
Banas-Wanik Anna
 Zahnärzte
Robert-Koch-Str. 40A,
 28277 Bremen
 (Kattenturm)
 4 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Economy
Does Till Zahnarztpraxis
 Zahnärzte
Arsterdamm 138,
 28279 Bremen
 (Arsten)
 4,9 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Economy
Dr. Kaiser, Schumacher & Kollegen, MVZ am Werdersee
 3,9 3.9
 7 Bewertungen
 Zahnärzte
Buntentorsteinweg 348,
 28201 Bremen
 (Huckelriede)
 1,8 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Economy
Ebeling Frank
 Zahnärzte
Grambker Heerstr. 139A,
 28719 Bremen
 (Burg-Grambke)
 10,7 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Economy
Höhns Matthias u. Huang Jianmin Dr.
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Osterholzer Dorfstr. 26I,
 28307 Bremen
 (Osterholz)
 8,1 km
 Webseite
Economy
Holstermann Gerd-Jürgen Dr., Holstermann Inga K. Dr., Holstermann Jan K.
 Zahnärzte
Crüsemannallee 78,
 28213 Bremen
 (Neu Schwachhausen)
 3,2 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Economy
Jungholt & Dr. Seyer
 Zahnärzte
Heinrich-Plett-Allee 78,
 28259 Bremen
 (Mittelshuchting)
 6,7 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Economy
Moubarak Patrick Dr. und Maik Reber
 4,9 4.9
 18 Bewertungen
 Zahnärzte
Esmarchstr. 5,
 28309 Bremen
 (Sebaldsbrück)
 5,5 km
 Webseite
Economy
Schwier Gerlof u. Maren Dr.
 5,0 5.0
 7 Bewertungen
 Zahnärzte
Kattenturmer Heerstr. 289,
 28277 Bremen
 (Kattenturm)
 4,6 km
 Geschlossen
 – Öffnet um 15:00
Economy
Tröst-Nielsen Klaus Zahnarzt, Tröst-Nielsen Klaus
 Zahnärzte
Bahnhofstr. 8,
 28816 Stuhr
 (Brinkum)
 7 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Economy
Zahnarztpraxis Drs. Michael Kanitz
 5,0 5.0
 1 Bewertung
 Zahnärzte
Landstr. 83,
 28790 Schwanewede
 26,3 km
Apelt Britta Dr.med.dent. u. Kaiser B.
 5,0 5.0
 1 Bewertung
 Zahnärzte
Tessiner Str. 4,
 28325 Bremen
 (Ellenerbrok-Schevemoor)
 9,5 km
Business
Schlemme Christina Dr. & Saleh Kristina Dr.
 5,0 5.0
 1 Bewertung
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
An der Weide 34,
 28195 Bremen
 (Bahnhofsvorstadt)
 862 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Nahas R. Dr. Zahnarzt Oralchirurg.
 4,6 4.6
 8 Bewertungen
 Zahnärzte
Martinistr. 31,
 28195 Bremen
 (Altstadt)
 243 m
 Geschlossen
 – Öffnet um 14:30
 Webseite
Lauenstein Ralf Dr. Zahnarztpraxis
 5,0 5.0
 9 Bewertungen
 Zahnärzte
Westerstr. 17,
 28199 Bremen
 (Alte Neustadt)
 680 m
 Geschlossen
 – Öffnet um 15:00
 Webseite
Stahlberg Dr. & Partner
 5,0 5.0
 498 Bewertungen
 Zahnärzte
Ostertorsteinweg 62,
 28203 Bremen
 (Ostertor)
 724 m
 Geöffnet
 – Schließt um 19:00
 Webseite
Zahnarztpraxis Wilke Siemons
 4,3 4.3
 9 Bewertungen
 Zahnärzte
Obernstr. 26-28,
 28195 Bremen
 (Altstadt)
 244 m
 Geschlossen
 – Öffnet um 15:00
 Webseite
AllDent Zahnzentrum Bremen GmbH
 4,2 4.2000003
 5 Bewertungen
 Zahnärzte
Martinistr. 1,
 28195 Bremen
 (Altstadt)
 192 m
 Geöffnet
 – Schließt um 21:00
 Webseite
Siegmund Tina Dr.med.dent.
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Osterstr. 79,
 28199 Bremen
 (Alte Neustadt)
 848 m
 Geschlossen
 – Öffnet um 14:30
 Webseite
Rühenbeck Petra Dr. Zahnärztin
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Kalkstr. 4,
 28195 Bremen
 (Altstadt)
 914 m
 Webseite
Klencke Vera
 4,8 4.8
 47 Bewertungen
 Zahnärzte
Hermann-Böse-Str. 10,
 28209 Bremen
 (Bürgerweide/Barkhof)
 1,2 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Zahnarztpraxis Dr. Blazo Gojnic & Dr. Slavica Gojnic
 5,0 5.0
 7 Bewertungen
 Zahnärzte
Friedrich-Ebert-Straße 114-116,
 28201 Bremen
 1,2 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Elsholz Henning Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Faulenstr. 54,
 28195 Bremen
 (Altstadt)
 999 m
 Webseite
Ilner Torben Dr.
 4,8 4.8
 5 Bewertungen
 Zahnärzte
Außer der Schleifmühle 80,
 28203 Bremen
 (Ostertor)
 1,2 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Nensa Reinhard, Rathscheck-Nensa Micaela Dres. Zahnärzte für Oralchirurgie
 5,0 5.0
 2 Bewertungen
 Zahnärzte: Oralchirurgie (Fachzahnärzte)
Außer der Schleifmühle 71,
 28203 Bremen
 (Ostertor)
 1,1 km
 Webseite
Seidemann Ralf G. Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Goebenstr. 34,
 28209 Bremen
 (Bürgerweide/Barkhof)
 1,2 km
 Webseite
Harting Olaf Dr., Saleh Rami Dr. Zahnärzte
 4,8 4.8
 4 Bewertungen
 Zahnärzte
Hollerallee 61,
 28209 Bremen
 (Barkhof)
 1,5 km
 Geöffnet
 – Schließt um 18:00
 Webseite
bausdorf & bausdorf Dr. Anja Bausdorf Zahnarzt
 4,1 4.1
 18 Bewertungen
 Zahnärzte
Hollerallee 22,
 28209 Bremen
 (Bürgerpark)
 1,6 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Friedrichs Diana Zahnarztpraxis
 4,6 4.6
 9 Bewertungen
 Zahnärzte
Schwachhauser Heerstr. 52A,
 28209 Bremen
 (Schwachhausen)
 2 km
 Webseite
Burggraf Grit Dr. Zahnarztpraxis
 3,7 3.7
 3 Bewertungen
 Zahnärzte
Außer der Schleifmühle 22,
 28203 Bremen
 (Ostertor)
 1 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Maj Regina Dr. Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Wachmannstr. 52,
 28209 Bremen
 (Bürgerpark)
 1,9 km
 Webseite
Partnerschaft für interdisziplinäre ZahnMedizin
 5,0 5.0
 1 Bewertung
 Zahnärzte
Lüder-von-Bentheim-Str. 18,
 28209 Bremen
 (Schwachhausen)
 1,8 km
 Geöffnet
 – Schließt um 19:00
 Webseite
Wascher Jochen Dr.med.dent. Zahnarzt
 5,0 5.0
 7 Bewertungen
 Zahnärzte
Dötlinger Str. 2,
 28197 Bremen
 (Woltmershausen)
 2,5 km
 Webseite
Haferkamp Olga Dr. Zahnärztin
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Elsasser Str. 93,
 28211 Bremen
 (Gete)
 2,2 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Lindemann Andreas Dr. Zahnarzt
 3,7 3.7
 3 Bewertungen
 Zahnärzte
Parkstr. 105,
 28209 Bremen
 (Barkhof)
 1,4 km
 Geöffnet
 – Schießt um 18:00
 Webseite
Zahnarztpraxis Am Osterdeich 103 Dr. Christian Dreyer
 5,0 5.0
 1 Bewertung
 Zahnärzte
Osterdeich 103,
 28205 Bremen
 (Peterswerder)
 2,2 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Liepe Thomas Dr. med. dent.
 5,0 5.0
 1 Bewertung
 Zahnärzte
Buntentorsteinweg 498,
 28201 Bremen
 (Huckelriede)
 2,3 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Pein Stephan u.Silke Zahnärtze
 4,5 4.5
 6 Bewertungen
 Zahnärzte
Schwachhauser Heerstr. 82,
 28209 Bremen
 (Schwachhausen)
 2,5 km
 Webseite
Knopfe Christian-Uwe Zahnarzt
 4,2 4.2000003
 1 Bewertung
 Zahnärzte
Hemmstr. 178,
 28215 Bremen
 (Regensburger Straße)
 2,1 km
 Webseite
Plättner Maren u. Jörg Zahnärztepraxis
 4,1 4.1
 8 Bewertungen
 Zahnärzte
Woltmershauser Str. 348,
 28197 Bremen
 (Woltmershausen)
 2,7 km
 Webseite
Conradi Frank Dr., Romberg Bastian
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Innsbrucker Str. 96,
 28215 Bremen
 (Weidedamm)
 3 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Krüger Jörg Dr.
 5,0 5.0
 1 Bewertung
 Zahnärzte
Elisabethstr. 62,
 28217 Bremen
 (Steffensweg)
 2,9 km
Zahnarzt Regine Kolem
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Osterfeuerberger Ring 46,
 28219 Bremen
 (Osterfeuerberg)
 3,3 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Hufschmidt Dr. Karsten Zahnarzt
 3,9 3.9
 6 Bewertungen
 Zahnärzte
H.-H.-Meier-Allee 14,
 28213 Bremen
 2,8 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
""",
    "Essen": """
Aesthetische Zahnheilkunde Peter Sponholz
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Witteringstr. 91,
 45130 Essen
 (Südviertel)
 1,6 km
 Geöffnet
 – Schließt um 19:00
 Webseite
ZAHNÄRZTE AM RATHAUS
 Zahnärzte
Schulstr. 3 -5,
 45219 Essen
 11,4 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Darwi.Dent Zahnarztpraxis Basel Darwish Zahnarzt
 Zahnärzte
Rüttenscheider Str. 134,
 45131 Essen
 (Rüttenscheid)
 2,7 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Grotkamp Frank Dr.
 Zahnärzte
Am Schwarzen 7,
 45239 Essen
 (Heidhausen)
 8 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Siemund Volker
 Zahnärzte
Bocholder Str. 183,
 45355 Essen
 (Bochold)
 3,8 km
 Geöffnet
 – Schließt um 16:30
 Webseite
Dr. med. dent. Torsten Voß
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Heidehang 2,
 45134 Essen
 (Stadtwald)
 4 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Klauer Juliane
 Zahnärzte
Altenessener Str. 401,
 45326 Essen
 (Altenessen-Süd)
 4,4 km
Rudolf Jan Burchardt
 4,0 4.0
 1 Bewertung
 Zahnärzte
Gervinusstr. 1,
 45144 Essen
 2,8 km
 Geöffnet
 – Schließt um 18:30
 Webseite
Dyckhoff C.-M.
 Zahnärzte
Kuglerstr. 24,
 45144 Essen
 (Frohnhausen)
 2,6 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Dr. Talayeh Zadeh Zahnarztpraxis
 Zahnärzte
Steeler Str. 258,
 45138 Essen
 (Huttrop)
 1,9 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Dr. Lukas Bialasinski Zahnarzt
 Zahnärzte
Hagmanngarten 2,
 45259 Essen
 (Heisingen)
 7,2 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Kipp Anja
 4,4 4.4
 5 Bewertungen
 Zahnärzte
Bocholder Str. 276,
 45356 Essen
 (Bochold)
 3,4 km
 Webseite
Schlegel Kai Dr. med. dent.
 4,4 4.4
 5 Bewertungen
 Zahnärzte
Bocholder Str. 276,
 45356 Essen
 (Bochold)
 3,4 km
 Geöffnet
 – Schließt um 20:00
 Webseite
Fürst Peter Dr. med. dent.
 Zahnärzte
Klapperstr. 38-40,
 45277 Essen
 (Überruhr-Hinsel)
 6,2 km
Dr. med. dent. Kai Beermann Zahnarzt
 4,8 4.8
 27 Bewertungen
 Zahnärzte
Steeler Str. 402,
 45138 Essen
 (Huttrop)
 3 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Grünhagen Christian R. Dr.
 5,0 5.0
 5 Bewertungen
 Zahnärzte
Hufelandstr. 68,
 45147 Essen
 (Holsterhausen)
 2,6 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Kusnezov Andrej
 Zahnärzte
Grabenstr. 81,
 45141 Essen
 (Stoppenberg)
 2,4 km
 Geöffnet
 – Schließt um 19:00
 Webseite
Albers Heinz-Jürgen Dr. Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Grabenstr. 81,
 45141 Essen
 (Stoppenberg)
 2,4 km
 Geöffnet
 – Schließt um 19:00
 Webseite
Kieferorthopädische Fachpraxis Gabersek Dr. med. dent., Kiwitz Dr. med. dent.
 4,8 4.8
 24 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Frankenstr. 143,
 45134 Essen
 (Stadtwald)
 4 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Hagemann Kai Dr. med. dent.
 2,8 2.8
 9 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Limbecker Platz 9,
 45127 Essen
 (Stadtkern)
 344 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Zahnarztpraxis Werner Roskothen
 5,0 5.0
 1 Bewertung
 Zahnärzte: Ästhetische Zahnmedizin (Schwerpunkt)
Huyssenallee 5,
 45128 Essen
 765 m
 Geschlossen
 – Öffnet um 14:30
 Webseite
Marzi Dr.
 4,8 4.8
 55 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Klemensborn 42,
 45239 Essen
 (Werden)
 7,7 km
 Geöffnet
 – Schließt um 17:30
 Webseite
Loock Heidrun van Zahnärztin
 4,9 4.9
 9 Bewertungen
 Zahnärzte
Kettwiger Str. 31,
 45127 Essen
 (Stadtkern)
 139 m
Kuhn Michaela Zahnärztin
 4,8 4.8
 5 Bewertungen
 Zahnärzte
Kettwiger Str. 2-10,
 45127 Essen
 (Stadtkern)
 335 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Essers Peter Dr. Kieferorthopäde
 4,8 4.8
 82 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Rolandstr. 7,
 45128 Essen
 (Südviertel)
 874 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Gem Praxis Dr. Markovic
 5,0 5.0
 1 Bewertung
 Zahnärzte
Kopstadtplatz 2,
 45127 Essen
 (Stadtkern)
 213 m
Schnitzler Manfred Dr. Zahnarzt
 4,2 4.2000003
 5 Bewertungen
 Zahnärzte
Kettwiger Str. 54,
 45127 Essen
 (Stadtkern)
 174 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Diedrich Frank Dr. Fachzahnarzt für Kieferorthopädie
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Alfredstr. 393,
 45133 Essen
 (Bredeney)
 4,8 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
""",
    "Bochum": """
Taschke, Bettina Dr.
 4,9 4.9
 51 Bewertungen
 Zahnärzte
Ruhrstr. 142,
 44869 Bochum
 (Eppendorf)
 5,1 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Aesthetische Zahnheilkunde Jana Anastase & Adrian Hadyniak
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Oststr. 40,
 44866 Bochum
 (Wattenscheid)
 5,5 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Bochumer Zahnetage
 4,5 4.5
 4 Bewertungen
 Zahnärzte
Huestr. 34,
 44787 Bochum
 (Innenstadt)
 322 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Przybylek Barbara M. Dr. / Przybylek Christoph Dr. / Przybylek Thomas
 4,6 4.6
 27 Bewertungen
 Zahnärzte
Markstr. 417,
 44795 Bochum
 (Weitmar)
 4,6 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Thies Alexandra Dr.
 4,9 4.9
 16 Bewertungen
 Zahnärzte
Bongardstr. 21,
 44787 Bochum
 (Innenstadt)
 250 m
 Geöffnet
 – Schließt um 19:30
 Webseite
Zahnklinik Bochum und ÜBAG
 Zahnärzte
Bergstr. 28,
 44791 Bochum
 (Grumme)
 572 m
 Geöffnet
 – Schließt um 20:00
 Webseite
Dr. med. dent. Klenke / ZA. Naum Kreitschmann
 Zahnärzte
Herner Str. 335,
 44807 Bochum
 (Riemke)
 2,9 km
 Geöffnet
 – Schließt um 17:00
 Webseite
Worobjows Tanja Zahnärztin
 Zahnärzte
Hattinger Str. 809,
 44879 Bochum
 (Linden)
 7,1 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Großkurth Hilmar
 Zahnärzte
Clemensstr. 14,
 44789 Bochum
 (Wiemelhausen)
 977 m
 Geschlossen
 – Öffnet um 15:00
Schmidt Stephan Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Nordring 84,
 44787 Bochum
 (Innenstadt)
 378 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Pagiela-Lange Magdalena
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Voedestr. 69-71,
 44866 Bochum
 (Wattenscheid)
 5,1 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Dr. med. Julia Lenz Zahnarztpraxis
 Zahnärzte
Herner Str. 289,
 44809 Bochum
 (Hofstede)
 2,4 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
du Bois Dr. med. dent. Zahnarztpraxis Linden
 Zahnärzte
Kesterkamp 45-47,
 44879 Bochum
 (Linden)
 7,7 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Neukirchen Stefan Dr. u. Tsiokas Angelos Dr. Zahnärzte
 5,0 5.0
 5 Bewertungen
 Zahnärzte
Huestr. 34,
 44787 Bochum
 (Innenstadt)
 324 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Sievers S. Dipl.-Stom., Kreitschman N., Klenke C. Dr. med. dent. Gemeinschaftspraxis für Zahnärzte
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Herner Str. 335,
 44807 Bochum
 (Riemke)
 2,9 km
 Geöffnet
 – Schließt um 17:00
 Webseite
Dr. M. Friesen, Dr. B. Genderski, Dr. K. Friesen, Dr. P. Ehl Kieferorthopädische Gem.-praxis
 4,0 4.0
 4 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Viktoriastr. 23,
 44787 Bochum
 (Innenstadt)
 344 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Praxisklinik für Mund-Kiefer-Gesichtschirurgie Dr. Dr. Rafael Grimm
 Zahnärzte: Implantologie (Schwerpunkt)
Huestr. 18,
 44787 Bochum
 (Innenstadt)
 443 m
 Geschlossen
 – Öffnet um 15:00
 Webseite
Neukirchen Stefan Dr. Zahnärzte u. Tsiokas Angelos Dr.
 5,0 5.0
 5 Bewertungen
 Zahnärzte
Huestr. 34,
 44787 Bochum
 (Innenstadt)
 322 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Krah Jürgen Dr. Zahnarzt
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Große Beckstr. 19,
 44787 Bochum
 (Innenstadt)
 367 m
Dental.Ruhr Dervis Koyupinar Zahnarzt
 5,0 5.0
 5 Bewertungen
 Zahnärzte
Kurt-Schumacher-Platz 4,
 44787 Bochum
 (Bochum)
 564 m
 Geöffnet
 – Schließt um 20:00
 Webseite
Schuleit Ralf Dr. Zahnarzt
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Südring 15,
 44787 Bochum
 (Innenstadt)
 536 m
 Geschlossen
 – Öffnet Dienstag um 08:00
 Webseite
Wüst Michael Zahnarzt
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Kortumstr. 32,
 44787 Bochum
 (Innenstadt)
 520 m
 Geschlossen
 – Öffnet um 14:30
 Webseite
Mamok-Lawo Ulrike Dr. Zahnärztin, Burow Natalia Zahnärztin
 5,0 5.0
 1 Bewertung
 Zahnärzte
Brückstr. 62,
 44787 Bochum
 (Innenstadt)
 330 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Niegel Thomas Dr.med.dent. Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Huestr. 4,
 44787 Bochum
 (Innenstadt)
 559 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Niekamp Helga Dr., Kai-Uwe Dr. Zahnärzte
 5,0 5.0
 1 Bewertung
 Zahnärzte
Kanalstr. 20,
 44787 Bochum
 (Innenstadt)
 430 m
 Geschlossen
 – Öffnet um 14:30
 Webseite
Winking Robert Dr.med.dent. Zahnarzt
 4,0 4.0
 12 Bewertungen
 Zahnärzte
Maximilian-Kolbe-Str. 42,
 44793 Bochum
 (Innenstadt)
 583 m
 Geschlossen
 – Öffnet um 14:30
 Webseite
Schmidt Michael Zahnarztpraxis
 5,0 5.0
 1 Bewertung
 Zahnärzte
Massenbergstr. 15,
 44787 Bochum
 (Innenstadt)
 535 m
 Geschlossen
 – Öffnet um 15:00
 Webseite
Falta Burghard Dipl.-Stom. und Spezialist für Endodontologie, Fachzahnarzt für Allgemeine Stomatologie Heidrun Dipl.-Stom.
 4,3 4.3
 3 Bewertungen
 Zahnärzte
Kurt-Schumacher-Platz 11,
 44787 Bochum
 595 m
 Geöffnet
 – Schließt um 18:00
 Webseite
innodentum Zahnmedizin Bochum Kiziler Ferit M.
 4,9 4.9
 20 Bewertungen
 Zahnärzte
Steinring 56,
 44789 Bochum
 (Bochum)
 1,5 km
 Geöffnet
 – Schließt um 18:00
 Webseite
König Stefan Dr. Zahnarzt Oral-Chirurgie "Twin Tower"
 4,2 4.2000003
 3 Bewertungen
 Zahnärzte: Oralchirurgie (Fachzahnärzte)
Massenbergstr. 19-21.,
 44787 Bochum
 (Innenstadt)
 640 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Keller Claudia Zahnärztin
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Universitätsstr. 61,
 44789 Bochum
 (Ehrenfeld)
 1,1 km
 Geschlossen
 – Öffnet um 14:30
Ferdosi Sepideh Zahnärztin
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Herner Str. 141,
 44809 Bochum
 (Hamme)
 1,4 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Speidel Peter Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Bergstr. 115,
 44791 Bochum
 (Grumme)
 1,1 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Glodan A. Zahnärztin
 3,4 3.4
 2 Bewertungen
 Zahnärzte
Hellweg 5,
 44787 Bochum
 (Innenstadt)
 472 m
 Webseite
Killing Dr. Zahnärztin
 5,0 5.0
 1 Bewertung
 Zahnärzte
Gudrunstr. 56,
 44791 Bochum
 (Grumme)
 1,6 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Leugner Gerhard Dr. Zahnarzt, Schöbel Lina Dr. Zahnarzt
 5,0 5.0
 7 Bewertungen
 Zahnärzte
Castroper Str. 205,
 44791 Bochum
 (Innenstadt)
 2,2 km
 Webseite
Meyer, Martin Zahnarzt
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Bochumer Str. 14,
 44623 Herne
 (Mitte)
 5,9 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Neudorf-Konze Brigitte Dr. Zahnarztpraxis
 4,2 4.2000003
 2 Bewertungen
 Zahnärzte
Steinring 8,
 44789 Bochum
 (Wiemelhausen)
 1,4 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Klinger Eric Dr. Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Cimbernstr. 2,
 44793 Bochum
 (Weitmar)
 1,8 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Böwering u. Zöllner Dres. med. dent. Zahnärzte
 4,9 4.9
 122 Bewertungen
 Zahnärzte
Josephinenstr. 234B,
 44791 Bochum
 (Grumme)
 2,6 km
 Geöffnet
 – Schließt um 19:00
 Webseite
""",
    "Bielefeld": """
Business
Praxis Dr. Geu
 5,0 5.0
 1 Bewertung
 Zahnärzte
Friedrich-Verleger-Str. 7,
 33602 Bielefeld
 (Innenstadt)
 252 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Business
Specht Oliver
 Zahnärzte
Carl-Severing-Str. 112,
 33649 Bielefeld
 (Quelle)
 4,8 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Economy
Badura Christian, Zahnarzt Implantologie Parodontologie Prophylaxe
 2,7 2.7
 2 Bewertungen
 Zahnärzte
Vogelruth 13,
 33647 Bielefeld
 (Brackwede)
 4,2 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Economy
Dr. Frank Nienstedt
 4,2 4.2000003
 5 Bewertungen
 Zahnärzte
Hauptstr. 53,
 33647 Bielefeld
 (Brackwede)
 4,1 km
 Geöffnet
 – Schließt um 14:00
 Webseite
Economy
Drs. (NL) Hub. J.M. van Rijt
 Zahnärzte
Altmühlstr. 30b,
 33689 Bielefeld
 (Sennestadt)
 9,3 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Economy
Gellert J. Dr.
 Zahnärzte
Hirschweg 96,
 33689 Bielefeld
 (Sennestadt)
 9,9 km
 Geschlossen
 – Öffnet um 14:00
Economy
Pfeifer Klaus Dr.
 Zahnärzte
Niedernstr. 28,
 33602 Bielefeld
 (Innenstadt)
 124 m
 Geschlossen
 – Öffnet um 15:00
 Webseite
Economy
Schmelzer J.
 5,0 5.0
 1 Bewertung
 Zahnärzte
Voltmannstr. 158,
 33613 Bielefeld
 (Gellershagen)
 3,1 km
 Geschlossen
 – Öffnet um 14:00
Aus der Region
Dr. Jörg Umfermann u. Dr. Isabel Hespe-Umfermann
 4,8 4.8
 4 Bewertungen
 Zahnärzte
Hauptstr. 7A,
 33813 Oerlinghausen
 11,4 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Aus der Region
Implantologie-Zentrum-Gütersloh Dr.med.dent. Herman Hidajat
 4,7 4.7000003
 3 Bewertungen
 Zahnärzte
Münsterstr. 7,
 33330 Gütersloh
 (Innenstadt)
 17 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Aus der Region
Zahnärzte Lehmann - Praxisklinik für Implantologie
 Zahnärzte
Bismarckstr. 20a,
 32545 Bad Oeynhausen
 (Innenstadt)
 27,2 km
 Geöffnet
 – Schließt um 20:00
 Webseite
Aus der Region
Zahnarztpraxis Dr. Angelika Wensing & Anne König
 Zahnärzte
Kneppers Gäßchen 17,
 33428 Harsewinkel
 22 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Business
Tohid Pars, Zahnarzt Implantologie Parontologie
 5,0 5.0
 1 Bewertung
 Zahnärzte: Implantologie (Schwerpunkt)
Am Großen Feld 10,
 33617 Bielefeld
 (Gadderbaum)
 2,5 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Economy
Rako Julia, Dr., Rako Ivan Dr. Dr.
 5,0 5.0
 1 Bewertung
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Welle 15,
 33602 Bielefeld
 (Innenstadt)
 486 m
 Geöffnet
 – Schließt um 17:15
 Webseite
Economy
Wellen Claudia Dr. Kieferorthopädin
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Am Hang 8,
 33619 Bielefeld
 (Großdornberg)
 3,7 km
 Geöffnet
 – Schließt um 17:00
 Webseite
Zwanzig Kai Dr. Zahnarzt
 4,9 4.9
 47 Bewertungen
 Zahnärzte
Mauerstr. 8,
 33602 Bielefeld
 (Innenstadt)
 222 m
 Webseite
Schneidereit Michael Dr.
 5,0 5.0
 8 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Niederwall 29,
 33602 Bielefeld
 (Innenstadt)
 359 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Pijahn Oliver Dr.med.dent. Zahnarzt
 5,0 5.0
 5 Bewertungen
 Zahnärzte
Grünstr. 26,
 33615 Bielefeld
 (Innenstadt)
 578 m
 Webseite
Kayar Yonca Zahnärztin
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Obernstr. 15,
 33602 Bielefeld
 (Innenstadt)
 416 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Feuerstein Gregor Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Friedenstr. 1,
 33602 Bielefeld
 (Innenstadt)
 198 m
 Geöffnet
 – Schließt um 17:00
Dr. Johanning & Partner Zahnärztepraxis
 5,0 5.0
 1 Bewertung
 Zahnärzte
Bahnhofstr. 47,
 33602 Bielefeld
 (Innenstadt)
 484 m
 Webseite
Hoyer Marc Dr. Praxis für Zahnmedizin
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Jöllenbecker Str. 40,
 33613 Bielefeld
 (Innenstadt)
 920 m
 Webseite
Nawartschi Dr. Amir C. Implantologie u. Parodontologie Zahnärzte
 4,9 4.9
 8 Bewertungen
 Zahnärzte
Gadderbaumer Str. 36,
 33602 Bielefeld
 (Innenstadt)
 1,3 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Praxis Dr. Benz u. Kollegen Zahnarztpraxis
 4,0 4.0
 4 Bewertungen
 Zahnärzte
Am Bach 20,
 33602 Bielefeld
 (Innenstadt)
 494 m
 Geschlossen
 – Öffnet um 14:00
May Tobias Dr. med. dent.
 5,0 5.0
 1 Bewertung
 Zahnärzte
Wertherstr. 50,
 33615 Bielefeld
 (Innenstadt)
 1 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Ruschhaupt Jochen Dr. Zahnarzt
 3,7 3.7
 3 Bewertungen
 Zahnärzte
Viktoriastr. 25-27,
 33602 Bielefeld
 (Innenstadt)
 418 m
 Webseite
Kemper Sigrid Dr., Sturhann J. Carsten Zahnärzte
 5,0 5.0
 1 Bewertung
 Zahnärzte
Detmolder Str. 25-33,
 33604 Bielefeld
 (Innenstadt)
 1,1 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Dentikum Zahnärzte
 4,9 4.9
 16 Bewertungen
 Zahnärzte
Artur-Ladebeck-Str. 81,
 33617 Bielefeld
 (Innenstadt)
 1,9 km
 Geöffnet
 – Schließt um 20:00
 Webseite
Szypajlo Mariusz
 5,0 5.0
 1 Bewertung
 Zahnärzte
Schloßhofstr. 37,
 33615 Bielefeld
 (Innenstadt)
 1,2 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
MKG am Adenauerplatz
 4,0 4.0
 3 Bewertungen
 Zahnärzte
Gadderbaumer Str. 14,
 33602 Bielefeld
 (Innenstadt)
 1 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Blum Martin Dr.
 4,0 4.0
 1 Bewertung
 Zahnärzte
Nebelswall 11,
 33602 Bielefeld
 (Innenstadt)
 747 m
 Webseite
Markiewicz Daniel Dr. Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Apfelstr. 23A,
 33613 Bielefeld
 (Innenstadt)
 1,8 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Schau Ingmar Dr.med.dent. Zahnarzt
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Nachtigallstr. 1,
 33607 Bielefeld
 (Innenstadt)
 2,3 km
 Webseite
Bisspraxis – Praxis für Zahngesundheit Trägerin: 4smile MVZ GmbH
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Otto-Brenner-Str. 122,
 33607 Bielefeld
 (Innenstadt)
 2,4 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Strathmann Roger Dr.
 3,7 3.7
 3 Bewertungen
 Zahnärzte
Gadderbaumer Str. 41,
 33602 Bielefeld
 (Innenstadt)
 1,4 km
 Geschlossen
 – Öffnet um 14:30
Rocholl Klaus Dr.med.dent. Zahnarzt
 5,0 5.0
 8 Bewertungen
 Zahnärzte
Osningstr. 3,
 33605 Bielefeld
 (Sieker)
 2,8 km
 Webseite
Dr. Arthur Baumgardt Zahnarztpraxis
 4,7 4.7000003
 3 Bewertungen
 Zahnärzte
Meierfeld 4,
 33611 Bielefeld
 (Schildesche)
 2,5 km
Oles Christian Dr. Zahnarzt
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Meinolfstr. 6,
 33607 Bielefeld
 (Innenstadt)
 2,8 km
 Webseite
Breitenfeld Aneta Zahnärztin
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Heeper Str. 262,
 33607 Bielefeld
 (Innenstadt)
 2,8 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Einenckel Matthias M.Sc. Zahnarzt
 4,8 4.8
 46 Bewertungen
 Zahnärzte
Beckhausstr. 210,
 33611 Bielefeld
 (Schildesche)
 3,5 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Semmler Rudolf Zahnarzt
 Zahnärzte
Jahnplatz 10,
 33602 Bielefeld
 (Innenstadt)
 64 m
 Webseite
Implantat-Zentrum Bielefeld
 Zahnärzte
Alfred-Bozi-Str. 23,
 33602 Bielefeld
 (Innenstadt)
 108 m
 Geöffnet
 – Schließt um 18:00
 Webseite
Pfeifer Klaus Dr. Zahnarztpraxis
 Zahnärzte
Niedernstr. 28,
 33602 Bielefeld
 (Innenstadt)
 124 m
 Webseite
Dr. med. dent. Wolfgang Stute Praxis für ganzheitliche und innovative Zahnheilkunde
 Zahnärzte
Niedernstraße 37,
 33602 Bielefeld
 125 m
 Geschlossen
 – Öffnet um 15:00
 Webseite
Stute Wolfgang Dr.med.dent.
 Zahnärzte
Niedernstr. 37,
 33602 Bielefeld
 (Innenstadt)
 127 m
 Webseite
Zahnarzt am Niederwall Dr. Sandra Eggert Zahnarzt
 Zahnärzte
Niederwall 9,
 33602 Bielefeld
 (Innenstadt)
 135 m
 Geöffnet
 – Schließt um 20:00
 Webseite
Bohatsch Torsten Dr. Zahnarzt
 Zahnärzte
Wilhelmstr. 3a,
 33602 Bielefeld
 166 m
Bäumer-König Amelie Margarete Elisabeth Dr.
 Zahnärzte
Niedernstr. 16,
 33602 Bielefeld
 (Innenstadt)
 179 m
 Webseite
Blümchen Torsten Dr.med.dent.
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Körnerstr. 5,
 33602 Bielefeld
 (Innenstadt)
 190 m
 Webseite
Schmidt-Nonhoff, A., Dr. med. dent, Löhnert, S., Dr. med. Dr. med. dent
 Zahnärzte
Wilhelmstr. 13,
 33602 Bielefeld
 (Innenstadt)
 260 m
 Geöffnet
 – Schließt um 19:00
 Webseite
""",
    "Bonn": """
Basic Partner
Bader Stefan
 Zahnärzte
Rochusstr. 305,
 53123 Bonn
 4,6 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Basic Partner
Kaiser Kerstin Zahnärztin
 Zahnärzte
Hausdorffstr. 185-187,
 53129 Bonn
 2,6 km
 Geöffnet
 – Schließt um 21:00
 Webseite
Basic Partner
Mahmoudian M. Reza Zahnarzt
 Zahnärzte
Münsterstr. 18,
 53111 Bonn
 193 m
Basic Partner
Rehfeld Eva-Marie Dr. med. dent.
 Zahnärzte
Mittelstr. 52,
 53175 Bonn
 5,7 km
 Geöffnet
 – Schließt um 18:00
Griese Bettina Dr.
 5,0 5.0
 1 Bewertung
 Zahnärzte
Rochusstr. 81,
 53123 Bonn
 3,5 km
Bär Bettina Zahnärztin
 Zahnärzte
Geschlossen
 – Öffnet um 14:30
Bagambisa Frank Dr. Dr.(YU) Mund-Kiefer-Gesichtschirurg
 5,0 5.0
 1 Bewertung
 Zahnärzte
Koblenzer Str. 37,
 53173 Bonn
 (Bad Godesberg)
 6,7 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Barzinmehr Gilda Zahnarzt
 Zahnärzte
Mainzer Str. 193,
 53179 Bonn
 (Mehlem)
 10,5 km
Bayer Stefan Dr.med Zahnarzt, Priv.-Doz.
 Zahnärzte
Hauptstr. 56A,
 53229 Bonn
 (Holzlar)
 5,4 km
 Webseite
Becker Eric Dr.med.dent. Zahnarzt
 5,0 5.0
 7 Bewertungen
 Zahnärzte
Meßdorfer Str. 187,
 53123 Bonn
 4 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Behrend Andreas Dr. Zahnarzt
 Zahnärzte
Thomas-Mann-Str. 23,
 53111 Bonn
 (Zentrum)
 327 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Besel Willi Zahnarzt
 Zahnärzte
Theaterplatz 11,
 53177 Bonn
 6,8 km
Bissinger Sindhu Zahnärztin für Kieferorthopädie
 Zahnärzte
Poppelsdorfer Allee 62,
 53115 Bonn
 (Poppelsdorf)
 685 m
Bodenschatz Christoph Dr. Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Caspar-D.-Friedrich-Str. 3,
 53125 Bonn
 5,3 km
 Geschlossen
 – Öffnet um 14:00
Bormann J. Dr.
 Zahnärzte
Meßdorfer Str. 306,
 53123 Bonn
 (Zentrum)
 4,3 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Brandenburg Christine Zahnärztin
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Loestr. 7,
 53113 Bonn
 822 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Broll Ludwik Dr.med.dent.
 5,0 5.0
 1 Bewertung
 Zahnärzte
Stolpstr. 1A,
 53119 Bonn
 (Tannenbusch)
 3,5 km
 Geschlossen
 – Öffnet um 15:00
Burkert Vesela Dr. Zahnarztpraxis
 Zahnärzte
Hausdorffstr. 345,
 53129 Bonn
 3,4 km
Caldarella Fabio Dr. Zahnarzt
 Zahnärzte
Enggasse 3,
 53127 Bonn
 3,4 km
Choi Yu Jung Zahnärztin
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Endenicher Allee 27,
 53121 Bonn
 (Endenich)
 1,6 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Claßen Oliver Dr.med Zahnärzte, Wassong W. J. Dr.med Zahnärzte
 3,0 3.0
 2 Bewertungen
 Zahnärzte
Joachimstr. 1A,
 53113 Bonn
 1,4 km
 Webseite
Daum Peter Dr. Zahnarzt
 4,4 4.4
 4 Bewertungen
 Zahnärzte
Sternenburgstr. 1,
 53115 Bonn
 (Poppelsdorf)
 1,5 km
 Geschlossen
 – Öffnet um 14:00
De John Maribel Varela
 Zahnärzte
Thomas-Mann-Str. 5,
 53111 Bonn
 (Zentrum)
 347 m
Delius Georg Dr.med.dent. Zahnarzt
 Zahnärzte
Graurheindorfer Str. 107,
 53117 Bonn
 1,5 km
Dentalwerk Bonn
 Zahnärzte
Auf der Schleide 75,
 53225 Bonn
 (Beuel)
 1,5 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Deubel Rainer Dr. Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Friedrich-Ebert-Allee 63,
 53113 Bonn
 (Zentrum)
 3,3 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Dieckhoff Myriam Zahnarztpraxis
 4,2 4.2000003
 5 Bewertungen
 Zahnärzte
Joseph-Roth-Str. 96,
 53175 Bonn
 4,8 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Dilg Andreas Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Schultheißstr. 1,
 53225 Bonn
 2,9 km
 Webseite
Dittrich Andreas Dr.med.dent. Zahnarzt
 Zahnärzte
Kreuzherrenstr. 59,
 53227 Bonn
 (Beuel)
 2,4 km
 Geschlossen
 – Öffnet um 14:00
Ehlenz Heinrich Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Friedrich-Breuer-Str. 98,
 53225 Bonn
 (Beuel)
 1,8 km
Engels Helmut B. Dr.med.dent. Zahnarzt Implantologie
 Zahnärzte
Am Kurpark 5,
 53177 Bonn
 (Bad Godesberg)
 6,8 km
 Geschlossen
 – Öffnet Dienstag um 08:30
 Webseite
Falla Frank Farzin Dr. Zahnarztpraxis
 4,9 4.9
 14 Bewertungen
 Zahnärzte
Oxfordstr. 12-16,
 53111 Bonn
 (Zentrum)
 403 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Fandel Markus Dr. Zahnarzt
 Zahnärzte
Mainzer Str. 45,
 53179 Bonn
 (Mehlem)
 9,4 km
 Geschlossen
 – Öffnet um 14:00
 Webseite
Föll Viktor Zahnarzt
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Kölnstr. 480,
 53117 Bonn
 (Zentrum)
 3 km
 Geschlossen
 – Öffnet um 15:00
 Webseite
Foet Jan Hendrik Dr.med.dent. Zahnarzt, Wencke Dr.med.dent. Zahnärztliche Gemeinschaftspraxis
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Hopmannstr. 7,
 53177 Bonn
 (Muffendorf)
 7,9 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Fritsch Ferdinand Dr.med.dent. Zahnarzt
 5,0 5.0
 1 Bewertung
 Zahnärzte
Adenauerallee 23,
 53111 Bonn
 591 m
 Geöffnet
 – Schließt um 19:00
 Webseite
Fuß Markus Dr.med.dent. Zahnarzt
 5,0 5.0
 2 Bewertungen
 Zahnärzte
Alte Bahnhofstr. 1A,
 53173 Bonn
 6,8 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Basic Partner
Wahner Susanne Kieferorthopädin
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Konrad-Adenauer-Platz 26,
 53225 Bonn
 1,5 km
 Geöffnet
 – Schließt um 18:00
 Webseite
Basic Partner
Dr. med. dent. Christina Winkel
 4,8 4.8
 4 Bewertungen
 Zahnärzte
Großenbuschstr. 18,
 53757 Sankt Augustin
 6,8 km
 Geschlossen
 – Öffnet um 14:30
 Webseite
Basic Partner
Ziegler Anne
 5,0 5.0
 2 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Kerpstr. 36,
 53844 Troisdorf
 7,6 km
 Geöffnet
 – Schließt um 17:00
 Webseite
Steinberg Zahnarzt
 4,9 4.9
 33 Bewertungen
 Zahnärzte
Martinsplatz 2A,
 53113 Bonn
 (Zentrum)
 148 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
Otterbach Thomas Dr.med.dent., Brohm Heinz Dr.med.dent. Zahnärzte
 4,9 4.9
 8 Bewertungen
 Zahnärzte
Münsterstr. 20,
 53111 Bonn
 (Zentrum)
 174 m
 Geschlossen
 – Öffnet um 14:00
Wesner Bärbel Praxis für Zahnmedizin
 5,0 5.0
 4 Bewertungen
 Zahnärzte
Gerhard-von-Are-Str. 4,
 53111 Bonn
 (Zentrum)
 146 m
 Geöffnet
 – Schließt um 19:00
 Webseite
Lehmann Karl Martin Dr.med.dent. Zahnarzt
 5,0 5.0
 3 Bewertungen
 Zahnärzte
Friedensplatz 9,
 53111 Bonn
 (Zentrum)
 291 m
 Geöffnet
 – Schließt um 19:00
 Webseite
Kim Christian Dr.med.dent. Kieferorthopäde
 5,0 5.0
 2 Bewertungen
 Zahnärzte: Kieferorthopädie (Fachzahnärzte)
Münsterstr. 18,
 53111 Bonn
 (Zentrum)
 193 m
 Webseite
Siebers Georg Dr.med.dent. Zahnarzt
 4,3 4.3
 6 Bewertungen
 Zahnärzte
Dreieck 4A,
 53111 Bonn
 (Zentrum)
 137 m
Grüttner-Schroff Mirjam Dr. Zahnärztin
 5,0 5.0
 52 Bewertungen
 Zahnärzte
Königstr. 79,
 53115 Bonn
 (Zentrum)
 896 m
 Geschlossen
 – Öffnet um 14:00
 Webseite
"""
}

# ── main ─────────────────────────────────────────────────────────────────
all_recs = []
for city, raw in RAW.items():
    recs = parse(raw, city)
    print(f"  {city}: {len(recs)} records")
    all_recs.extend(recs)

# dedup
seen = set()
deduped = []
for r in all_recs:
    k = (r["clinic_name"].strip(), r["address"].strip())
    if k not in seen:
        seen.add(k)
        deduped.append(r)

print(f"\nTotal after dedup: {len(deduped)}")
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)
print(f"Saved: {OUT}")

from collections import Counter
for c, n in sorted(Counter(r["city"] for r in deduped).items()):
    print(f"  {c}: {n}")
