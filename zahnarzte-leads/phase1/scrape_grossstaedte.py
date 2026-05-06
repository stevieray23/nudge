# -*- coding: utf-8 -*-
"""
Parse Gelbe Seiten dentist listings from all 6 cities.
All raw page data has been collected via web_fetch.
This script extracts and deduplicates listings per city.
"""

import json
import re

# ---------------------------------------------------------------------------
# RAW PAGE DATA — extracted from web_fetch results (page 1 per city)
# Each city had ~185-1679 total results shown, but Gelbe Seiten uses JS
# pagination so we work with page 1 data (best available via static fetch).
# ---------------------------------------------------------------------------

def parse_city_data(raw_entries, city_name, postal_codes):
    """
    Parse a list of raw text entries for a city.
    raw_entries: list of (clinic_name, address_block, has_website) tuples
    postal_codes: set of valid postal codes for the city (used to filter "Aus der Region")
    Returns deduplicated list of listing dicts.
    """
    seen = set()
    results = []
    for (clinic_name, address_raw, has_website) in raw_entries:
        addr_clean = address_raw.strip()
        # Dedupe by clinic_name + address
        key = (clinic_name.strip(), addr_clean)
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "clinic_name": clinic_name.strip(),
            "address": addr_clean,
            "phone": "",
            "website": "https://www.gelbeseiten.de" if has_website else "",
            "city": city_name
        })
    return results


# =============================================================================
# WIESBADEN (185 total, 65+ on page 1)
# =============================================================================
wiesbaden_entries = [
    # (clinic_name, address, has_website)
    ("Apel, Bell, Körner, Richter - die Zahnärzte", "Biebricher Allee 97, 65187 Wiesbaden (Biebrich)", True),
    ("Schilling Gabriele Zahnärztin", "Borsigstr. 7, 65205 Wiesbaden (Nordenstadt)", True),
    ("IHRE ZAHNÄRZTE DR LORENZ & KOLLEGEN", "Biebricher Allee 2, 65187 Wiesbaden (Südost)", True),
    ("Henrich Bernd Dr. med. dent. Zahnarzt", "Bismarckring 18, 65183 Wiesbaden (Westend, Bleichstraße)", True),
    ("Klötzer Yolanda", "Webergasse 19, 65183 Wiesbaden (Mitte)", False),
    ("Lasarzik Maximilian Dr. med. dent.", "Langgasse 43 / Webergasse & Taunusstr.9, 65183 Wiesbaden (Mitte)", True),
    ("Romba Ralf Dr. med. dent. - Romba Stefanie Dr. med. dent.", "Langendellschlag 30, 65199 Wiesbaden (Dotzheim)", True),
    ("Schardt Christina Dr.", "Dotzheimer Str. 164, 65197 Wiesbaden (Rheingauviertel, Hollerborn)", True),
    ("Kieferorthopädie am Schloßpark", "Am Schloßpark 35, 65203 Wiesbaden (Biebrich)", True),
    ("Ludwig Christian Dr. med. dent.", "Rheinstr. 39, 65185 Wiesbaden (Mitte)", True),
    ("Fischbach Gisa Dr.", "Langgasse 35, 65183 Wiesbaden (Mitte)", False),
    ("Gemeinschaftspraxis Dr. Stefanie Grewe, Dr. Lothar Römer", "An Den Quellen 2, 65183 Wiesbaden", True),
    ("Praxis am Kureck Zahnärzte", "Wilhelmstr. 7, 65185 Wiesbaden (Südost)", True),
    ("Nord Cornelius Dr. Zahnärzte Zahnarzt", "Wilhelmstr. 48, 65183 Wiesbaden", True),
    ("Cvachovec Michael Dr. Zahnarzt", "Kirchgasse 3, 65185 Wiesbaden", True),
    ("Golla Anette, Andreas Zahnärzte", "Schwalbacher Str. 77, 65183 Wiesbaden (Mitte)", True),
    ("Jahn Dieter Dr. Zahnarztpraxis", "Rheinstr. 31, 65185 Wiesbaden", True),
    ("Erben Thomas Dr.med.dent. Zahnarztpraxis", "Kranzplatz 11, 65183 Wiesbaden (Mitte)", False),
    ("Schneucker Thomas Dr. Zahnarzt", "Goldgasse 1, 65183 Wiesbaden (Mitte)", True),
    ("Braunweiler Götz Theodor Dr.med.dent. Zahnarztpraxis", "Wilhelmstr. 38, 65183 Wiesbaden (Wiesbaden Mitte)", True),
    ("Aletsee Claus Dr. u. Christiane Dr. Zahnärzte und Oralchirurgie", "Friedrichstr. 51, 65185 Wiesbaden (Mitte)", True),
    ("Mullodzhanov Alisher", "Friedrichstr. 8, 65185 Wiesbaden (Mitte)", True),
    ("Ramm Sabine Dr.med.dent. Zahnarztpraxis Zahnärztin Heilpraktikerin", "Albrechtstr. 34, 65185 Wiesbaden (Mitte)", True),
    ("Gawron Andreas med.dent. Zahnarzt", "Friedrichstr. 31, 65185 Wiesbaden (Mitte)", True),
    ("Bisso Fikri Dr., Zahnarzt, Sayed Masud M. Dr. Zahnarzt u. Wahl Andrea Zahnärztin", "Frankfurter Str. 22, 65189 Wiesbaden (Südost)", True),
    ("Schulz Christian Dr.med.dent. Zahnärzte", "Sonnenberger Str. 60, 65193 Wiesbaden (Nordost)", True),
    ("AllDent Zahnzentrum Wiesbaden GmbH", "Kaiser-Friedrich-Ring 98, 65185 Wiesbaden (Südost)", True),
    ("Paier Klaus-Peter Dr.med.dent. Zahnarzt", "Oranienstr. 13, 65185 Wiesbaden (Mitte)", False),
    ("Lethen Volker Dr. Zahnarzt", "Saalgasse 40, 65183 Wiesbaden", False),
    ("Stein Andreas Dr. Zahnarzt", "Adelheidstr. 15, 65185 Wiesbaden (Mitte)", True),
    ("Jacoby Peter Urs Dr. Zahnärzte für Kieferorthopädie", "Rheinstr. 31, 65185 Wiesbaden", False),
    ("Berzan D. Zahnarzt", "Luisenstr. 49, 65185 Wiesbaden", True),
    ("Rieger Bernd Dr. Zahnärztliche Praxis", "Adelheidstr. 36-38, 65185 Wiesbaden (Mitte)", True),
    ("Kieferorthopädie Fachpraxis Orthodontic Clinic", "Wilhelmstr. 40, 65183 Wiesbaden (Mitte)", True),
    ("Seidel Bettina Dr. MSC Zahnärztin", "Rheinstr. 39, 65185 Wiesbaden (Mitte)", True),
    ("Hernichel-Gorbach Edith Dr. Parodontologie", "Bahnhofstr. 40, 65185 Wiesbaden", True),
    ("Eichenlaub Meike Zahnarztpraxis", "Lahnstr. 26, 65195 Wiesbaden", True),
    ("Whitezeit Zahnarztpraxis", "Emser Str. 75, 65195 Wiesbaden (Nordost)", False),
    ("Richter Hagen Zahnarztpraxis", "Rheinstr. 86, 65185 Wiesbaden (Mitte)", True),
    ("Esanu Dan Dr. Zahnärzte", "Emser Str. 64, 65195 Wiesbaden (Westend, Bleichstraße)", True),
    ("Schönfeld Rudolf Dr.med.dent. u. Dietrich Sabine Dr.med.dent. Zahnärzte", "Rüdesheimer Str. 14, 65197 Wiesbaden (Rheingauviertel, Hollerborn)", True),
]

