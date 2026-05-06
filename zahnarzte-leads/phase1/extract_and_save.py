#!/usr/bin/env python3
"""
Parse dentist listings from collected Gelbe Seiten text data and save to JSON.
"""

import json
import re
import os

# City data - raw text from web_fetch results (page 1 only)
# Note: Pagination via URL doesn't work for Gelbe Seiten (JS-rendered),
# so data is limited to first page (~50-60 listings per city)

CITY_DATA = {
    "Gelsenkirchen": """[Ärzte für Zahnheilkunde Dr. Klaus Dohle

 5,05.0

 10 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/4e66d69f-d3e7-4f4e-b366-200d4880dace)

 Hochstr. 36,
 45894 Gelsenkirchen
 (Buer)
 8,1 km

 Geschlossen
  – Öffnet um 16:00

	Webseite

 [Kaschynski Andreas

 4,04.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/23923350-ca4b-43b9-957e-81452a965c4f)

 Bochumer Str. 124,
 45886 Gelsenkirchen
 (Ückendorf)
 1,8 km

 Geschlossen
  – Öffnet um 14:30

	Webseite

 [Tavrovski Ilia Dr.

 5,05.0

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/82c5cc32-2dcd-42c5-abe8-f2bc8eef3f38)

 Husemannstr. 53,
 45879 Gelsenkirchen
 (Altstadt)
 457 m

 Geöffnet
  – Schließt um 18:30

	Webseite

 [Kaldenbach Christian Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/076cb52a-8dfc-4ec1-a2a3-1a13d6d1435c)

 Horster Str. 75,
 45897 Gelsenkirchen
 (Buer)
 7,6 km

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Dohle Klaus

 5,05.0

 10 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/4e66d69f-d3e7-4f4e-b366-200d4880dace)

 Hochstr. 36,
 45894 Gelsenkirchen
 (Buer)
 8,1 km

 Geschlossen
  – Öffnet um 16:00

	Webseite

 [Kaldenbach Christian Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d4f3ebf2-ab9b-4c9c-ab38-ba6a6b2b6fd8)

 Horster Str. 75,
 45897 Gelsenkirchen
 (Buer)
 7,6 km

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Kaschynski Andreas Zahnarzt

 4,04.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/23923350-ca4b-43b9-957e-81452a965c4f)

 Bochumer Str. 124,
 45886 Gelsenkirchen
 (Ückendorf)
 1,8 km

 Geschlossen
  – Öffnet um 14:30

	Webseite

 [Dr. med. dent. Julia Becker

 5,05.0

 1 Bewertung

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)

	Dr. med. dent. Julia Becker ist Ihre Spezialistin für moderne Kieferorthopädie. Wir bieten individue...](https://www.gelbeseiten.de/gsbiz/f401e5d4-340b-4166-9d32-684f957dcd84)

 Goldbergplatz 1,
 45894 Gelsenkirchen
 (Buer)
 7,9 km

 Geöffnet
  – Schließt um 17:30

	Webseite

 [Orzelski Roger Dr.med.dent. Zahnarzt

 5,05.0

 9 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/bdfed35a-dad0-4f0c-829d-8f7742bec43e)

 Bahnhofstr. 12,
 45879 Gelsenkirchen
 (Altstadt)
 252 m

 Geöffnet
  – Schließt um 18:00

 [Wenzel Izabela Zahnärztin

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/57191af3-ecc2-4b7b-8671-cd1c5c467588)

 Ebertstr. 20,
 45879 Gelsenkirchen
 (Altstadt)
 39 m

	Webseite

 [Braun Anneliese Dr. Zahnärzte

 5,05.0

 9 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7988e4d6-a8db-440c-afd5-b96c2a8daf28)

 Dickampstr. 7-9,
 45879 Gelsenkirchen

 595 m

 [Zahnarztpraxis Dr. Carl Walter Kreitz

 5,05.0

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1eae1958-13c5-4ebc-8f31-de65bcff729c)

 Wanner Str. 38,
 45888 Gelsenkirchen
 (Bulmke-Hüllen)
 742 m

	Webseite

 [Heimann-Langner Elka Zahnärztin

 4,24.2000003

 13 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e03b15a8-570d-404b-96df-94e08a8cbe76)

 Bahnhofstr. 68,
 45879 Gelsenkirchen
 (Altstadt)
 603 m

 [Grüter Klaus Zahnarzt

 4,84.8

 16 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/5e39dac7-a0a0-493e-9908-43c89ab19015)

 Magdeburger Str. 64,
 45881 Gelsenkirchen
 (Schalke)
 1,4 km

 Geschlossen
  – Öffnet um 14:00

 [Grüter Klaus Zahnarzt

 4,84.8

 16 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/5498e6c3-581f-405a-bdf8-79fd4ca83c46)

 Magdeburger Str. 64,
 45881 Gelsenkirchen
 (Schalke)
 1,4 km

 Geschlossen
  – Öffnet um 14:00

 [Lauer W. Dr.med.dent. & Lauer D. Dr.med.dent. Zahnärzte

 5,05.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ecdc4899-684e-46bd-92f8-3a8ea8c54ec7)

 Kurt-Schumacher-Str. 81,
 45881 Gelsenkirchen
 (Schalke)
 1,2 km

	Webseite

 [Lauer W. Dr.med.dent. & Lauer D. Dr.med.dent. Zahnärzte

 5,05.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/a20971cc-5cd3-4fd5-8345-41d3703bc519)

 Kurt-Schumacher-Str. 81,
 45881 Gelsenkirchen
 (Schalke)
 1,2 km

 Geöffnet
  – Schließt um 19:00

	Webseite

 [Ungruhe Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ed00c164-21e0-4ad2-9da7-242914bd7f5e)

 Bulmker Str. 4,
 45888 Gelsenkirchen
 (Bulmke-Hüllen)
 841 m

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Wolak Zahnarztpraxis

 4,54.5

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/843a5aa0-cd61-4e86-a0d8-de473d8ee04a)

 Bokermühlstr. 15,
 45879 Gelsenkirchen
 (Neustadt)
 1 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Vidakovic Jovan Zahnarzt

 5,05.0

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/2b991901-9988-4d16-a35c-2459969a3f34)

 Moorkampstr. 25,
 45883 Gelsenkirchen
 (Heßler)
 2,1 km

 [Spitzhofer Stefan Dr.med.dent.

 5,05.0

 8 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1254420c-7b5d-4c86-8a4c-f4ef1c64beda)

 Karl-Meyer-Str. 19,
 45884 Gelsenkirchen
 (Rotthausen)
 2,4 km

 Geschlossen
  – Öffnet um 15:00

 [Zarmas Dan Dr. Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/8ccd8d96-26bb-469f-a343-bee79888df12)

 Ravenbusch 2,
 45888 Gelsenkirchen
 (Bulmke-Hüllen)
 1,8 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Demir Cevdet Zahnarztpraxis

 4,04.0

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/8f78ce4d-c402-44c1-b925-2adf8cbfe3d4)

 Bismarckstr. 208,
 45889 Gelsenkirchen
 (Bismarck)
 1,9 km

 [Hoferichter Dr. u. Partner Zahnärzte

 5,05.0

 121 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/9a6237ef-e03a-4ef2-b944-cbb1c96cd341)

 Ückendorfer Str. 210,
 45886 Gelsenkirchen
 (Ückendorf)
 2,9 km

 Geöffnet
  – Schließt um 19:00

	Webseite

 [Kerstan Axel Drs. Zahnarztpraxis

 5,05.0

 7 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/77953524-d729-4440-9956-7f924bd7f189)

 Bismarckstr. 281,
 45889 Gelsenkirchen
 (Bismarck)
 2,7 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Kaya Aliya Zahnärztin

 4,64.6

 11 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/9615a303-f518-46ea-aa17-029303c01705)

 Im Lindacker 21,
 45886 Gelsenkirchen
 (Ückendorf)
 2,7 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Djukanovic Zahnärztin

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e070b716-f052-4cee-a27e-e23ddd46bb05)

 Kurt-Schumacher-Str. 174,
 45881 Gelsenkirchen
 (Schalke-Nord)
 2,8 km

 [Neunobel Ernst-Georg Dr.med.dent.

 4,54.5

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/547f3e95-7542-4eaf-b589-3bd6ff3fa84c)

 Grimmstr. 12,
 45883 Gelsenkirchen
 (Heßler)
 2,7 km

 Geschlossen
  – Öffnet um 14:30

	Webseite

 [Weichsel Wolfgang Dr.med.dent. und Partner Gemeinschaftspraxis für Kieferorthopädie

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/d733f8a4-ad00-48ae-88fb-c574d06d0a3c)

 Ebertstr. 20,
 45879 Gelsenkirchen
 (Altstadt)
 44 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Qasem Dr. Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ed3cfcf3-b797-4947-bb7c-213ffa2d4e6b)

 Ahstr. 8,
 45879 Gelsenkirchen
 (Altstadt)
 202 m

 Geschlossen
  – Öffnet um 14:30

	Webseite

 [Blaga Paul Dr.-medic stom. (RO), Elvermann Niels Dr.med.dent. Zahnärzte

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/00446174-f238-4460-86ef-cd29dd6ab457)

 Von-der-Recke-Str. 6,
 45879 Gelsenkirchen
 (Altstadt)
 400 m

	Webseite

 [Elvermann Niels Dr.med.dent., Blaga Paul Dr.-medic stom (RO) Zahnärzte

 1,01.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/6511c5f2-18f3-4984-9088-8ae313a8c5d1)

 Von-der-Recke-Str. 6,
 45879 Gelsenkirchen
 (Altstadt)
 400 m

 [Dr. med. dent. Romeo G. Brezeanu

 4,94.9

 5 Bewertungen

 Zahnärzte: Oralchirurgie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/bdd3e0fd-adab-4407-aba6-e43511360881)

 Ahstraße 2,
 45879 Gelsenkirchen

 137 m

 Geöffnet
  – Schließt um 17:00

	Webseite""",

    "Braunschweig": """[First Class

	König Jeannette Zahnärztin

 Zahnärzte

	Unsere Praxisräume befinden sich über der Buchhandlung Graff](https://www.gelbeseiten.de/gsbiz/a309a1fb-f261-472d-8938-9bf11001230c)

 Sack 15,
 38100 Braunschweig
 (Innenstadt)
 330 m

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Business

	BAG Dr. Anneke Ossenkop, Dr. Sabine Bruns, Dr. Lea Schneider (angestellt)

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b2b98793-3289-4979-83d9-aa032d7c821f)

 Münstedter Str. 5,
 38114 Braunschweig

 1,6 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Economy

	Dierksmeier, Martin

 Zahnärzte

	Zahnmedizin von Mensch zu Mensch](https://www.gelbeseiten.de/gsbiz/309c3a77-b253-4b2c-a1ca-515542bdd649)

 Neustadtring 30A,
 38114 Braunschweig

 1,4 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Economy

	Frau Dr. med. dent. Monika Siebert u. Frau Dr. med. dent. Anne Schlüter

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/3dd882f3-9418-4e6e-a3a5-47fccac46fdd)

 Am Fallersleber Tore 11,
 38100 Braunschweig
 (Innenstadt)
 661 m

	Webseite

 [Economy

	Frey Daniel

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/f466c495-504f-4bfd-86b0-e8cc212807c5)

 Leipziger Str. 213,
 38124 Braunschweig
 (Stöckheim)
 5,9 km

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Economy

	Kintzi-Hesse Manuela & Hesse Stefan Dr.

 4,84.8

 9 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/0aae5078-a855-4303-8763-c9fbe674a388)

 Hagenring 13,
 38106 Braunschweig

 1 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Economy

	Reinert Markus Dr. med. dent.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/047ad55a-dbf3-4d71-9cb9-cb4a3da30b34)

 Saarbrückener Str. 87,
 38116 Braunschweig

 3,7 km

 Geschlossen
  – Öffnet um 15:00

 [Economy

	Sokoll-Schmidt Inken Dr. med. dent.

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/6aa8e5b4-3348-4d2a-aded-295b565a6dd3)

 Hartgerstr. 1,
 38104 Braunschweig

 1,5 km

 Geschlossen
  – Öffnet um 14:30

	Webseite

 [Economy

	Werner Jürgen Dr. med. dent.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1499236a-a45f-49b2-a6d6-a08546e61a88)

 Weststr. 70,
 38126 Braunschweig
 (Rautheim)
 4,5 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Economy

	Wieczorek Elisabeth

 4,74.7000003

 38 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/479a08b2-cb00-4e48-b247-9924d6bfb6d8)

 Petritorwall 21,
 38118 Braunschweig

 1,1 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Economy

	Zahnärzte Dr. Johannes Klute & Steffen Stockburger Gemeinschaftspraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/53bc7a25-acf2-4967-8613-7f1b8430b50b)

 Altewiekring 19,
 38102 Braunschweig

 1,1 km

 Geöffnet
  – Schließt um 17:00

	Webseite

 [Economy

	Zeitz Jörg-Oliver

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/465da3d1-1326-43e0-86df-4be47d0d28ee)

 Kastanienallee 21,
 38102 Braunschweig

 1,3 km

 Geöffnet
  – Schließt um 18:00

 [Hilger Jörg Torsten Dr., König Jeannette Zahnärztliche Gemeinschaftspraxis

 4,74.7000003

 17 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/620dd92e-24df-496d-9ca8-7292675c51ab)

 Leonhardstr. 61,
 38102 Braunschweig

 768 m

	Webseite

 [Lier Uwe Dr.med. dent.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e9f3832a-69fa-4dcc-84aa-f533b6391247)

 Wollmarkt 5,
 38100 Braunschweig
 (Innenstadt)
 717 m

 [Ossenkop Anneke Dr., Bruns Sabine Dr. & Kollegen, Zahnarztpraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b2b98793-3289-4979-83d9-aa032d7c821f)

 Münstedter Str. 5,
 38114 Braunschweig

 1,6 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Siebert Monika Dr. Zahnärztin

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/bc9f9790-cb09-47d6-80e0-8235a0228e76)

 Am Fallersleber Tore 11,
 38100 Braunschweig
 (Innenstadt)
 661 m

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Wieczorek Elisabeth Zahnärztin

 4,74.7000003

 38 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/479a08b2-cb00-4e48-b247-9924d6bfb6d8)

 Petritorwall 21,
 38118 Braunschweig

 1,1 km

	Webseite

 [Wagner Bruno Dr.med.dent. Zahnarzt

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/a55817f6-66f7-4d4a-8bb8-e51e8a055e3d)

 Schild 1A,
 38100 Braunschweig
 (Innenstadt)
 314 m

	Webseite

 [Dr. med. dent. Peter Kalitzki

 5,05.0

 38 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/9a52504d-df31-4454-a001-18bfb8538a7b)

 Sonnenstr. 13,
 38100 Braunschweig
 (Innenstadt)
 866 m

	Webseite

 [Bantelmann Uwe Dr. Zahnarzt

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c20e2a13-07fc-4def-904c-1abf669c532b)

 Sack 5,
 38100 Braunschweig
 (Innenstadt)
 343 m

 [Altunordu Yasmin Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/307aa32d-3db6-4855-ac9c-06b78498c226)

 Georg-Eckert-Str. 11,
 38100 Braunschweig
 (Innenstadt)
 256 m

 Geöffnet
  – Schließt um 17:00

	Webseite

 [Meßner Udo

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d315a3ff-396e-43ee-bdd2-207ff1754216)

 Steinweg 29A,
 38100 Braunschweig
 (Innenstadt)
 261 m

 [Boger Michael Dr.med.dent., Boger Inge Zahnärzte

 4,84.8

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/618d03f0-bac9-40da-9942-bc9ae67f7052)

 Theaterwall 18,
 38100 Braunschweig
 (Innenstadt)
 569 m

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Mirsch Stefan Dr.

 5,05.0

 3 Bewertungen

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/80b880c2-dad5-4c95-944f-e0abd26a6f70)

 John-F.-Kennedy-Platz 9,
 38100 Braunschweig
 (Innenstadt)
 679 m

 Geöffnet
  – Schließt um 17:30

	Webseite

 [Drost Carola K. Zahnärztin

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c400d5d7-08d4-4331-a911-d1bd901d7598)

 Hagenmarkt 8,
 38100 Braunschweig
 (Innenstadt)
 358 m

 [Schmidt Hagen Dr.med.dent. Dr.dent. Zahnarzt

 4,64.6

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ae2ed91e-5ede-4148-beb2-6d55341415f3)

 Jasperallee 5,
 38102 Braunschweig

 692 m

 [Leonhard Ira u. Meyer-Bruck Susanne Dres.

 4,64.6

 2 Bewertungen

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/0b114b88-6847-4bf5-9927-857ae926eb98)

 Jöddenstr. 11,
 38100 Braunschweig
 (Innenstadt)
 425 m

 [Arroub Obaeda

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c2420dd8-9091-4db1-a979-d06aeae8bcc0)

 Friedrich-Wilhelm-Str. 50,
 38100 Braunschweig
 (Innenstadt)
 534 m

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Knabe Zahnarzt Olaf Dr. Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/15a4a589-6703-48dd-911c-9e251e14d98a)

 Jasperallee 86,
 38102 Braunschweig

 595 m

 [Karge Klaus Dr.med.dent. Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/9681ba3a-91ab-4923-9fc9-6d7cc025a321)

 Eiermarkt 1,
 38100 Braunschweig
 (Innenstadt)
 666 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Maaz Uwe Dr. Zahnarztpraxis

 4,04.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/90b8b647-289c-4a79-a339-c2245854adc1)

 Steinweg 26,
 38100 Braunschweig
 (Innenstadt)
 315 m

 Geöffnet
  – Schließt um 14:00

	Webseite

 [Frobenius Hans-Joachim Dr.

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7ceba240-4f3a-48fa-8dbe-e45a69c393a7)

 Adolfstr. 12,
 38102 Braunschweig

 704 m

	Webseite

 [Behrend Andrea Zahnärztin

 5,05.0

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/fec0bccc-e0cd-4680-80ad-f8ae474a9f3a)

 Neustadtring 32,
 38114 Braunschweig

 1,4 km

 [Zielke Petra

 4,94.9

 52 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7b333ec1-64c0-4a5b-9948-68d71fa21fde)

 Frankfurter Str. 20,
 38122 Braunschweig

 1,5 km

 Geöffnet
  – Schließt um 14:30

	Webseite

 [Pfötsch Dr. J. Fachzahnarzt für Kieferorthopädie

 4,44.4

 7 Bewertungen

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/b9f3adf0-f765-4bf7-a154-0152a46074e1)

 Gieselerwall 5,
 38100 Braunschweig
 (Innenstadt)
 1 km

 Geöffnet
  – Schließt um 17:00

	Webseite

 [Kleczka B.

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/dbe7bfa2-073f-4355-9165-858cfb854ee1)

 Wendenring 4,
 38114 Braunschweig

 1,2 km

 Geöffnet
  – Schließt um 19:00

 [Kallenbach Peter Dr., Mischke Catharina

 3,03.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/67403c46-1958-43eb-b261-c24392902ad2)

 Ruhfäutchenplatz 4,
 38100 Braunschweig
 (Innenstadt)
 223 m

 [Wedekind Kai Zahnarztpraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/6d0c4053-f113-44cb-ade4-83cb9eb758a3)

 Frankfurter Str. 3B,
 38122 Braunschweig

 1,2 km

	Webseite

 [Weiland Sebastian Dr.med.dent.

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e2db3907-2f81-4e0e-b127-d5aa3458295d)

 Rebenring 50,
 38106 Braunschweig

 1,4 km

 [Posten-Laffers Kerstin Fachzahnärztin für Kieferorthopädie

 3,33.3

 3 Bewertungen

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/3a02bc91-c75c-4467-8077-fc2e5244874c)

 Bohlweg 72,
 38100 Braunschweig
 (Innenstadt)
 263 m

	Webseite

 [Schmidt Stefan

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/5a623b06-2021-4b47-8f53-2794287b392c)

 Sidonienstr. 4,
 38118 Braunschweig

 1,3 km

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Wilkens Harald Dr. Zahnarzt

 3,33.3

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/db5374f6-24b0-449e-a4f3-24717be046d7)

 Kohlmarkt 19,
 38100 Braunschweig
 (Innenstadt)
 460 m

	Webseite

 [Schreibman Zahnarztpraxis A.

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e4195a41-c343-46ae-845b-d8325532ef2b)

 Juliusstr. 2,
 38118 Braunschweig

 1,3 km

	Webseite

 [Zimmer Dr. Annette Zahnärztin

 3,43.4

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c3a9779c-fdf9-4133-a36b-9bae35ab4d2d)

 Okerstr. 14,
 38100 Braunschweig
 (Innenstadt)
 836 m

 [Rühe Maurice Zahnarztpraxis

 4,74.7000003

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/34f77be4-2463-4f1c-ab44-8f6e125b9a2d)

 Walkürenring 57,
 38106 Braunschweig

 2,5 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Schoebel Susanne Dr. Zahnärztin

 5,05.0

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e5101306-b4d1-49e9-9b7b-b9142776d859)

 Hannoversche Str. 33,
 38116 Braunschweig
 (Lehndorf)
 3 km

 [Dr. Rüffert Haus der Zahnmedizin

 5,05.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/4b326e06-30be-47cc-8761-6019b5d2af2a)

 Traunstraße 1,
 38120 Braunschweig

 3,3 km

 Geöffnet
  – Schließt um 19:00

	Webseite

 [Zahnarztpraxis Dirk Rustenbach Praxis für Wurzelbehandlung und Implatologie Zahnarzt

 4,94.9

 12 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ad09d49d-963d-436c-9d29-8929195dcd06)

 Wurmbergstr. 30,
 38122 Braunschweig
 (Gartenstadt)
 3,7 km

	Webseite""",

    "Aachen": """[Comfort Partner

	Bosman David Dr.med.dent.

 Zahnärzte

	Moderne Zahnarztpraxis in Aachen: Ästhetische Zahnheilkunde, Endodontie und schmerzarme Behandlung.....](https://www.gelbeseiten.de/gsbiz/97f11d62-5a83-4c64-818b-7c0b79a12ba7)

 Annastr. 42,
 52062 Aachen

 414 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Comfort Partner

	Kuiff Wolfram Dr. med. dent.

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/8f663cdb-815c-4cd7-bef4-9bbb3e8b9582)

 Verlautenheidener Str. 104,
 52080 Aachen

 5,6 km

 Geschlossen
  – Öffnet um 14:30

	Webseite

 [Comfort Partner

	Pöggeler Rasmus Zahnheilkunde Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c9a7fdf2-6c40-4e11-9b70-307780c017da)

 Bissener Str. 39,
 52146 Würselen

 6 km

 Geschlossen
  – Öffnet um 14:45

	Webseite

 [Basic Partner

	Debuch Daniel

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7f7d9bd9-f005-4a54-8540-64f2ccf3ecc0)

 Adenauerallee 150,
 52066 Aachen

 2,7 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Comfort Partner

	Dolatnejad Gargari Meysam Zahnarzt

 5,05.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b8ea2c77-9910-4540-8d26-f38211516868)

 Hochstr. 42,
 52078 Aachen

 6,5 km

 Geöffnet
  – Schließt um 17:00

	Webseite

 [Basic Partner

	Kilian Thomas Dr.med.dent.

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c0f55c17-87c9-4f1e-826f-9e876abea7dd)

 Stolberger Str. 15-17,
 52068 Aachen

 2 km

 [Basic Partner

	Vlaicu Sanda-Iulia

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/604353ca-4c54-4dfe-b42c-4e2fed742638)

 Süsterfeldstr. 3-7,
 52072 Aachen

 1,1 km

 Geschlossen
  – Öffnet um 14:00

 [Basic Partner

	Wetzel Katherine Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/84bd8f1a-6dc8-4031-828f-489511404a92)

 Severinstr. 119,
 52080 Aachen

 5 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Al-Madhi Mujkic Gemeinschaftspraxis für Zahnärzte

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/19ce0d7a-7e2b-4d4e-9f88-26fc7ec05420)

 Wirichsbongardstr. 5-9,
 52062 Aachen

 451 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Amjadi-Kemper Arezoo Zahnarztpraxis, Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/0ab6c5d6-dbaf-4498-bbfe-20f93544e003)

 Monheimsallee 2,
 52062 Aachen

 840 m

 [Appel Christian Dr. Zahnarztpraxis

 2,32.3

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/8a721fdc-5b8f-4098-9847-a54d57d55f49)

 Maria-Theresia-Allee 77,
 52064 Aachen

 2 km

	Webseite

 [Aufermann Caroline Zahnärztin

 5,05.0

 13 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d0c87552-c7f9-47f8-bc25-3cf9613786d3)

 St. Gangolfsberg 18,
 52076 Aachen

 8,7 km

 Geöffnet
  – Schließt um 16:00

 [Baatz Astrid Dr., Baatz Achim Dr. Zahnärzte

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/a26cd8d3-9863-4ea1-8965-1b00572e7d60)

 Prämienstr. 19,
 52076 Aachen

 10,4 km

 Geschlossen
  – Öffnet Donnerstag um 09:00

	Webseite

 [Bartholomäus Alexandra Zahnarztpraxis

 4,84.8

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/595c252a-3a90-4fff-a525-7f866c8871ae)

 Gierstr. 10,
 52072 Aachen

 4,8 km

 [Baumgarten Th. F. Zahnarztpraxis

 5,05.0

 8 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d71caedf-7036-47ae-8b3f-3bd1c2679ec3)

 Roermonder Str. 386,
 52072 Aachen

 3,3 km

 [Beckers Markus P. Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ad08b543-2120-4e4e-8e4b-21272490fc4c)

 Jakobstr. 14-16,
 52064 Aachen

 222 m

 [Berndt Tobias

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/301839a7-3d09-4c0a-a3ae-eb1e9381b5f2)

 Augustastr. 57,
 52070 Aachen

 1,2 km

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Block Emina Zahnarztpraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/2e4b3235-05df-45f0-94a3-61ef561cfaf4)

 Gasborn 0,
 52026 Aachen

 679 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Bodden Astrid Dr., Cox Hans Dr. Zahnärzte

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e567492b-cfea-48ce-a329-ad20ff4bdcd4)

 Haarener Gracht 2,
 52080 Aachen

 3,7 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Bouchouchi Nassim Dr., Deutz Heike Dr. Zahnärzte

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7151ed8d-131b-4e7b-8be9-2daac1e506f6)

 Pottenmühlenweg 28,
 52064 Aachen

 1,4 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Brawek Petya Zahnarztpraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/66696ccb-7284-4730-a44c-72c9d56a4fad)

 Adalbertsteinweg 32-36,
 52070 Aachen

 1,2 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Busche Georg Dr. Zahnarzt & Oralchirurgie

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/9b473c52-0441-4694-9dff-c6fe3b19dc70)

 Theaterplatz 9,
 52062 Aachen

 527 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Chatzipetros Dina Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d1d5d722-e0ed-4330-8fda-96bf0d8b9b08)

 Suermondtplatz 2,
 52062 Aachen

 651 m

 Geschlossen
  – Öffnet um 08:30

 [Conrads Paul Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/3fd513db-1140-43b7-899f-fde0d1f1567f)

 Im Grüntal 1,
 52066 Aachen

 2,2 km

 Geschlossen
  – Öffnet um 14:00

 [Cox Hans Dr. Zahnarzt, Bodden Astrid Dr. Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/fc1fe8ae-d3de-482e-9ae1-7bf1adfef9cf)

 52080 Aachen

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Crott Wolfgang Dr.med.dent. Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/012ec09c-5bec-4c27-8b6b-55c629e2046f)

 Herzogstr. 1-5,
 52070 Aachen

 1,2 km

	Webseite

 [Debuch Daniel Zahnarzt

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7f7d9bd9-f005-4a54-8540-64f2ccf3ecc0)

 Adenauerallee 150,
 52066 Aachen

 2,7 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Dolezel Peter Dr.med.dent. Zahnarzt

 3,53.5

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/61470aaa-9075-45cb-bb3d-d4fcdf5aa1c8)

 Nerscheider Weg 60,
 52076 Aachen

 7,8 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Dr. Grümer und Kollegen Zahnärzte an der Theaterstrasse

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/0fba8afb-a6ab-4bc6-a550-658ed412325c)

 Theaterstr. 50,
 52062 Aachen

 844 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Dr. Z. Zahnarztpraxis Aachen GmbH

 2,62.6000001

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ed45f423-2090-4ba0-a337-528886b2dfa2)

 Holzgraben 17,
 52062 Aachen

 313 m

	Webseite

 [Dr. Z. Zahnarztpraxis Aachen GmbH

 2,62.6000001

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/0dd7eac0-54ff-4191-bad4-5ec383ddf34f)

 Holzgraben 17,
 52062 Aachen

 313 m

 Geschlossen
  – Öffnet um 14:30

	Webseite

 [Droste Klaus Dr.med.dent. Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ad6a88e9-8d3a-49fb-887a-927005002f8b)

 Trierer Str. 791,
 52078 Aachen

 6,4 km

 Geschlossen
  – Öffnet um 14:00

 [Drunkemöller Roswitha Dr.med.dent.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/684fc4b3-329e-4f2a-93f4-ba73327ee0a4)

 Morinerweg 6,
 52074 Aachen

 3,3 km

	Webseite

 [Endres Bernhard Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b3a3e066-b5df-423e-b565-5f5c650cc897)

 Neustr. 58,
 52066 Aachen

 1,5 km

 Geschlossen
  – Öffnet um 14:00

 [Endres Melanie Zahnärzte, Endres Lutz

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/2c6e8ea3-84d3-4cb7-b082-3450988c4c1f)

 Schleckheimer Str. 18,
 52076 Aachen

 8,5 km

 Geschlossen
  – Öffnet um 14:00

 [Feld Jennifer Dr.med.dent. Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/da285501-25a1-429b-abf7-6f46352fe9af)

 Harscampstr. 38-42,
 52062 Aachen

 716 m

 Geöffnet
  – Schließt um 20:00

	Webseite

 [Fey Axel Zahnarzt

 4,84.8

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7d6a3005-019d-4445-bc7e-a3498ec6ea29)

 Freunder Landstr. 6,
 52078 Aachen

 6,5 km

 [Finke-Schmitz Andrea Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/804b3d00-b4bf-4f75-85c2-7a66e9dfe6a5)

 Von-Coels-Str. 403,
 52080 Aachen

 6,5 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Fischer Julia Dr.med.dent. Zahnärztin

 4,24.2000003

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/29cbeb84-3f85-44dd-a693-b809c6020fc3)

 Horbacher Str. 321A,
 52072 Aachen

 6,9 km

 Geschlossen
  – Öffnet um 14:00

 [Frenzel Ute MSc u. Frenzel Walter Zahnärztliche Gemeinschaftspraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/a742d59a-81eb-41bc-8a6c-4671ba7ad94b)

 Elsassplatz 8,
 52068 Aachen

 2,3 km

 Geöffnet
  – Schließt um 18:30

	Webseite

 [Basic Partner

	Besel Simone Dr.med.dent.

 5,05.0

 1 Bewertung

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/8354cb6b-3314-46ee-8c7c-dc725cdc1691)

 Theaterplatz 13,
 52062 Aachen

 535 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [dent-a-la-carté | Dr. Sven Hertzog

 4,94.9

 31 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/16367e20-d215-4ee3-8694-bd9579d0f9c3)

 Rochusstraße 22,
 52062 Aachen

 414 m

	Webseite

 [dent-à-la-carte | Dr. Sven Hertzog

 4,94.9

 31 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/62b73ad3-d07d-4b38-8f6c-87e86e43c1b2)

 Rochusstraße 22-24,
 52062 Aachen

 414 m

 Geöffnet
  – Schließt um 17:00

	Webseite""",

    "Kiel": """[Gold Partner

	Dr. Christoph Quast M.Sc. und Kollegen Praxis für Zahnheilkunde

 3,03.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/32751cde-52f6-40a4-b886-7c9dd3bb9620)

 Holtenauer Str. 268,
 24106 Kiel
 (Wik)
 3 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Gold Partner

	Piepereit Torsten Zahnarztpraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/3d279b0e-cbf7-4193-a361-e16e1e5bd039)

 Grot Steenbusch 32,
 24145 Kiel
 (Poppenbrügge)
 4,3 km

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Silber Partner

	Aneta Krajna-Edel, Zahnärztin

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/48fa851c-45a3-4ac8-82bf-a4a1a2383ef3)

 Hedinweg 18,
 24109 Kiel

 4,5 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Silber Partner

	Zahnarztpraxis im Citti-Park, Inh. Sünje Callea

 4,34.3

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/093a2979-0916-4a1b-b9af-d147548583bb)

 Mühlendamm 1,
 24113 Kiel
 (Hassee)
 2,5 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Bronze Partner

	Dentoneum - Zahnarztpraxis Kiel

 5,05.0

 9 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/dbbc3249-3f4f-4b59-b066-528132290268)

 Karlstal 35,
 24143 Kiel

 1,6 km

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Bronze Partner

	Herholz Niels Dr.med.dent. Zahnarzt

 4,74.7000003

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ad7a7579-3917-44ed-bc8f-7349c8bf7fe3)

 Feldstr. 96,
 24105 Kiel

 2 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Männel Stefan Dr.med.dent. Zahnarzt

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/74b2c889-81ba-468c-a890-aa2531a06358)

 Knooper Weg 107,
 24116 Kiel
 (Brunswik)
 945 m

 Geöffnet
  – Schließt um 15:00

	Webseite

 [Silber Partner

	Rohwedder Frank Dr. Fachzahnarzt für Kieferorthopädie

 4,24.2000003

 1 Bewertung

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/fc4feea7-2aef-4b0f-97c9-7f8165ea3f4f)

 Preußerstr. 17-19,
 24105 Kiel
 (Brunswik)
 831 m

 [Gemeinschaftspraxis für Zahnmedizin, Zahnärztin Linda Bodart & Dr. Andrea Schädler

 5,05.0

 26 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/82bbd265-94a5-43de-8228-8cfabd3c50e5)

 Holstenstr. 37,
 24103 Kiel
 (Vorstadt)
 247 m

 [Heinze Ulf Zahnarzt

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e333385e-3de3-49d9-8a46-81d011ef9f85)

 Kehdenstr. 25,
 24103 Kiel
 (Altstadt)
 207 m

 Geöffnet
  – Schließt um 19:00

 [Gleichfeld Andreas Dr. Zahnarzt

 5,05.0

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/0a649085-e211-415f-bc16-5658a9d843a2)

 Alter Markt 14,
 24103 Kiel
 (Altstadt)
 434 m

 [Gleichfeld Andreas Dr. Zahnarzt

 5,05.0

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/5ac81fa1-d85d-499e-b65d-bda5c58607c7)

 Alter Markt 14,
 24103 Kiel
 (Altstadt)
 434 m

 [Musewald Thomas Dr.med.dent. Kieferorthopäde

 5,05.0

 3 Bewertungen

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/9ddf7197-bb71-475d-95e6-25220ddea490)

 Rathausstr. 28,
 24103 Kiel
 (Exerzierplatz)
 279 m

 Geöffnet
  – Schließt um 18:00

 [Musewald Thomas Dr.med.dent., Bellingkrodt Dietrich Dr. Kieferorthopäden

 5,05.0

 3 Bewertungen

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/0321ee8d-62d7-4388-8c4d-0d9c197eae21)

 Rathausstr. 28,
 24103 Kiel
 (Exerzierplatz)
 279 m

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Hinrichsen Jan Dr. Zahnarzt Implantologie

 4,74.7000003

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/0a0961f2-90d4-4bfc-b905-7193f33decca)

 Kehdenstr. 25,
 24103 Kiel
 (Altstadt)
 207 m

 Geöffnet
  – Schließt um 19:00

 [Ehlers Heiko Dr. Zahnärzte

 5,05.0

 8 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/faf6b4d3-64b4-479d-bc62-2c6981b67cc3)

 Schloßgarten 12,
 24103 Kiel
 (Damperhof)
 772 m

 Geschlossen
  – Öffnet um 14:00

 [Hartmann Björn Dr. med. dent. Zahnarztpraxis

 4,94.9

 7 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/a4af5bc9-f82b-4e5f-acb2-a07861041069)

 Brunswiker Str. 50,
 24105 Kiel
 (Brunswik)
 710 m

 Geschlossen
  – Öffnet um 14:00

 [Zahnarzt in Kiel / Dr. Björn Hartmann

 4,94.9

 7 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/dd7b4652-b23c-4aa3-9ce0-68ae5a457441)

 Brunswiker Straße 50,
 24105 Kiel

 710 m

	Webseite

 [Müller Philipp Dr. Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/dbaf430c-c117-4196-9d2c-1ba1952943af)

 Andreas-Gayk-Str. 23,
 24103 Kiel
 (Vorstadt)
 326 m

 Geschlossen
  – Öffnet Dienstag um 09:30

 [Jager Hans-Dieter Dr. Zahnarzt

 4,64.6

 70 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/78f99e97-b523-402e-afd1-a6e8400c1b5d)

 Kronshagener Weg 26,
 24116 Kiel
 (Schreventeich)
 1,1 km

 Geschlossen
  – Öffnet um 14:30

 [Wegner Stefan Dr.med.dent. MSc Implantology Zahnarzt

 5,05.0

 11 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/9ca8c5a9-961e-4589-9ebb-2e5c0f3e0a89)

 Goethestr. 30,
 24116 Kiel
 (Schreventeich)
 1,1 km

 Geöffnet
  – Schließt um 18:00

 [Bohlsen Frank Dr. & Steinebrunner Lars Dr. Praxis für Zahnheilkunde

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/5d5683c5-53ff-4cf7-af32-0ad9ecc7f6ff)

 Bollhörnkai 1,
 24103 Kiel
 (Vorstadt)
 532 m

 Geöffnet
  – Schließt um 19:00

 [Runge Sabine Dr. u. Alexander Dr.

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/8b60b106-40e9-4c5a-9397-fc5a312a1508)

 Prüner Gang 15,
 24103 Kiel
 (Exerzierplatz)
 563 m

 [Schneider Uwe Dr., Dieter Zahnärzte

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/6f2d423f-aed1-447e-9f26-bfce2770ce2c)

 Holtenauer Str. 3,
 24103 Kiel

 683 m

 [Schneider Uwe Dr., Dieter Zahnärzte

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/21d8bb61-1e28-4c8c-a30d-bdef0718eded)

 Holtenauer Str. 3,
 24103 Kiel

 683 m

 [Schneider Uwe Dr. Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/6b304754-1203-474e-ac07-75b0e6558a01)

 Holtenauer Str. 3,
 24103 Kiel

 683 m

 [Rafail Silvia u. Weber Steffen

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e75ab4fb-bd79-4a36-a9bb-31ebb81a13b6)

 Schillerstr. 5,
 24116 Kiel
 (Schreventeich)
 934 m

 Geschlossen
  – Öffnet Donnerstag um 10:00

 [Boether Christian Dr., Boether Harriet Zahnärzte

 4,54.5

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/4180a6f9-e9d2-45e9-9449-5d6d86f85c5c)

 Wilhelminenstr. 20,
 24103 Kiel
 (Damperhof)
 617 m

 Geschlossen
  – Öffnet um 15:00

 [Fischer Michael u. Schmidt Oliver Dr.

 4,34.3

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b472e1ec-1480-4138-93b2-d01917c9e730)

 Holtenauer Str. 53,
 24105 Kiel
 (Brunswik)
 1,1 km

 Geöffnet
  – Schließt um 19:00

 [Raspel Tim Dr., Bünnig Nina Johanna Dr. Zahnärzte

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/997643df-1b24-41ce-94d3-0e8a2246adeb)

 Karlstal 25,
 24143 Kiel
 (Gaarden-Ost)
 1,4 km

 Geöffnet
  – Schließt um 18:00

 [Erdogan Mehmet Dr. med. dent. - Zahnarztpraxis am Germaniahafen Zahnarzt

 4,54.5

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/fce0d785-481b-4e93-81d7-b0b10fc958d6)

 Am Germaniahafen 4,
 24143 Kiel
 (Gaarden-Ost)
 934 m

 Geöffnet
  – Schließt um 20:00

 [Erdogan Mehmet Dr. med. dent. - Zahnarztpraxis am Germaniahafen Zahnarzt

 4,54.5

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/fce0d785-481b-4e93-81d7-b0b10fc958d6)

 Am Germaniahafen 4,
 24143 Kiel
 (Gaarden-Ost)
 934 m

 Geöffnet
  – Schließt um 20:00

 [Kühne Dr. Falk Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/740ee478-c897-48c2-b193-4a221aebb99b)

 Harmsstr. 83,
 24114 Kiel
 (Südfriedhof)
 1,1 km

 Geschlossen
  – Öffnet um 15:00

 [Schreiber Siegbert Dr. Zahnarzt

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1a621452-b13a-4a60-91e8-daf529223215)

 Lutherstr. 9,
 24114 Kiel
 (Südfriedhof)
 1,4 km

 Geschlossen
  – Öffnet Dienstag um 09:00

 [Zahnarztpraxis Wurzelwerk

 5,05.0

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/eee84ba4-1f1e-4f54-a1e6-646dff420f35)

 Niemannsweg 46,
 24105 Kiel
 (Düsternbrook)
 1,7 km

 Geöffnet
  – Schließt um 19:00

 [Zahnecke Kiel - Zahnarztpraxis Oliver Großkopf & Kollegen

 4,94.9

 13 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/5ce073f2-4838-4434-8c87-766d145895a0)

 Gefionstr. 2,
 24105 Kiel
 (Blücherplatz)
 2 km

 Geschlossen
  – Öffnet um 14:00

 [Glockenstein Markus Facharzt für Kieferorthopädie

 5,05.0

 1 Bewertung

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/c9115c52-9263-4220-a3fb-a53cf6709f83)

 Elisabethstr. 32,
 24143 Kiel
 (Gaarden-Ost)
 1,3 km

 [Sayk Erhard Zahnarzt

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/12001d56-6862-472d-abf3-7dc1875ce269)

 Kaiserstr. 37,
 24143 Kiel
 (Gaarden-Ost)
 1,6 km

 Geöffnet
  – Schließt um 20:00

 [Zahnarzt Kiel - Klaas Köppe

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/96881063-1f28-45d0-b0b3-ba76092bf425)

 Knooper Weg 163,
 24118 Kiel

 1,5 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Kamps Bettina Dr. Zahnärztin

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/6e077fef-e35c-450b-89e3-2eb7f0db0980)

 Waitzstr. 41A,
 24105 Kiel
 (Brunswik)
 1,4 km

 [Schneeberg Peter-Andreas Zahnärztliche Praxis

 3,23.2

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d62dec95-875d-4127-a3cf-a0b3f947101f)

 Lerchenstr. 20,
 24103 Kiel
 (Vorstadt)
 691 m

 Geschlossen
  – Öffnet um 15:00

 [Schneeberg Peter-Andreas Zahnärztliche Praxis

 3,23.2

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d62dec95-875d-4127-a3cf-a0b3f947101f)

 Lerchenstr. 20,
 24103 Kiel
 (Vorstadt)
 691 m

 Geschlossen
  – Öffnet um 15:00

 [Delia Chmill Kieferorthopädin

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/50663a21-0dae-43dd-974c-a3daf124a98c)

 Adelheidstr. 10,
 24103 Kiel
 (Exerzierplatz)
 708 m

 Geöffnet
  – Schließt um 18:00

 [Herholz Niels Dr. Zahnarzt

 4,74.7000003

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e0029862-0de2-41ac-827c-55edf0a20ca2)

 Feldstr. 96,
 24105 Kiel
 (Blücherplatz)
 2 km

 Geschlossen
  – Öffnet um 14:30

 [Stitz M. Dr., Mogadas A. Dr. Zahnärzte

 4,74.7000003

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/707ad0fe-1c05-4d6c-ad36-8ca0518fb11e)

 Olshausenstr. 26,
 24118 Kiel
 (Ravensberg)
 1,8 km

 Geöffnet
  – Schließt um 20:00""",

    "Chemnitz": """[Platin Partner

	Schlesies Rainer Dipl.-Stom.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c8ef037b-4cf5-40a1-a04a-a3225acb73a7)

 Ringstr. 17a,
 09247 Chemnitz
 (Röhrsdorf)
 5,1 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Silber Partner

	Halm Matthias Dr. Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/f8c5cb0d-e0fe-48c0-a49c-f49fe2a39e77)

 Querstr. 2,
 09114 Chemnitz
 (Glösa-Draisdorf)
 4,1 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Silber Partner

	Döring, Götz und Isa

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e79247d5-cba2-4965-8cb1-677d23c94ff1)

 Magaretenstr. 10,
 09131 Chemnitz
 (Hilbersdorf)
 2,8 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Silber Partner

	Barthel Rolf MR Dr. med. dent., Barthel Tom Dr. med. dent.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ad8c1d11-fbcc-44d3-94cb-55e9d77e1497)

 Faleska-Meinig-Str. 2,
 09122 Chemnitz
 (Markersdorf)
 4,8 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Silber Partner

	Loos René Dr. med. dent.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/0c166b3f-c31f-4989-9065-9d09b4b916c1)

 Wartburgstr. 84,
 09126 Chemnitz
 (Bernsdorf)
 2,4 km

 Geöffnet
  – Schließt um 19:00

	Webseite

 [Silber Partner

	Milad, Asskaf

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/81012105-4963-4cf3-93c2-21f9fb755bf8)

 Agricolastr. 9,
 09112 Chemnitz
 (Kaßberg)
 1 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Gemeinschaftspraxis der Zahnärzte Dr. Rolf und Dr. Tom Barthel Zahnärzte

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/20b99707-cd87-4536-b571-8f17abd825ff)

 Faleska-Meinig-Str. 2,
 09122 Chemnitz
 (Markersdorf)
 4,8 km

 Geschlossen
  – Öffnet um 14:00

 [Gemeinschaftspraxis der Zahnärzte Dr. Rolf und Dr. Tom Barthel Zahnärzte

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/20b99707-cd87-4536-b571-8f17abd825ff)

 Faleska-Meinig-Str. 2,
 09122 Chemnitz
 (Markersdorf)
 4,8 km

 Geschlossen
  – Öffnet um 14:00

 [Dr. Z Zahnmedizinischen Zentrum

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1d9cd2a5-f9d5-4850-a913-dcecd96ff2d1)

 Markt 5,
 09111 Chemnitz
 (Zentrum)
 136 m

 [Müller-Leißring & Kollegen Zahnarztpraxis

 5,05.0

 5 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/9402c678-f7d1-4ac9-ba63-edf70d8d083b)

 Wiesenstr. 11,
 09111 Chemnitz
 (Zentrum)
 763 m

 Geöffnet
  – Schließt um 19:00

 [Schmidt Matthias Dr.med.dent. Zahnarzt

 4,34.3

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/20645632-9b7b-4b3d-bbf3-ad6e5b02bad2)

 Düsseldorfer Platz 1,
 09111 Chemnitz
 (Zentrum)
 144 m

 Geöffnet
  – Schließt um 18:00

 [Zahnkontakte Chemnitz Dres. Krause Fachzahnärzte Partnerschaft

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/a2c3162d-c79e-42e5-89a0-bef7958c4c25)

 Theaterstr. 34 A,
 09111 Chemnitz
 (Zentrum)
 335 m

 Geschlossen
  – Öffnet um 14:00

 [Zahnärztliche Gemeinschaftspraxis Dr.Jehmlich/Dr.Bergner

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d2d72dea-f04a-4e41-b0fa-c5cc0e4c0664)

 Hainstr. 29,
 09130 Chemnitz
 (Sonnenberg)
 962 m

 Geöffnet
  – Schließt um 18:00

 [Georgi Claudia Dr.med., Jürgen Dr.med. Zahnarztpraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/82135907-e518-47f8-a9dc-4ce9b0ee6d89)

 Barbarossastr. 10,
 09112 Chemnitz
 (Kaßberg)
 1,2 km

 Geschlossen
  – Öffnet Dienstag um 08:00

 [Georgi Claudia Dr.med., Jürgen Dr.med. Zahnarztpraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/82135907-e518-47f8-a9dc-4ce9b0ee6d89)

 Barbarossastr. 10,
 09112 Chemnitz
 (Kaßberg)
 1,2 km

 Geschlossen
  – Öffnet Dienstag um 08:00

 [Krasselt Cornelia Dr. Zahnärztin

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/15ac173c-b691-4f6e-90ba-9aec5b90b2b7)

 Gießerstr. 13,
 09130 Chemnitz
 (Sonnenberg)
 1,2 km

 Geschlossen
  – Öffnet Dienstag um 08:00

 [Wagner Evelyn Dr.med., Uwe Zahnarztpraxis

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1c61c3d7-d0ca-40cc-9139-31c595cabb57)

 Würzburger Str. 25,
 09130 Chemnitz
 (Sonnenberg)
 1,7 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Kruglowa Christine Dipl.-Med. Facharzt für Kieferorthopädie

 3,53.5

 4 Bewertungen

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/c96499ae-9d7b-4c04-909d-bad2a23deb6f)

 Carolastr. 1,
 09111 Chemnitz
 (Zentrum)
 783 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Zahnarztpraxis Dr. Berthold Rink

 4,04.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c565cd27-7349-4f7e-bb1d-e872f1263996)

 Straße Der Nationen 70,
 09111 Chemnitz

 1 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Espenhayn Frank Dr.med.dent. Zahnarztpraxis

 3,03.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/8f7f7542-047a-4006-b3c6-5052dd1ef386)

 Schloßteichstr. 11,
 09113 Chemnitz
 (Schloßchemnitz)
 1,1 km

 Geschlossen
  – Öffnet um 14:00

 [Schafir Wiktorija Zahnärztin

 4,04.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/668efbc0-d133-4c2e-9caf-da73c1544575)

 Parkstr. 28A,
 09120 Chemnitz
 (Kapellenberg)
 1,8 km

 [Gregor Claudia Dr. Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1067ebd4-4659-4f98-a812-17a9971caf22)

 Flemmingstr. 1B,
 09116 Chemnitz
 (Altendorf)
 2,6 km

 Geschlossen
  – Öffnet um 14:00

 [Dr. med. M. Müller Kieferorthopädische Praxis Facharzt für Kieferorthopädie

 5,05.0

 1 Bewertung

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/ae7d0474-cb5b-4c80-87c1-5fa6ba4efa9f)

 Annaberger Str. 171,
 09120 Chemnitz
 (Altchemnitz)
 2,6 km

 Geöffnet
  – Schließt um 18:00

 [Löser-Toth Maria Zahnärztin

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/cc6fd7d7-57c0-4659-b6a2-44e20518c086)

 Zwickauer Str. 216,
 09116 Chemnitz
 (Schönau)
 3 km

 Geöffnet
  – Schließt um 16:00

 [Seyffert Ivonne Zahnärztin

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/21003332-cf23-40a0-8269-519d291c75b7)

 Zwickauer Str. 223A,
 09116 Chemnitz
 (Schönau)
 3 km

 Geöffnet
  – Schließt um 17:30

 [Stammler Jens

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/15fdb6af-ec62-4c9f-b573-3191a50266d5)

 Ulbrichtstr. 6,
 09126 Chemnitz
 (Bernsdorf)
 2,8 km

 Geöffnet
  – Schließt um 16:00

 [Stammler Jens Dr.med.

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/15fdb6af-ec62-4c9f-b573-3191a50266d5)

 Ulbrichtstr. 6,
 09126 Chemnitz
 (Bernsdorf)
 2,8 km

 Geöffnet
  – Schließt um 16:00

 [Döring Götz Dipl.-Stom., Döring Isa Dipl.-Stom. Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/a2c31897-97c0-4293-9ee6-594c22407bd1)

 Margaretenstr. 10,
 09131 Chemnitz
 (Hilbersdorf)
 2,8 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Seiß Holger Dr.med.dent. Zahnarzt

 4,24.2000003

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/946765fd-8a2f-4ec7-97d8-c8bfb0daa7eb)

 Fürstenstr. 143,
 09130 Chemnitz
 (Yorckgebiet)
 2,7 km

 Geöffnet
  – Schließt um 17:30

 [Pietz Jörg Dr.med.dent. Zahnarztpraxis, Pietz Toni Dr.med.dent.

 5,05.0

 26 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/2a6b3b14-606b-4067-a1a2-0d63b50c470c)

 Bornaer Str. 79,
 09114 Chemnitz
 (Borna-Heinersdorf)
 3,6 km

 Geschlossen
  – Öffnet um 15:00

 [Kost Silvio Dr.med.dent. Zahnarzt

 4,74.7000003

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e59932cb-1883-4f18-9391-3f96e1a10041)

 Stollberger Str. 131,
 09119 Chemnitz
 (Helbersdorf)
 2,9 km

 Geschlossen
  – Öffnet um 14:00

 [Oralchirurgische Praxis Dr. Schetschorke

 Zahnärzte: Oralchirurgie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/1d6719f0-c917-483c-a234-338893c4bc6f)

 Jakobikirchplatz 4,
 09111 Chemnitz
 (Zentrum)
 42 m

 Geöffnet
  – Schließt um 17:00

 [Taubert Martina Dipl.-Stom. Praxis für Kieferorthopädie

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/39e7a115-0e31-477c-9747-77626f811394)

 Markt 5,
 09111 Chemnitz
 (Zentrum)
 135 m

 Geschlossen
  – Öffnet um 14:00

 [Neidt Roger Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ea1a2192-47e1-44fe-96f6-28af572fee84)

 Am Rathaus 2A,
 09111 Chemnitz
 (Zentrum)
 142 m

 [Ramelow Heike Dr. Zahnarztpraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/65cf4235-0fdd-4167-9c6a-0a3aeb1f40a1)

 Bahnhofstr. 54,
 09111 Chemnitz
 (Zentrum)
 263 m

 [Graupner Sabine Dr. Zahnarztpraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/698b9397-535e-46e5-b3ef-8886d6d53339)

 Rosenhof 16,
 09111 Chemnitz
 (Zentrum)
 267 m

 [Wolf Daniel Dr. Zahnarzt

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c04004af-e378-4d45-a12f-18a1cb9ff46e)

 Rosenhof 16,
 09111 Chemnitz
 (Zentrum)
 267 m

 Geschlossen
  – Öffnet um 14:00

 [Birr Angela Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/16ae178f-3e04-4295-ba6d-520ddecce011)

 Moritzstr. 37,
 09111 Chemnitz
 (Zentrum)
 432 m

 Geschlossen
  – Öffnet Dienstag um 08:00

 [Birr Angela Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/48390389-46d0-4632-a3ba-50c654c4a8c8)

 Moritzstr. 37,
 09111 Chemnitz
 (Zentrum)
 432 m

 Geschlossen
  – Öffnet Dienstag um 08:00

 [Meyer Evelin MUDr Zahnarztpraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b05ce744-75c8-4551-814b-78e7d55f09b1)

 Brückenstr. 37,
 09111 Chemnitz
 (Zentrum)
 535 m

 Geöffnet
  – Schließt um 19:00

	Webseite

 [Budai Carola Dr.med.dent. Zahnarztpraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e90aeae2-70a8-42f9-a13c-9ecd5774a56f)

 Augustusburger Str. 28,
 09111 Chemnitz
 (Zentrum)
 672 m

 Geöffnet
  – Schließt um 18:00

 [Richter Pia Dr. med. dent. Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e67ae465-f584-4f12-bd42-da05e900648f)

 Reichsstr. 26,
 09112 Chemnitz
 (Kaßberg)
 741 m

 [Richter Pia Dr. Zahnärztin

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/618bbbf8-af37-4563-9780-27faf53fbe81)

 Reichsstr. 26,
 09112 Chemnitz
 (Kaßberg)
 741 m

 [Müller Lisa Zahnarztpraxis

 4,04.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/fb213b40-1640-413a-8004-19599a183fe1)

 Carl-von-Ossietzky-Str. 151,
 09127 Chemnitz
 (Gablenz)
 3 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Pradler Hagen Zahnarzt

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/848c6368-df16-4990-98ea-aab7cdf7e57a)

 Glösaer Str. 18,
 09131 Chemnitz
 (Ebersdorf)
 4 km

 Geöffnet
  – Schließt um 18:00

 [Zahnzentrum MK Mariam Magomedova & Jakob Krauß GbR

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7e4059f8-8c45-4e15-959f-d0dcd68e1b55)

 Dresdner Str. 38 A,
 09130 Chemnitz
 (Sonnenberg)
 894 m

 Geöffnet
  – Schließt um 18:30

 [Pöllnitz Nils Zahnarztpraxis

 5,05.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e901065c-8dd3-4219-b43f-74c9c3c1e8ed)

 Robert-Siewert-Str. 22,
 09122 Chemnitz
 (Markersdorf)
 4,3 km

 Geschlossen
  – Öffnet um 14:00

 [Rehbach Matthias

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/aecb43c7-07e3-44e8-b43c-8e85b04d7de5)

 Paul-Bertz-Str. 3,
 09120 Chemnitz
 (Helbersdorf)
 3,9 km

 Geöffnet
  – Schließt um 18:00

 [Jung Uwe Dr. med. Zahnarztpraxis u. Jung Tatjana Dipl. med.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/9dab8f5b-b806-4eb0-b2ab-dfae09fb7b30)

 Annaberger Str. 71,
 09111 Chemnitz
 (Zentrum)
 939 m

 Geschlossen
  – Öffnet um 14:00""",

    "Halle": """[Economy

	Ahrens Stefan Dr. med. dent.

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/574bdb58-a780-477e-a706-0c7288454a00)

 Kröllwitzer Str. 15,
 06120 Halle
 (Kröllwitz)
 3 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Economy

	Näumayr Elke Dipl.-Stom.

 4,74.7000003

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/2ce7a5e6-22bb-4ca5-81c0-6fe5dc89d838)

 Am Treff 3,
 06124 Halle (Saale)
 (Südliche Neustadt)
 2,7 km

 [Economy

	Zahnärztepraxisgemeinschaft Borghardt, Hofmann und Voas

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/31594326-c79f-4ef5-a31d-a280e9fac126)

 Am Gastronom 17,
 06124 Halle
 (Westliche Neustadt)
 3,6 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Zeplin Sirko Dr. Zahnarztpraxis

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/13115f24-28d4-46d3-82b9-54e4b80cac3a)

 Marktplatz 19,
 06108 Halle (Saale)
 (Altstadt)
 228 m

 Geschlossen
  – Öffnet Dienstag um 10:00

	Webseite

 [Günther Constanze Zahnarztpraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/bc13d6a6-00b0-4f64-aba3-90de9209b327)

 Spitze 2,
 06108 Halle (Saale)
 (Altstadt)
 138 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Eppendorf Kirstin Dr. Zahnarzt Praxis

 5,05.0

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/f8913e85-a101-497d-8f13-40cd1c47458a)

 Leipziger Str. 93,
 06108 Halle (Saale)
 (Innenstadt)
 535 m

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Bertram Janine Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/11a4437a-e091-4ea1-88d4-1fc6b643d211)

 Talamtstr. 6,
 06108 Halle (Saale)
 (Altstadt)
 52 m

 Geöffnet
  – Schließt um 14:30

	Webseite

 [Reißmann A. Dr.med.dent

 4,84.8

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c7a5c937-e575-4a5c-9402-225cb6b8e788)

 Barfüßerstr. 17,
 06108 Halle

 371 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Artschwager Martin Dr.med.dent. Zahnarzt

 4,94.9

 8 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/3488dcd9-86a4-476f-93aa-b73aa78141df)

 Mansfelder Str. 44,
 06108 Halle (Saale)
 (Saaleaue)
 721 m

 Geschlossen
  – Öffnet Dienstag um 08:00

	Webseite

 [Ernst Andrea, Schenk Ulf Zahnarztpraxis

 4,74.7000003

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/f8123f41-ad22-4024-ba7b-8b978bde4b26)

 Große Steinstr. 15,
 06108 Halle (Saale)
 (Altstadt)
 461 m

 [Raue Alexander Zahnarztpraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/77503c71-0784-43fa-83a2-6d91339c93cd)

 Große Wallstr. 47,
 06108 Halle (Saale)
 (Innenstadt)
 596 m

 Geöffnet
  – Schließt um 19:00

	Webseite

 [Zahnarztpraxis Koehler und Hein

 5,05.0

 80 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/f2bdc26f-7259-4765-8d30-427fb45e00c9)

 Pfännerhöhe 23,
 06110 Halle
 (Innenstadt)
 1,3 km

 Geöffnet
  – Schließt um 16:00

	Webseite

 [Ende Brigitta Dipl.-Stom. Zahnarztpraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/a2a7fead-116f-40d9-8b4b-fffc78bc0b66)

 Lerchenfeldstr. 18,
 06110 Halle
 (Innenstadt)
 814 m

 Geöffnet
  – Schließt um 16:00

 [Beyer-Dames Ines Dr., Beyer Susanne

 5,05.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/8afe74aa-c0f7-4243-8d43-354758fc03a9)

 Leipziger Str. 48,
 06108 Halle (Saale)
 (Innenstadt)
 1 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Zahnarztpraxis Dr.med. Peter Liske

 4,94.9

 37 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/887b0080-7d7d-4f52-a42b-263738f8cbeb)

 Händelstr. 22,
 06114 Halle (Saale)
 (Giebichenstein)
 1,4 km

	Webseite

 [Schöder Angela Zahnarztpraxis

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c2fefa4b-17b6-4fac-be41-3c35b8cf39e5)

 Beesener Str. 4,
 06110 Halle
 (Innenstadt)
 1,1 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Wolf Sabine

 4,94.9

 8 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/01ab98df-c86a-47c6-9b8a-e42309c09b73)

 Carl-von-Ossietzky-Str. 21,
 06114 Halle
 (Paulusviertel)
 1,4 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Frehse Lars Zahnarzt

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/45e7aa28-5702-43a7-9533-942977ac8d20)

 Forsterstr. 20,
 06112 Halle (Saale)
 (Innenstadt)
 1,2 km

 [Labitzke Frank

 5,05.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1b0a2248-3ba7-4e15-81a1-804b453dd4c5)

 Mühlweg 37,
 06114 Halle (Saale)
 (Innenstadt)
 1,2 km

 [Mittenentzwei Wolfgang Zahnarztpraxis

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/e65bf8be-ea55-4389-a5db-df1d9f39da0a)

 Südstr. 61,
 06110 Halle
 (Innenstadt)
 1,2 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Osada Jakob Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/3505d709-55c0-4577-815f-60f3c6716611)

 Willy-Brandt-Str. 3,
 06110 Halle (Saale)
 (Innenstadt)
 963 m

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Benkenstein Hanna Zahnärztin

 3,03.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/1d4095d6-73fc-4725-9f39-48b6a1236ac7)

 Robert-Franz-Ring 1C,
 06108 Halle (Saale)
 (Innenstadt)
 252 m

 Geöffnet
  – Schließt um 19:00

	Webseite

 [Erbring Christoph Dr.

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c7b8eb38-2ef6-43ae-9bf6-87c2626c121d)

 Ludwig-Wucherer-Str. 57,
 06108 Halle
 (Paulusviertel)
 1,3 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Hoffmann Dr.med. Dietrich Zahnarztpraxis

 5,05.0

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/db1f7bc1-a133-45dc-8576-0604b02cf8c1)

 Willy-Lohmann-Str. 8,
 06114 Halle (Saale)
 (Paulusviertel)
 1,4 km

 Geöffnet
  – Schließt um 14:00

	Webseite

 [Schauer Sabine Zahnärztin

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ae9eda80-69e3-4381-bffa-5c01c9731898)

 Krukenbergstr. 26,
 06112 Halle
 (Innenstadt)
 1,1 km

 Geschlossen
  – Öffnet Dienstag um 08:00

	Webseite

 [Mika Vera Dipl.Stom.

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b5dd2051-2a8a-4e24-97e8-5bedbbdc93e0)

 Willy-Brandt-Str. 58,
 06110 Halle (Saale)

 1,3 km

 [Zahnarztpraxis Natalie Hevisov

 3,93.9

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/ac66e7dd-d403-4017-954b-43c6e1fcea75)

 Geiststr. 16,
 06108 Halle
 (Innenstadt)
 779 m

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Rösel Michael und Walter Dr. Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/68797be4-7dc9-4fcc-8510-10fe0f44bff4)

 Bernburger Str. 24,
 06108 Halle (Saale)
 (Innenstadt)
 1,2 km

 [Guzinski Uwe, Guzinski Heike Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b989d877-5e13-451d-921f-377da21ea536)

 Kurt-Tucholsky-Str. 28,
 06110 Halle (Saale)
 (Innenstadt)
 1,3 km

	Webseite

 [Mohaupt Volker Dr.med. Zahnarzt, Mohaupt Philipp Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/46a5da7b-b0cc-427e-909b-be330124062f)

 Mühlweg 48,
 06114 Halle (Saale)
 (Innenstadt)
 1,3 km

 [Böttcher Franka Dr.med. Zahnarztpraxis

 4,74.7000003

 3 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c9aa5cd9-7f49-4862-88e9-8a909f047542)

 Unstrutstr. 3,
 06122 Halle
 (Nördliche Neustadt)
 1,6 km

 Geöffnet
  – Schließt um 18:30

	Webseite

 [Reppel Rüdiger

 5,05.0

 4 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/da3da8d9-5477-4f42-92ea-79507f68f69f)

 Fischer-von-Erlach-Str. 29,
 06114 Halle (Saale)
 (Paulusviertel)
 2 km

 [Rennert Holm Dr. Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/45da2e80-8fc2-467d-8582-227e7844cd77)

 Reilstr. 129,
 06114 Halle (Saale)
 (Paulusviertel)
 1,6 km

 [Roger Barz Zahngesundheit Halle

 3,03.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/3232f377-921b-480a-bdbd-e13af4fc9372)

 Geiststr. 32,
 06108 Halle
 (Innenstadt)
 1 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Schmidt Dorothea

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/7c1110ea-d333-4b15-8f76-a5c0a340fb1d)

 Robert-Koch-Str. 29,
 06110 Halle (Saale)
 (Gesundbrunnen)
 2,2 km

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Fuchs Rayk-Uwe

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/5d92da1d-2292-47a0-90f5-2231d177f9ce)

 Ernst-Abbe-Str. 24B,
 06122 Halle (Saale)
 (Nördliche Neustadt)
 2,8 km

 [Zahnarztpraxis Michael Deutschmann

 5,05.0

 6 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/189c3902-987e-42e6-8a11-51260582173d)

 Paul-Suhr-Str. 53,
 06130 Halle (Saale)
 (Südstadt)
 3,2 km

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Köhler Uta Dipl.-Stom.

 5,05.0

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/81ad1f64-a8d7-40bb-a4eb-2b33f929a5f1)

 Elsa-Brändström-Str. 181,
 06110 Halle (Saale)
 (Gesundbrunnen)
 2,8 km

 [Blechschmidt Brit Dr. Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d640e829-bcef-4ea6-9cce-9b568de11540)

 Am Treff 3,
 06124 Halle (Saale)
 (Südliche Neustadt)
 2,7 km

 Geöffnet
  – Schließt um 15:00

 [Berger Lutz Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/43e9329a-21ce-4951-967d-2fd3a8d72375)

 Merseburger Str. 181,
 06112 Halle
 (Damaschkestraße)
 2,8 km

 Geöffnet
  – Schließt um 16:00

	Webseite

 [Brandt Annegret Dr. med. Zahnarztpraxis

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/d2ee2497-a5d2-4e4a-87fd-2f7f10dd4644)

 An der Petruskirche 21,
 06120 Halle (Saale)
 (Kröllwitz)
 2,8 km

	Webseite

 [Buchmann Thomas Dr. Zahnarzt

 5,05.0

 1 Bewertung

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/0d7fd6c9-4bfd-4f31-95f9-87ced1230bb4)

 Ernst-Grube-Str. 28,
 06120 Halle (Saale)
 (Kröllwitz)
 2,9 km

 Geöffnet
  – Schließt um 16:00

	Webseite

 [Reeg Wolfram Dr. Zahnarztpraxis

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/102d1af3-6d9e-46da-91c3-51c98ccfe60b)

 Salzgrafenstr. 1,
 06108 Halle (Saale)
 (Altstadt)
 53 m

 Geöffnet
  – Schließt um 18:00

	Webseite

 [Katschinski Marlies

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/27f39f42-7541-4e6a-98ff-3805aaca75c3)

 Oleariusstr. 9,
 06108 Halle (Saale)
 (Altstadt)
 75 m

 [Nettlau Roland Dr.med.

 4,24.2000003

 2 Bewertungen

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b29a5939-9c36-4bb6-8697-cc05cf79a2a5)

 Albert-Einstein-Str. 3,
 06122 Halle (Saale)
 (Nördliche Neustadt)
 2,7 km

 [Stephan Dr. Fachzahnärztin für Kieferorthopädie

 5,05.0

 2 Bewertungen

 Zahnärzte: Kieferorthopädie (Fachzahnärzte)](https://www.gelbeseiten.de/gsbiz/b53187aa-f8bd-4f12-90a9-f1b9481e1342)

 Am Bruchsee 4,
 06122 Halle (Saale)
 (Nördliche Neustadt)
 3,4 km

 Geöffnet
  – Schließt um 17:00

 [Klapproth Jana Dr.med.dent.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/c77b7807-28c5-40ff-819a-20d88cffbb39)

 Kleine Marktstr. 3,
 06108 Halle (Saale)
 (Altstadt)
 219 m

 [Otto Nikolas Dr.med.dent.

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/b146de8d-d012-46bf-ac79-7eaa64caf212)

 Kleinschmieden 6,
 06108 Halle
 (Altstadt)
 238 m

 Geschlossen
  – Öffnet um 15:00

	Webseite

 [Hillebrand R. Dr., Hillebrand K. Zahnärzte

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/6b079721-56f3-4036-907a-d3a17719f389)

 Große Ulrichstr. 1,
 06108 Halle (Saale)
 (Altstadt)
 245 m

 Geschlossen
  – Öffnet um 14:00

	Webseite

 [Schirner Susanne

 Zahnärzte](https://www.gelbeseiten.de/gsbiz/bf04bd63-8553-40fb-9648-b4bb3acf1291)

 Große Ulrichstr. 4,
 06108 Halle (Saale)
 (Altstadt)
 292 m"""
}