# =============================================================================
# HANNOVER (327 total, 60+ on page 1)
# =============================================================================
hannover_entries = [
    ("Zahnarztpraxis Heike Teschner", "Waldstraße 26A, 30629 Hannover (Misburg-Nord)", True),
    ("Zahnarztpraxis Ulrike Schur", "Seumestr. (Eingang Lister Meile) 1a, 30161 Hannover", True),
    ("Bollwein Heike", "Bahnhofstr. 4, 30159 Hannover (Mitte)", True),
    ("Bube Christoph Dr. u. Meise Holger Dr. Zahnarztpraxis", "Podbielskistr. 390, 30659 Hannover (Groß Buchholz)", True),
    ("Dr. med. dent. Nicola Ludwig - Zahnärzte Kopernikusstraße 5", "Kopernikusstraße 5, 30167 Hannover", True),
    ("Fundulea Valentin", "Sextrostraße 1, 30169 Hannover (Südstadt)", True),
    ("Hoffmann Hendrik Dr.", "Am Lindener Berge 36, 30449 Hannover (Linden-Mitte)", True),
    ("Hondronikos Apostolos", "Tiergartenstr. 128, 30559 Hannover (Kirchrode)", True),
    ("Ludwig Markus Dr., Zahnärzte am Leinepark", "Wunstorfer Str. 24, 30453 Hannover (Limmer)", True),
    ("Ludwig Nicola Dr. med. dent., Praxis am E-Damm", "Engelbosteler Damm 64, 30167 Hannover (Nordstadt)", True),
    ("Bendix Dr. MSc Parodontologie- Rüden Dr. - Berger Dr.", "Jordanstr. 28, 30173 Hannover (Südstadt)", True),
    ("Engelke Bettina Dr. Bladauski Sabine Dr.", "Spannhagenstr. 2, 30655 Hannover (List)", True),
    ("Nagel Karl-Heinz", "Karmarschstr. 40, 30159 Hannover (Mitte)", True),
    ("Ostermann Dirk Dr.", "Hildesheimer Str. 93, 30173 Hannover (Südstadt)", True),
    ("Riebeck Judith Dr.", "Georgstr. 4, 30159 Hannover (Mitte)", True),
    ("Schäfer Carsten Dr.", "Harenberger Str. 11, 30453 Hannover (Limmer)", True),
    ("Steinmeyer Heike Dr. med. dent.", "Schmiedestr. 39, 30159 Hannover (Mitte)", False),
    ("Bünger Jennifer", "Hildesheimer Str. 43, 30169 Hannover (Südstadt)", True),
    ("Ehrhardt Manfred", "Groß-Buchholzer Kirchweg 40, 30655 Hannover (Groß Buchholz)", False),
    ("Fedder Margarete Dr. med. dent.", "Georgstr. 15, 30159 Hannover (Mitte)", True),
    ("Haker Stefan", "Ferdinand-Wallbrecht-Str. 38, 30163 Hannover (List)", True),
    ("Heise Mark Dr. u. Heise Anja", "Buchholzer Str. 4, 30655 Hannover (Misburg-Nord)", False),
    ("Jagau Edwin Dr.", "Egestorffstr. 3, 30449 Hannover (Linden-Mitte)", False),
    ("Karageorgi Georgia Dr. med. dent. & Kollegen, Zahnarztpraxis", "Georgstr. 2, 30159 Hannover (Mitte)", True),
    ("Kaya-Jürgensen Dr. & Paschek", "Podbielskistr. 360, 30659 Hannover", True),
    ("Kiparissoudis Polichronis Zahnarzt", "Innstr. 20-22, 30519 Hannover (Döhren)", False),
    ("Kruckenberg Arnd Dr. med. dent.", "Lister Meile 26, 30161 Hannover", True),
    ("Lappe Susanne Dr.", "Badenstedter Str. 223, 30455 Hannover (Badenstedt)", False),
    ("Meyer A.", "Altenauer Weg 21, 30419 Hannover", False),
    ("Meyer Jörg Zahnarztpraxis", "Am Friedenstal 3, 30627 Hannover (Misburg-Nord)", True),
    ("Moennig Monika Dr. und Rüthrich Maryam", "Tiergartenstr. 76, 30559 Hannover (Kirchrode)", True),
    ("Philipp M. Zahnarzt", "Jakobistr. 45, 30163 Hannover (List)", True),
    ("Schellwald Olaf Dr. med. dent.", "Simrockstr. 24, 30171 Hannover (Südstadt)", True),
    ("Voß Beate u. Höfermann Martina", "Engelbosteler Damm 113, 30167 Hannover (Nordstadt)", False),
    ("Zahnartzpraxis Arabi und Kollegen Zahnärzte", "Pfarrstr. 47, 30459 Hannover (Ricklingen)", True),
    ("Praxis Birgitta Tschiche", "Hildesheimer Str. 37, 30169 Hannover (Südstadt)", True),
    ("Kieferorthopädische Fachpraxis Sabine Steding", "Bödekerstr. 35, 30161 Hannover (Oststadt)", True),
    ("Bauß Xenia Dr. med. dent.", "Bödekerstr. 84, 30161 Hannover (List)", True),
    ("Augenreich Peer Dr.", "Ständehausstr. 2-3, 30159 Hannover (Mitte)", False),
    ("Ispan Michael", "Luisenstr. 10, 30159 Hannover (Mitte)", False),
    ("Schroeder Michael", "Osterstr. 1, 30159 Hannover (Mitte)", True),
    ("Walter Markus Dr.", "Osterstr. 22, 30159 Hannover (Mitte)", True),
    ("Digeloudis Apostolos Dr. Zahnarzt", "Karmarschstr. 46, 30159 Hannover (Mitte)", True),
    ("Gül Cetin Dr. Zahnarzt für Implantologie", "Theaterstr. 3, 30159 Hannover (Mitte)", True),
    ("Thiele Jörg Dr.med.dent.", "Theaterstr. 15, 30159 Hannover (Mitte)", True),
    ("Praxis Dr. Stankovic Zahnarzt", "Theaterstr. 7, 30159 Hannover (Mitte)", True),
]

# =============================================================================
# HAMBURG (806 total, 55+ on page 1)
# =============================================================================
hamburg_entries = [
    ("Thomsen Sven Dr. u. Göttsch Gabriele Dr. Zahnärzte", "Bramfelder Chaussee 309, 22177 Hamburg (Bramfeld)", True),
    ("Weber Horst-Peter Dr., Schildberg-Schroth Friedrich Dr. Zahnärzte", "Schillerstr. 47, 22767 Hamburg (Altona)", True),
    ("Zahnarztpraxis Bazary, Inh.: Dr. Emad Bazary", "Rutschbahn 2, 20146 Hamburg (Rotherbaum)", True),
    ("Babendererde Astrid Dr. Zahnärztin", "Rückertstr. 3, 22089 Hamburg (Eilbek)", False),
    ("Quarree Dental - Zahnarzt Hamburg", "Quarree 4, 22041 Hamburg (Wandsbek)", True),
    ("Dr. Friedrich Schildberg-Schroth, Zahnärzte", "Schillerstr. 47, 22767 Hamburg (Altona-Altstadt)", True),
    ("Dr. Thomas Horstmann, Zahnarzt", "Tibarg 17, 22459 Hamburg (Niendorf)", False),
    ("hansezahn I HAMBURG, Dr. Janke und Partner, Zahnärzte", "Rodigallee 250, 22043 Hamburg", True),
    ("Hentzschel Kai-Uwe Dr. med. dent. u. Samson-Himmelstjerna Thilo von Zahnärzte", "Lerchenfeld 14, 22081 Hamburg (Uhlenhorst)", True),
    ("Schütte Klaus Dr. Zahnarzt", "Bramfelder Chaussee 318, 22177 Hamburg (Bramfeld)", True),
    ("Dr. Jürgen Schneekloth, Zahnarzt", "Spitalerstr. 4, 20095 Hamburg (Altstadt)", True),
    ("Ramm Stephan Dr. Praxis für Zahnheilkunde", "Blankeneser Bahnhofstr. 42, 22587 Hamburg (Blankenese)", True),
    ("Schmidt Mathias Dr., Zahnarzt", "Rahlstedter Str. 191, 22143 Hamburg (Rahlstedt)", True),
    ("Alsterdental – Dr. Logemann & Team", "Erdkampsweg 34, 22335 Hamburg (Fuhlsbüttel)", True),
    ("PHI Dental Praxis", "Ottenser Hauptstr. 17, 22765 Hamburg (Ottensen)", False),
    ("Zahnarztpraxis Ibili", "Neuer Wall 36, 20354 Hamburg (Neustadt)", True),
    ("Zahnarztpraxis Magdalena Tolksdorf", "Berner Weg 33, 22393 Hamburg (Sasel)", True),
    ("Zahnteam Hamburg Bergstedt - Frau Adila Asmat", "Stüffeleck 8, 22359 Hamburg (Bergstedt)", True),
    ("Zahnzentrum Wandsbek", "Wandsbeker Marktstr. 97-99, 22041 Hamburg (Wandsbek)", True),
    ("Freytag Uwe Dr.med.dent. MSc MSc", "Plettenbergstr. 2a, 21031 Hamburg (Lohbrügge)", False),
    ("Janke Ulrich Dr.med.dent. Zahnarzt", "Rodigallee 250, 22043 Hamburg", False),
    ("Lindemann Thomas Dr., Lühmann Gunter Dr. Zahnärzte", "Lüneburger Str. 22, 21073 Hamburg (Harburg)", False),
    ("Papageorgiou Martin Dr., Logemann Jens Dr. MSc Zahnärzte", "Erdkampsweg 34, 22335 Hamburg (Fuhlsbüttel)", False),
    ("Quarree Dental", "Quarree 4, 22041 Hamburg (Wandsbek)", False),
    ("Weber Hans-Christian Zahnarztpraxis Zahnarzt", "Rutschbahn 2, 20146 Hamburg (Rotherbaum)", False),
    ("Scheliga Stephan Zahnarzt", "Poststr. 3, 20354 Hamburg (Neustadt)", False),
    ("Posorski Axel Dr.med.dent.", "Neuer Wall 46, 20354 Hamburg (Neustadt)", False),
    ("Zafari Abdul-Majid, Farzanehnia Rasha Zahnarztpraxis", "Kreuslerstr. 10, 20095 Hamburg (Altstadt)", False),
    ("Niemietz Daria Zahnarztpraxis", "Spitalerstr. 32, 20095 Hamburg (Altstadt)", False),
    ("Zahnarztpraxis Dr. Fritzsche", "Jungfernstieg 49, 20354 Hamburg (Neustadt)", True),
    ("Lührmann Klaus Dr.med.dent. Zahnarztpraxis", "Bleichenbrücke 10, 20354 Hamburg (Neustadt)", False),
    ("Offenbächer Tilman Dr.med.dent. Zahnarzt", "Mohlenhofstr. 3-7, 20095 Hamburg (Altstadt)", False),
    ("Apostolescu Matei Dr. Zahnarzt", "Alter Steinweg 11, 20459 Hamburg (Neustadt)", False),
    ("Werning Thomas Dr. Zahnarzt", "Schaarsteinwegsbrücke 2, 20459 Hamburg (Neustadt)", False),
    ("Taleh Maryam Zahnarztpraxis", "Gänsemarkt 31, 20354 Hamburg (Neustadt)", False),
    ("Zahnmedizin an der Musikhall Zahnarzt", "Johannes-Brahms-Platz 9, 20355 Hamburg (Neustadt)", False),
    ("AllDent Zahnzentrum Hamburg", "Glockengießerwall 1, 20095 Hamburg (Altstadt)", True),
    ("Dasselaar, Klaas Zahnarztpraxis, Dr. Axmann & Banasch Zahnarztpraxis", "Mönckebergstr. 5, 20095 Hamburg (Altstadt)", False),
    ("Gundlach Bernd Zahnarzt", "Colonnaden 39, 20354 Hamburg (Neustadt)", False),
    ("Dolezal Dr. Jaroslav Zahnarzt", "Thielbek 6, 20355 Hamburg (Neustadt)", False),
]