def parse_text(text, city):
    """Parse listings from raw text."""
    listings = []
    
    # Split by gsbiz URLs
    url_pattern = r'(https://www\.gelbeseiten\.de/gsbiz/[a-f0-9-]+)'
    segments = re.split(url_pattern, text)
    
    i = 1  # Start at 1 since segments[0] is before first URL
    while i < len(segments) - 1:
        url = segments[i]
        before = segments[i-1] if i > 0 else ""
        after = segments[i+1] if i+1 < len(segments) else ""
        
        # Extract name from the [name](url) markdown link
        # Format: [Name\n\nRating\n\nReviews\n\n Category](URL)
        # We need only the text before the first blank line (the name itself)
        # Remove partner prefix first, then extract the first line of content
        name_clean = before
        name_clean = re.sub(r'^(Silber Partner|Top Partner|Platin Partner|Premium Partner|Aus der Region|Gold Partner|Bronze Partner|Economy|Business|Comfort Partner|Basic Partner|First Class)\s+', '', name_clean)
        # Get the first non-empty line inside brackets
        bracket_match = re.search(r'\[([^\n]+)', name_clean)
        if not bracket_match:
            i += 2
            continue
        name = bracket_match.group(1).strip()
        
        if len(name) < 3:
            i += 2
            continue
        
        # Extract address from after URL
        lines = after.split('\n')
        addr_lines = []
        has_website = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if 'Webseite' in line:
                has_website = True
                continue
            if any(x in line for x in ['Geschlossen', 'Geöffnet', 'Bewertung', 'Zahnärzte:']):
                break
            if re.match(r'^[\d,.]+\s*km', line):
                continue
            if re.match(r'^\([^)]{1,60}\)$', line):
                continue
            if any(x in line for x in ['Häufige Fragen', 'Folgende Leistungen', 'Gelbe Seiten', 'Ratgeber']):
                break
            addr_lines.append(line)
        
        # Build address - first 3 lines typically contain street + postal/city
        address = ' '.join(addr_lines[:3]).strip()
        # Fix leading ) from markdown link trailing ) in after text
        address = re.sub(r'^\)[\s]*', '', address).strip()
        
        listings.append({
            "clinic_name": name,
            "address": address,
            "phone": "",
            "website": url if has_website else "",
            "city": city
        })
        
        i += 2
    
    # Deduplicate by URL
    seen = set()
    unique = []
    for l in listings:
        if l['website'] and l['website'] not in seen:
            seen.add(l['website'])
            unique.append(l)
        elif not l['website']:
            # Include non-website entries if name is unique
            key = l['clinic_name'].lower()
            if key not in seen:
                seen.add(key)
                unique.append(l)
    
    return unique


def main():
    all_listings = []
    
    for city, text in CITY_DATA.items():
        listings = parse_text(text, city)
        all_listings.extend(listings)
        print(f"  {city}: {len(listings)} listings")
    
    # Deduplicate by clinic name
    seen_names = set()
    final = []
    for l in all_listings:
        key = l['clinic_name'].lower().strip()
        if key not in seen_names:
            seen_names.add(key)
            final.append(l)
    
    output_path = r"C:\Users\steph\.qclaw-oversea\workspace\projects\chase\zahnarzte-leads\phase1\agent3_gelsenkirchen_aachen.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal unique listings: {len(final)}")
    print(f"Saved to: {output_path}")
    
    # Count by city
    from collections import Counter
    city_counts = Counter(l['city'] for l in final)
    for city, count in sorted(city_counts.items()):
        print(f"  {city}: {count}")


if __name__ == "__main__":
    main()