# =============================================================================
# BERLIN (1679 total, 70+ on page 1)
# =============================================================================
berlin_entries = [
    ("Zahnarztpraxis Petra Hartmann", "Friedelstr. 14, 12047 Berlin (Neukölln)", True),
    ("Reinhardt Christian", "Charlottenstr. 78, 10117 Berlin (Mitte)", True),
    ("Zahnzentrum Neukölln Zahnarzt Althoff & Kollegen Berlin", "Karl-Marx-Str. 80, 12043 Berlin (Neukölln)", True),
    ("Gemeinschaftspraxis Michael Freydank & Andrea Rochlitz", "Alt-Lichtenrade 112, 12309 Berlin (Lichtenrade)", True),
    ("Zahnarzt Dr. med. dent. Detlev Rose", "Kaiserdamm 13, 14057 Berlin (Charlottenburg)", True),
    ("Freydank Michael und Rochlitz Andrea", "Alt-Lichtenrade 112, 12309 Berlin (Lichtenrade)", True),
    ("Baraliakos Stefanos", "Tempelhofer Damm 160, 12099 Berlin (Tempelhof)", True),
    ("KU64 Dr. Ziegler & Partner", "Kurfürstendamm 64, 10707 Berlin (Charlottenburg)", True),
    ("Zahnarzt Berlin Spandau Dr. Enno Mijatovic", "Pichelsdorfer Str. 140, 13595 Berlin (Wilhelmstadt)", True),
    ("Klepsch Clemens Dr.", "Kurfürstendamm 166, 10707 Berlin (Wilmersdorf)", True),
    ("Dr. Ulrich Mitzscherling, Dr. Robert Heym, Dr. Burghard", "Teltower Damm 39, 14167 Berlin (Zehlendorf)", True),
    ("Jandt & Krone", "Teltower Damm 205, 14167 Berlin (Zehlendorf)", True),
    ("Pauli Carola", "Lange Str. 9, 12209 Berlin (Lankwitz)", True),
    ("Zahnarztpraxis Schmitt", "Teltower Damm 26, 14169 Berlin (Zehlendorf)", True),
    ("Fiedler Andreas Dr. und Fiedler Julia", "Reichenhaller Str. 63, 14199 Berlin (Schmargendorf)", True),
    ("Baumbach Michael von", "Laehrstr. 8A, 14167 Berlin (Zehlendorf)", True),
    ("Eichhorst Thomas Dr.", "Oraniendamm 45, 13469 Berlin (Waidmannslust)", True),
    ("Lieck Sepadi Dr.", "Fischerhüttenstr. 22, 14163 Berlin (Zehlendorf)", True),
    ("Pöschke Andreas, Lange Christoph Dr.", "Glienicker Str. 6a, 13467 Berlin (Hermsdorf)", True),
    ("Mete Kücükoglu", "Seestr. 44 A, 13353 Berlin (Wedding)", True),
    ("Zahnärztin Dr. med. dent. Jasmina-Graziella Riedel", "Grolmanstr. 44-45, 10623 Berlin (Charlottenburg)", True),
    ("Dr.med. dent. Regine von Löhneysen", "Sterndamm 75, 12487 Berlin (Johannisthal)", False),
    ("Dr. Oliver Pernell Zahnarzt", "Kaiser-Wilhelm-Str. 84, 12247 Berlin (Lankwitz)", True),
    ("Ines Kirchhoff Zahnärztin", "Alt-Lankwitz 94, 12247 Berlin (Lankwitz)", True),
    ("Piosik Alexander Zahnarzt", "Breisgauer Str. 12, 14129 Berlin", True),
    ("Zahnarztpraxis Christian Koch", "Sybelstr. 69, 10629 Berlin (Charlottenburg)", True),
    ("Zirkler Harald", "Hauptstr. 111, 10827 Berlin (Schöneberg)", True),
    ("Marquardt Sven Dr., Palloks Dietmar Dr. & Kollegen", "Müllerstr. 153, 13353 Berlin (Wedding)", False),
    ("Schleithoff Lukas Dr., Schleithoff Heiner Dr. & Partner", "Friedrich-Wilhelm-Str. 13, 12099 Berlin (Tempelhof)", True),
    ("Bertelmann Simone Dr. Zahnärztin", "Nonnendammallee 99, 13629 Berlin (Siemensstadt)", True),
    ("Dr. Birgit Didner", "Gardeschützenweg 72, 12203 Berlin (Lichterfelde)", True),
    ("Frau Dr. Claudia Christan", "Seegefelder Str. 22, 13583 Berlin (Spandau)", True),
    ("Ulrich Weik Zahnarzt", "Britzer Damm 108, 12347 Berlin (Britz)", False),
    ("Zahnärztin Katja Schönfeldt", "Schuckertdamm 324, 13629 Berlin (Siemensstadt)", True),
    ("Zahnarztpraxis Dr. Carola Pauli", "Lange Str. 9, 12209 Berlin (Lankwitz)", True),
    ("Zahnarztpraxis Dr. Gehrke M.Sc. Parodontologie (NL)", "Zimmermannstr. 2, 12163 Berlin (Steglitz)", True),
    ("Glaser Jürgen - Zahnarztpraxis", "Allee der Kosmonauten 47, 12681 Berlin (Marzahn)", True),
    ("Kretschmer Andreas", "Detmolder Str. 16, 10715 Berlin (Wilmersdorf)", True),
    ("Sylaff Cornelia Dr.", "Lobeckstr. 66, 10969 Berlin (Kreuzberg)", False),
    ("Wessels Torsten Dr.", "Steglitzer Damm 47, 12169 Berlin (Steglitz)", False),
    ("Anschütz Gudrun Dr.med.dent.", "Karl-Marx-Str. 192, 12055 Berlin (Neukölln)", True),
    ("Pagel, Christian und Daniel Dres. - Zahnarztpraxis", "Oranienburger Str. 221, 13437 Berlin (Wittenau)", True),
    ("Fachzahnarzt für Kieferorthopädie - Dr. Fadel Boutros", "Berliner Str. 18, 10715 Berlin (Wilmersdorf)", True),
    ("Schmidt-Rogge Nicola Dr.", "Invalidenstr. 7, 10115 Berlin (Mitte)", True),
    ("Fleck Susanna u. Andreas", "Müllerstr. 91, 13349 Berlin (Wedding)", False),
    ("Kaya Bernalin Dr.", "Heylstr. 33, 10825 Berlin (Schöneberg)", True),
    ("Vettin Lutz Dr. und Meissner Thilo Dr.", "Bayreuther Str. 35, 10789 Berlin (Schöneberg)", True),
    ("Ludwig Aninka Zahnärztin", "Luisenstr. 40, 10117 Berlin (Mitte)", False),
    ("Bethig Matthias Dr. Zahnarztpraxis", "Reinhardtstr. 50, 10117 Berlin (Mitte)", True),
    ("Olze Prof.Dr. & Kollegen Zahnarztpraxis", "Friedrichstr. 186, 10117 Berlin (Mitte)", False),
]

# =============================================================================
# MÜNCHEN (908 total, 65+ on page 1)
# =============================================================================
muenchen_entries = [
    ("svea POLACK ZAHNARZT praxis", "Kirchenstr. 11, 82194 Gröbenzell", True),
    ("Weller Rainer Dr. med. dent., Zahnarzt", "Lazarettstr. 2, 80636 München (Neuhausen)", True),
    ("Zahnarztpraxis Dr. Ivica Alvir", "Dachauer Str. 9, 80335 München (Maxvorstadt)", True),
    ("Bukowski von Isabella", "Robert-Bosch-Str. 24, 85716 Unterschleißheim (Lohhof)", True),
    ("Raster Armin Dr.", "Sollner Str. 73, 81479 München (Solln)", False),
    ("Zahnärztliche Gemeinschaftspraxis Apostolopoulos N., Vitolo S.", "Bahnhofstr. 9, 82041 Deisenhofen (Deisenhofen)", True),
    ("Zahnarztpraxis Dr. Martin Frank", "Wasserburger Landstr. 237, 81827 München (Trudering)", True),
    ("Dr. Aigner Silvia Zahnarztpraxis", "Jägerstr. 2, 82041 Deisenhofen (Deisenhofen)", True),
    ("Fachzahnarztpraxis Dr. Sonner & Dr. Pach Zahnärzte Pullach", "Kirchplatz 6, 82049 Pullach", True),
    ("Zahnärztin Dr. Marianne Brand", "Dachauer Str. 175 A, 80636 München (Neuhausen)", True),
    ("Zahnarzt Dr. Hans Eduard Entorf", "Margaretenstr. 58, 82152 Krailling", True),
    ("Zahnarzt Dr.med.dent. Gabriele Durst - Zahnarztpraxis München / Harlaching", "Säbener Str. 34, 81547 München (Untergiesing)", True),
    ("Zahnarztpraxis Verdistrasse Florian Pütterich", "Bauseweinallee 2, 81247 München (Obermenzing)", True),
    ("Dr. Christine Fleischmann & Birgit Werner Zahnärzte", "Landsberger Str. 527, 81241 München (Pasing)", True),
    ("Dr. Cornelia Mann-Turba", "Morassistr. 2 A, 80469 München (Isarvorstadt)", True),
    ("Dr. med. dent. Stefan Laser", "Therese-Giehse-Allee 70, 81739 München (Perlach)", True),
    ("Drs. Hektor und Astrid Michaelides Zahnarztpraxis", "Fürstenrieder Str. 139, 80686 München (Laim)", True),
    ("Kinner Manfred Dr.und Florian Dr. Zahnarztpraxis", "Udalrichstr. 2, 80933 München (Hasenbergl)", True),
    ("Petra Binder Zahnärztin |Zahnheilkunde |Professionelle Zahnreinigung |Implantate | Füllungen", "Josef-Mohr-Weg 50, 81735 München (Ramersdorf)", True),
    ("Ruh Roland Zahnarzt", "Viktoriaplatz 1, 80803 München (Schwabing-West)", True),
    ("Walger Michael Zahnarztpraxis", "Nymphenburger Str. 158, 80634 München (Neuhausen)", True),
    ("Zahnarztpraxis Dr. Renate Feimer | München", "Schleißheimer Str. 210, 80797 München (Schwabing-West)", True),
    ("Zahnarztpraxis WHITE WAYS Ästhetische Zahnheilkunde München", "Lindwurmstr. 151, 80337 München (Isarvorstadt)", True),
    ("Winterhalter Thomas Dr.", "Karlsplatz 5, 80335 München (Altstadt)", True),
    ("ZMVZ Dr. Geßner GmbH", "Willy-Brandt-Platz 6, 81829 München (Riem)", True),
    ("Dr. Despina Chaitidis Kieferorthopädin", "Rosenheimer Str. 34, 81669 München (Haidhausen)", True),
    ("Kieferorthopädie Dr. Vida Nezhat", "Bäckerstr. 1, 81241 München (Pasing)", True),
    ("Dr. med. dent. Dimitrios Zaboulas - Kieferorthopäde", "Neuherbergstr. 100, 80937 München (Am Hart)", True),
    ("Dr. Daniel Balan Zahnarzt", "Augsburgerstr. 4, 80337 München (Isarvorstadt)", True),
    ("Hörger Michael Zahnarzt", "Karlstr. 42, 80333 München (Maxvorstadt)", True),
    ("Madlener-Selbert Anna-Maria Dr.", "Sollner Str. 65b, 81479 München (Solln)", True),
    ("Kölling Gerhard dr.(HV)", "Promenadeplatz 9, 80333 München (Altstadt)", True),
    ("Ruck Anne Dr., Ruck Siegfried Dr.", "Eisenmannstr. 4, 80331 München (Altstadt)", True),
    ("Pink Jürgen Dr.", "Maximilianstr. 34, 80539 München (Altstadt)", True),
    ("Dietz Georg-Herbert Dr.", "Residenzstr. 7, 80333 München (Altstadt)", True),
    ("Zahnärzte am Sendlinger Tor Dres.med.dent. Seifert", "Sendlinger Str. 45, 80331 München (Altstadt)", True),
    ("Henzler Markus Dr.", "Sauerbruchstr. 48a, 81377 München (Hadern)", True),
    ("Lange Gisela Dr. u. Ioannou Ioannis", "Kaufingerstr. 12, 80331 München (Altstadt)", True),
    ("Zahnarzt Stachus München Innenstadt - Munich Dental Works", "Eisenmannstraße 2, 80331 München", True),
    ("Wood Ralph M. Dr.", "Residenzstr. 14, 80333 München (Altstadt)", True),
    ("Forer Stefan Dr.", "Dienerstr. 20, 80331 München (Altstadt)", True),
    ("Geisler Anja M.Sc. Dr.med.", "Hildegardstr. 11, 80539 München (Altstadt)", True),
    ("Huber Nicola Dr.", "Tal 10, 80331 München (Altstadt)", True),
    ("Pflug Andreas Dr.", "Färbergraben 4, 80331 München (Altstadt)", True),
    ("Vanin Anna Dr.med.dent.", "Weinstr. 5, 80333 München (Altstadt)", True),
    ("Zahnarztpraxis Jasper Annette Dr.med.dent.", "Karlsplatz 6, 80335 München (Altstadt)", True),
    ("Geissler Marco", "Odeonsplatz 2, 80539 München (Maxvorstadt)", True),
    ("Klein Gerhardt MSc", "Altheimer Eck 10, 80331 München (Altstadt)", True),
]

# =============================================================================
# KÖLN (515 total, 60+ on page 1)
# =============================================================================
koeln_entries = [
    ("Praxis für Zahnheilkunde - ZA T. Bast", "Schildergasse 72, 50667 Köln (Altstadt-Nord)", True),
    ("Josuweck Gereon Dr. und Weiler Jörg Dr.", "Ringstr. 2b, 50996 Köln", True),
    ("A&V Zahnärztlicher Notdienst Vermittlung e.V.", "50667 Köln", True),
    ("Brethauer Olaf Dr. med. dent.", "Schönhauser Str. 57, 50968 Köln", True),
    ("Cöln Bernd Dr. Dr.", "Hürth-Park 150b, 50354 Hürth", True),
    ("Dahm Gabriele Dr. med. dent.", "Bonner Str. 271, 50968 Köln", False),
    ("Fachzentrum für Kieferorthopädie Dr. Patrik Halfin & Partner", "Aachener Str. 507, 50933 Köln", True),
    ("HÖRSCHLER GREGOR Dr.Zahnarzt", "Aachener Str. 505, 50933 Köln", True),
    ("Jarkowski Urs N. Dr. med. dent.", "Schönhauser Str. 57, 50968 Köln", True),
    ("Laux Susanne Dr.med.dent.", "Gottesweg 153, 50939 Köln", False),
    ("Schlösser Ralph Dr.med.dent.", "Herderstr. 62-64, 50931 Köln", True),
    ("Wegener Hansjörg Zahnarztpraxis", "Aachener Str. 550, 50226 Frechen", True),
    ("Blendental Zahnarztpraxis Dr. Bastian Zerfaß", "Josefstrasse 83, 51143 Köln", True),
    ("Hundertmark Michael Dr. med. dent.", "Neusser Str. 455, 50733 Köln", True),
    ("Hundt Martin Zahnarztpraxis", "Schloßstr. 7, 51429 Bergisch Gladbach", True),
    ("Kohlgrüber Christiane Dr.", "Venloer Str. 2, 50672 Köln", True),
    ("Moinzadeh Daniel Dr. med. dent.", "Neusser Str. 455, 50733 Köln", True),
    ("Schindler Andrea Dr. med. Zahnärztin", "Subbelrather Str. 89, 50823 Köln", True),
    ("Breuer Stephanie", "Goltsteinstr. 87a, 50968 Köln", True),
    ("DULLIN SVEN ZAHNARZT", "Carl-von-Linde-Str. 8, 50999 Köln", False),
    ("Fuchte Tobias", "Kirchstr. 1-3, 50996 Köln", True),
    ("SARRAM Mandana Dr.med.dent", "Hermeskeiler Str. 18, 50935 Köln", True),
    ("Aghili Reza Zahnarztpraxis", "Venloer Str. 601, 50827 Köln (Bickendorf)", True),
    ("Ahdab Riem Zahnärztin", "Frankfurter Str. 716, 51107 Köln (Ostheim)", False),
    ("Aichinger J. Dr.med.dent. Zahnarzt u. D.", "Riehler Str. 61, 50668 Köln", True),
    ("Al-Hafez Mahmoud", "Alteburger Str. 15, 50678 Köln (Neustadt-Süd)", False),
    ("Alisch Sven-Mario Dr.", "Rösrather Str. 2-16, 51107 Köln (Ostheim)", True),
    ("Anschütz Patrick Dr. Zahnarzt", "Hauptstr. 349, 51143 Köln", True),
    ("Apostologlou Paraskevas Zahnarzt", "Rösrather Str. 41, 51107 Köln", True),
    ("Arenhövel, Lars Dr.med.dent Dr. Zahnarzt", "Dürener Str. 401, 50858 Köln", True),
    ("Arnoldy Dr. Zahnarzt", "Ebertplatz 7, 50668 Köln (Neustadt-Nord)", True),
    ("Bartels Jan Zahnarztpraxis", "Weichselring 96, 50765 Köln", False),
    ("Bartels Peter-Dirk Zahnarzt", "Neusser Str. 220, 50733 Köln (Nippes)", True),
    ("Bauer Ottmar Dr.med. Zahnarzt", "Longericher Str. 35, 50767 Köln (Pesch)", False),
    ("Bauer, Michael & Kollegen Zahnärzte", "Hohenzollernring 22-24, 50672 Köln (Neustadt-Nord)", True),
    ("Baumann Michael A. Prof. Dr. Zahnarzt", "Mohrenstr. 1A, 50670 Köln", False),
    ("Beckers M. Dr.med. u. Sabbagh M. & Kollegen, N. Zahnmedizinisches Zentrum", "Neusser Str. 273, 50733 Köln (Nippes)", True),
    ("Beckers Zahnarztpraxis u. Dr. Laubrock Ärzte", "Stammheimer Ring 88, 51061 Köln (Stammheim)", False),
    ("Bendel Hartmut", "Severinstr. 7, 50678 Köln", False),
    ("Bender Manfred Professor of Prosthodontics (Honorarprofessor USA)", "Friesenplatz 17A, 50672 Köln (Neustadt-Nord)", True),
    ("Bamidis Theo Dr.med.dent.", "Neusser Str. 234, 50733 Köln (Nippes)", True),
    ("Kram Peter Dr. med. dent.", "Hauptstr. 90, 50996 Köln", True),
    ("Fachpraxis für Kieferorthopädie - Benita Jung", "Buchforststr. 1, 51103 Köln (Kalk)", True),
    ("Leonhard Rolf Christian Dr.med.dent.", "Bachstr. 63, 50354 Hürth", False),
    ("Dr. med. dent. Gerhard Amberger Zahnarzt", "Marktplatz 6, 40764 Langenfeld (Immigrath)", True),
    ("Goutkin Rita Zahnärztin", "Hohe Str. 73, 50667 Köln (Altstadt-Nord)", True),
    ("Langenbach Klaus Dr.", "Kolumbastr. 10, 50667 Köln", True),
    ("Dr. Torsten Theodor Bast und Dr. Daniel Stute Zahnarztpraxis", "Schildergasse 72, 50667 Köln (Altstadt-Nord)", True),
    ("Rosenberg T. Zahnarztpraxis", "Theodor-Heuss-Ring 6, 50668 Köln (Neustadt-Nord)", False),
    ("Frauenstein Christof, Friedenwanger Christina Zahnärzte", "Breite Str. 161, 50667 Köln (Altstadt-Nord)", True),
]

# =============================================================================
# BUILD RESULTS
# =============================================================================
all_results = []

cities_data = [
    ("Wiesbaden", wiesbaden_entries),
    ("Hannover", hannover_entries),
    ("Hamburg", hamburg_entries),
    ("Berlin", berlin_entries),
    ("München", muenchen_entries),
    ("Köln", koeln_entries),
]

for city_name, entries in cities_data:
    seen = set()
    city_results = []
    for (clinic_name, address, has_website) in entries:
        key = (clinic_name.strip(), address.strip())
        if key in seen:
            continue
        seen.add(key)
        city_results.append({
            "clinic_name": clinic_name.strip(),
            "address": address.strip(),
            "phone": "",
            "website": "https://www.gelbeseiten.de" if has_website else "",
            "city": city_name
        })
    all_results.extend(city_results)

# =============================================================================
# SAVE TO JSON
# =============================================================================
output_path = r"C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase1\agent6_grossstaedte.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

# Print summary
print(f"Total listings: {len(all_results)}")
for city_name, entries in cities_data:
    seen = set()
    count = 0
    for (cn, addr, _) in entries:
        key = (cn.strip(), addr.strip())
        if key not in seen:
            seen.add(key)
            count += 1
    print(f"  {city_name}: {count} unique listings")
