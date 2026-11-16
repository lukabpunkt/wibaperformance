"""Teil 2 der Aufbereitung für wibaperformance.de.
Aufruf: python3 -I _raw/scripts/build.py <projektordner>
Voraussetzung: _raw/extract.json (aus extract.py)
Erzeugt: bilder/, daten/*.json, inhalte/seiten/*.md, design/*
"""
import os, re, sys, json, shutil, collections
from PIL import Image, ImageOps

ROOT = sys.argv[1]
RAW = os.path.join(ROOT, "_raw")
ex = json.load(open(os.path.join(RAW, "extract.json"), encoding="utf-8"))
MEDIA = {m["uri"]: m for m in ex["medien"]}
PAGES = {p["name"]: p for p in ex["seiten"]}
BASE = "https://www.wibaperformance.de"


def d(*p):
    path = os.path.join(ROOT, *p); os.makedirs(path, exist_ok=True); return path


def find(prefix):
    hits = [u for u in MEDIA if u.split("_", 1)[-1].startswith(prefix) or u.startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    return MEDIA[hits[0]]


img_index = []


def save(prefix, folder, name, rolle, seite, hinweis="", alt=""):
    """Original laden, EXIF-Drehung anwenden, als JPEG (q92) bzw. PNG (bei Transparenz) speichern."""
    m = find(prefix)
    src = os.path.join(ROOT, m["datei"])
    im = Image.open(src)
    orient = im.getexif().get(274)
    im = ImageOps.exif_transpose(im)
    has_alpha = im.mode in ("RGBA", "LA", "P") and src.lower().endswith(".png")
    ext = ".png" if has_alpha else ".jpg"
    dest = os.path.join(d(*folder.split("/")), name + ext)
    if has_alpha:
        im.save(dest, optimize=True)
    else:
        im.convert("RGB").save(dest, quality=92, optimize=True, progressive=True)
    rel = os.path.relpath(dest, ROOT)
    img_index.append({"datei": rel, "rolle": rolle, "breite": im.width, "hoehe": im.height,
                      "bytes": os.path.getsize(dest), "quelle_url": "https://static.wixstatic.com/media/" + m["uri"],
                      "wix_dateiname": (m.get("alts") or [""])[0] or m.get("wix_name", ""),
                      "seite": seite, "alt_vorschlag": alt,
                      "hinweis": "; ".join(x for x in [hinweis, "EXIF-Drehung angewendet" if orient and orient != 1 else ""] if x)})
    return rel


# ---------------- Logos ----------------
lg = Image.open(os.path.join(ROOT, find("7d88a5ddcb4c")["datei"])).convert("RGBA")
lg = lg.crop(lg.getbbox())
d("bilder", "logos")
shutil.copy(os.path.join(ROOT, find("7d88a5ddcb4c")["datei"]), os.path.join(ROOT, "bilder/logos/logo-original-2667x1611.png"))
lg.save(os.path.join(ROOT, "bilder/logos/logo-schwarz-transparent.png"), optimize=True)
alpha = lg.split()[3]
white = Image.new("RGBA", lg.size, (255, 255, 255, 0)); white.putalpha(alpha)
Image.composite(Image.new("RGBA", lg.size, (255, 255, 255, 255)), white, alpha).save(os.path.join(ROOT, "bilder/logos/logo-weiss-transparent.png"), optimize=True)
w2 = Image.new("RGBA", lg.size, (255, 255, 255, 0)); px = w2.load(); ap = alpha.load()
for y in range(lg.height):
    for x in range(lg.width):
        a = ap[x, y]
        if a: px[x, y] = (255, 255, 255, a)
w2.save(os.path.join(ROOT, "bilder/logos/logo-weiss-transparent.png"), optimize=True)
shutil.copy(os.path.join(ROOT, find("66d1c7e261dc")["datei"]), os.path.join(ROOT, "bilder/logos/logo-header-496x116.png"))
for n, note in (("logo-original-2667x1611.png", "Größte verfügbare Fassung (PNG, schwarz auf transparent, mit Rand). Keine SVG-Version auf Wix verfügbar."),
                ("logo-schwarz-transparent.png", "Auf Inhalt beschnitten, schwarz, transparent."),
                ("logo-weiss-transparent.png", "Automatisch erzeugte Negativ-Variante für dunkle Hintergründe."),
                ("logo-header-496x116.png", "Header-Version der alten Seite.")):
    w, h = Image.open(os.path.join(ROOT, "bilder/logos", n)).size
    img_index.append({"datei": "bilder/logos/" + n, "rolle": "logo", "breite": w, "hoehe": h,
                      "bytes": os.path.getsize(os.path.join(ROOT, "bilder/logos", n)), "quelle_url": "Wix-Medien (Logo)", "seite": "alle Seiten", "hinweis": note})

# ---------------- Hero / Seiten-Header ----------------
hero = save("709099a74a39", "bilder/hero", "werkstatt-wiba-wandlogo", "hero", "Startseite",
            "Werkstatt mit WIBA-Wandlogo, Mitarbeiter im Bild (Einverständnis klären)", "Werkstatt von WIBA Performance mit Wandlogo und eingeschweißten Reifensätzen")
hdr = {
    "reifenservice": save("42d0b68617ba", "bilder/seiten-header", "reifenservice", "seiten-header", "/produkte", "", "Reifenlager und Montiermaschine in der Werkstatt"),
    "klimaservice": save("d8d37beb2509", "bilder/seiten-header", "klimaservice", "seiten-header", "/dienstleistungen-1", "", "Klimaservice-Gerät an einem Kleinwagen mit offener Motorhaube"),
    "fahrzeugaufbereitung": save("8bed11ebb52f", "bilder/seiten-header", "fahrzeugaufbereitung", "seiten-header", "/dienstleistungen-2",
                                 "Hochformat-Screenshot (1170x2532), Mitarbeiter beim Polieren", "Mitarbeiter poliert ein Fahrzeug in der Werkstatt"),
    "ersatzteile": save("77679efeb4ec", "bilder/seiten-header", "ersatzteile-zubehoer", "seiten-header", "/dienstleistungen-3",
                        "Produkte mit Herstellerlogos (Mann-Filter, Bosch, Febi …) – eigenes Foto, Marken nur abgebildet", "Felgen, Reifen und Ersatzteile verschiedener Hersteller"),
    "agb": save("29390083a5f1", "bilder/seiten-header", "agb-felgenwaesche", "seiten-header", "/agb", "", "Felge eines weißen Fahrzeugs mit Schaum bei der Wäsche"),
}

# ---------------- Felgenservice ----------------
sortiment_def = [("Alufelgen", "d2825dfba229", "Alufelge mit Reifen"), ("Radnabenkappen", "893d6cb19f17", "Radnabenkappen verschiedener Marken"),
                 ("Zentrierringe", "4618593bda47", "Bunte Zentrierringe"), ("Radschrauben", "83de36818a31", "Radschrauben"),
                 ("RDKS-Sensoren", "9b6a5bb546a0", "Programmiergerät und RDKS-Sensoren"), ("Reifen", "fa96704aecd8", "Gestapelte Neureifen")]
sortiment = []
for i, (t, pre, alt) in enumerate(sortiment_def, 1):
    slug = t.lower().replace("ä", "ae").replace("-", "")
    sortiment.append({"titel": t, "bild": save(pre, "bilder/felgenservice/sortiment", f"{i:02d}-{slug}", "produktkategorie", "/services", "", alt)})
felg_gal = []
for i, pre in enumerate(["e62a62205b66", "c9f6f872ea57", "6ae369c293fa", "74ad28791700", "218b7a813188", "feccc3019547", "dd322b898e6d", "bae5cf9f1714", "8aa3a6700ba8"], 1):
    felg_gal.append(save(pre, "bilder/felgenservice/galerie", f"{i:02d}-kompletträder", "galerie", "/services", "", "Kompletträder mit Alufelgen in der Werkstatt"))
d("bilder", "video")
vid = ex["videos"][0]
shutil.copy(os.path.join(ROOT, vid["datei"]), os.path.join(ROOT, "bilder/video/felgen-rdks-480p.mp4"))
poster = save("6da4dac7fa7646dba7ade2ee4d5f8d19f000", "bilder/video", "felgen-rdks-poster", "video-poster", "/services, /über-uns", "Standbild des Videos, nur 716x720")
img_index.append({"datei": "bilder/video/felgen-rdks-480p.mp4", "rolle": "video", "breite": None, "hoehe": None,
                  "bytes": os.path.getsize(os.path.join(ROOT, "bilder/video/felgen-rdks-480p.mp4")), "quelle_url": vid.get("url"),
                  "seite": "/services, /über-uns", "hinweis": "Nur in 480p verfügbar (1080p/720p liefert Wix nicht). Für die neue Seite zu klein als Hero-Video."})

# ---------------- Reifenservice-Preise ----------------
reifen_bilder = {
    "montage": save("83fb21dd567a", "bilder/reifenservice", "01-reifenmontage", "preis-bild", "/produkte", "", "Reifen wird auf der Montiermaschine auf eine Alufelge gezogen"),
    "radwechsel": save("d873832218924", "bilder/reifenservice", "02-radwechsel", "preis-bild", "/produkte", "", "Radschrauben werden beim Radwechsel angezogen"),
    "auswuchten": save("6fac7ecd66a7", "bilder/reifenservice", "03-auswuchten", "preis-bild", "/produkte", "", "Kompletrad auf der Auswuchtmaschine"),
    "rdks": sortiment[4]["bild"],
    "altreifen": save("964fb7edcc28", "bilder/reifenservice", "05-altreifenentsorgung", "preis-bild", "/produkte", "", "Gestapelte Altreifen"),
}

# ---------------- Fahrzeugaufbereitung ----------------
aufb = []
for i, pre in enumerate(["1e4ed8cbc6ac", "9c3e2b239a82", "e21426bd624f", "dfba70a06172", "9e640628ee72", "ce95a4a00b30", "15103c701bc0",
                         "1bb4cc1224c5", "15c0541474c1", "c93c51fcb4b2", "430cf1de308a", "68202ac2d0ad", "9fd79b289889", "da24cac62774", "e8c6850f0cb1"], 1):
    note = "Vorher-Nachher-Collage" if pre in ("1e4ed8cbc6ac", "9c3e2b239a82", "e21426bd624f", "dfba70a06172", "c93c51fcb4b2") else ""
    aufb.append(save(pre, "bilder/fahrzeugaufbereitung", f"{i:02d}-aufbereitung", "galerie", "/dienstleistungen-2", note, "Fahrzeugaufbereitung"))

# ---------------- Ersatzteile ----------------
nabe = save("2ae890c9d924", "bilder/ersatzteile", "bmw-nabenkappen", "produkt", "/dienstleistungen-3", "BMW-Logo ist Markenzeichen; Produktfoto eigen", "BMW Nabenkappen")

# ---------------- Kunden ----------------
kunden_order = [l for l in PAGES["customer-name"]["bloecke"] if l["typ"] == "bild"]
kunden, seen = [], set()
for b in kunden_order:
    if b["uri"] in seen: continue
    seen.add(b["uri"])
    pre = b["uri"].split("_", 1)[1][:12]
    kunden.append(save(pre, "bilder/kunden", f"{len(kunden) + 1:02d}-kundenfahrzeug", "kundenfahrzeug", "/customer-name",
                       "Kennzeichen teils lesbar – vor Verwendung unkenntlich machen bzw. Einverständnis der Kunden klären", "Kundenfahrzeug mit Felgen von WIBA Performance"))

# ---------------- Social-Icons nur dokumentieren ----------------
for pre, n in (("01c3aff52f2a", "instagram-schwarz"), ("0fdef7512046", "facebook-schwarz"), ("23fd2a2be531", "facebook-weiss"),
               ("81af6121f84c", "instagram-weiss"), ("53dfd24b6fc7", "link-weiss"), ("a21cd4b9e8c0", "link-schwarz")):
    save(pre, "bilder/icons-alte-seite", n, "icon", "alle Seiten", "Wix-Standard-Icons, für die neue Seite nicht nötig")

# ---------------- Texte ----------------
def texts(name):
    return [b["md"] for b in PAGES[name]["bloecke"] if b["typ"] == "text"]

# Bewertungen: Text steht VOR dem Namen (Name als H2)
bew, buf = [], []
for t in texts("customer-name")[1:]:
    if t.startswith("## "):
        name = t[3:].strip()
        if name == "Bewertung hinzufügen": break
        txt = " ".join(buf).strip(); buf = []
        b = {"name": name, "text": txt, "quelle": "Seite 'Unsere Kunden' (vermutlich aus Google-Bewertungen übernommen)"}
        half = len(txt) // 2
        if txt[:half] == txt[half:]:
            b["text"] = txt[:half]; b["hinweis"] = "Text auf der alten Seite doppelt eingefügt"
        if re.search("[а-яА-Я]", txt):
            b["sprache"] = "ru"
            b["uebersetzung_de_sinngemaess"] = "Leute, vielen Dank, in kurzer Zeit wurde das Problem professionell behoben. Großen Respekt an Vitalik. Ich empfehle diesen Ort."
        if name == "D. Kindermann":
            b["hinweis"] = "Text beginnt auf der alten Seite mitten im Satz – Anfang fehlt, beim Kunden/Google nachsehen"
        bew.append(b)
    else:
        buf.append(t)

unternehmen = {
    "firmenname": "WIBA Performance",
    "zusatz": "Felgen- und Reifenhandel",
    "inhaber": "Witali Bakin",
    "rechtsform": "nicht angegeben (vermutlich Einzelunternehmen) – klären",
    "adresse": {"strasse": "Hackelbarg 7", "plz": "32369", "ort": "Rahden", "land": "Deutschland"},
    "telefon": {
        "mobil": {"anzeige": "0160 4151974", "alt_anzeige": "mobil.: 0160/4151974", "international": "+49 160 4151974", "tel_link": "tel:+491604151974"},
        "festnetz_laut_datenschutz": {"anzeige": "05776 3060088", "international": "+49 5776 3060088", "tel_link": "tel:+4957763060088"},
        "fax_laut_kontaktseite": {"anzeige": "05776 9619998", "international": "+49 5776 9619998"},
        "hinweis": "Festnetznummer steht nur in der Datenschutzerklärung, Fax nur auf der Kontaktseite. Welche Nummern sollen auf die neue Seite?",
    },
    "email": {
        "header_footer": "w.bakin@wibaperformance.de",
        "kontaktseite_und_datenschutz": "info@wibaperformance.de",
        "hinweis": "Zwei Adressen im Umlauf – mit Kunden klären, welche öffentlich genannt wird.",
    },
    "whatsapp": "In AGB/Datenschutz erwähnt (Bestellung per WhatsApp), aber keine Nummer/Link angegeben – vermutlich Mobilnummer.",
    "social": {"facebook": "https://www.facebook.com/wibaperformance", "instagram": "https://www.instagram.com/wiba_performance/",
               "tiktok": "https://www.tiktok.com/@wiba_performance"},
    "oeffnungszeiten": {"mo_fr": "nach Vereinbarung", "sa": "nach Vereinbarung", "so": "geschlossen"},
    "handelsregister": None, "ust_id": None,
    "impressum": "Auf der alten Seite NICHT vorhanden (Pflicht nach § 5 DDG). Angaben (Rechtsform, USt-ID, ggf. Steuernummer, Aufsichtsbehörde/Handwerkskammer) beim Kunden erfragen.",
    "gruendung": {"jahr": None, "hinweis": "Nicht angegeben. Domain seit 08.04.2021 registriert, Footer '©2021' – Gründung vermutlich 2021, beim Kunden bestätigen."},
    "leistungsbereiche": ["Reifenservice", "Felgenservice (Verkauf und Ankauf)", "Klimaservice", "Fahrzeugaufbereitung", "Ersatzteile & Zubehör"],
    "zielgruppe_aus_texten": "Auto-Liebhaber/Tuning-affine Privatkunden (Felgen, Eintragung, RDKS) und Alltagskunden (Reifenwechsel, Klima).",
    "einsatzgebiet": "Nicht angegeben; Standort Rahden (Kreis Minden-Lübbecke, NRW).",
    "claims_slogans": [
        "Willkommen bei WIBA Performance",
        "Mit uns fahren Sie gut und vor allem sicher!",
        "Die Klimaanlage kühlt nicht richtig? Wir regeln das!",
        "Suchen Sie nicht weiter – kommen Sie vorbei und lassen Sie sich von unserer großen Auswahl und unseren unschlagbaren Preisen überraschen.",
        "Unser Team besteht aus Automobil-Liebhabern mit vielen Jahren an Erfahrung.",
        "Wir garantieren Ihnen ein faires Angebot, das Ihren Erwartungen entspricht. (Felgenankauf)",
    ],
    "seo_alt": {"title": PAGES["index"]["titel"], "description": PAGES["index"]["meta"].get("description"),
                "keywords": PAGES["index"]["meta"].get("keywords"), "google_site_verification": PAGES["index"]["meta"].get("google-site-verification")},
    "hosting_alt": {"plattform": "Wix (Domain-DNS bei Wix: ns12/ns13.wixdns.net)", "email": "IONOS (MX mx00/mx01.ionos.de)", "domain_registriert": "2021-04-08 (DENIC)",
                    "hinweis": "Kein SPF-TXT-Eintrag gefunden (Zustellbarkeit E-Mails). Wix kann kein eigenes statisches HTML hosten → neuer Hoster nötig."},
}

leistungen = {
    "reifenservice": {
        "alte_url": BASE + "/produkte", "seitentitel_alt": "Reifen- und Felgenservice | WIBA Performance", "headerbild": hdr["reifenservice"],
        "intro": texts("produkte")[1],
        "preise": [
            {"titel": "Reifenmontage", "beschreibung": "inkl. Wuchten, Montieren und Luftdruck prüfen", "bild": reifen_bilder["montage"],
             "positionen": [["bis 17 Zoll", "12,50 €"], ["18 und 19 Zoll", "15,00 €"], ["ab 20 Zoll", "17,50 €"]]},
            {"titel": "Radwechsel", "beschreibung": "Rad wechseln, Luftdruck und Profiltiefe prüfen", "bild": reifen_bilder["radwechsel"],
             "positionen": [["Pkw", "25,00 €"], ["Transporter", "30,00 €"]]},
            {"titel": "Auswuchten", "beschreibung": "Rad auswuchten inkl. Auswuchtgewichte", "bild": reifen_bilder["auswuchten"],
             "positionen": [["Stahlfelge", "5,00 €"], ["Alufelge", "7,50 €"]], "hinweis": "Vermutlich Preis pro Rad – klären"},
            {"titel": "RDKS-Sensoren", "beschreibung": "Reifendruck-Kontrollsystem", "bild": reifen_bilder["rdks"],
             "positionen": [["4 RDKS-Sensoren anlernen", "15,00 €"], ["4 RDKS-Sensoren programmieren", "25,00 €"]]},
            {"titel": "Altreifenentsorgung", "beschreibung": "Pkw und Kleintransporter", "bild": reifen_bilder["altreifen"],
             "positionen": [["pro Reifen", "3,00 €"]]},
        ],
        "hinweis": "Preise Stand Abruf 13.11.2026, ob inkl. MwSt. nicht angegeben – klären. Reifenmontage-Preis vermutlich pro Rad.",
    },
    "felgenservice": {
        "alte_url": BASE + "/services", "video": "bilder/video/felgen-rdks-480p.mp4", "video_poster": poster,
        "felgenverkauf": texts("services")[1].split("**Felgenankauf**")[0].replace("Felgenverkauf ", "", 1).strip(),
        "felgenankauf": texts("services")[1].split("**Felgenankauf**")[1].strip(),
        "sortiment_titel": "bei uns erhältlich", "sortiment": sortiment, "galerie": felg_gal,
    },
    "klimaservice": {
        "alte_url": BASE + "/dienstleistungen-1", "headerbild": hdr["klimaservice"],
        "claim": "Die Klimaanlage kühlt nicht richtig? Wir regeln das!",
        "text": texts("dienstleistungen-1")[2],
        "preise": [["Klimaanlage befüllen (R134a)", "120,00 €"], ["Klimaanlage befüllen und desinfizieren (R134a)", "150,00 €"], ["Druckprüfung", "ab 40,00 €"]],
        "hinweis": "Nur Kältemittel R134a genannt. Neuere Fahrzeuge (ab ca. 2017) nutzen R1234yf – fragen, ob das auch angeboten wird. '15 % Kältemittelverlust pro Jahr' ist eine Herstelleraussage, die üblich zitiert wird (oft 10–15 %).",
    },
    "fahrzeugaufbereitung": {"alte_url": BASE + "/dienstleistungen-2", "headerbild": hdr["fahrzeugaufbereitung"],
                             "text": texts("dienstleistungen-2")[1], "galerie": aufb,
                             "hinweis": "Keine Preise oder Pakete angegeben. Fünf Bilder sind Vorher-Nachher-Collagen."},
    "ersatzteile_zubehoer": {"alte_url": BASE + "/dienstleistungen-3", "headerbild": hdr["ersatzteile"],
                             "text": texts("dienstleistungen-3")[1].strip("*").replace("unsren", "unseren"),
                             "produkte": [{"titel": "BMW Nabenkappen", "preis": "20,00 €", "bild": nabe, "hinweis": "Einziges Produkt; Menge (Satz à 4?) unklar"}]},
}

ueber_uns = {"alte_url": BASE + "/über-uns", "video": "bilder/video/felgen-rdks-480p.mp4",
             "text_original": texts("über-uns")[1],
             "text_korrigiert_vorschlag": texts("über-uns")[1].replace("WIBA Performance gegründet", "Wir haben WIBA Performance gegründet"),
             "hinweis": "Originalsatz beginnt grammatisch unvollständig ('WIBA Performance gegründet, um …'). Kein Gründungsjahr, keine Teamgröße."}

gewinnspiel = {"alte_url": BASE + "/gewinnspiel-jetzt-mitmachen", "zeitraum": "12.02.2026 – 04.03.2026",
               "status": "ABGELAUFEN (Abruf 13.11.2026) – Seite ist noch online und verlinkt",
               "preise": [["Platz 1", "2x Radwechsel, 1 Jahr kostenlose Reifenlagerung und 2x Radwäsche – Gesamtwert 250 €"],
                          ["Platz 2", "Professionelle Fahrzeugaufbereitung im Wert von 150 €"], ["Platz 3", "Kompletter Klimaservice im Wert von 120 €"],
                          ["Platz 4", "Hochwertiges Autopflege-Set im Wert von 85 €"], ["Platz 5", "Reifenmontage für 1 Satz Reifen im Wert von 75 €"]],
               "hinweise": ["Platzhalter '[E-Mail / Telefon / WhatsApp]' in den Teilnahmebedingungen nicht ausgefüllt",
                            "Erwähnt 'Reifenlagerung' und 'Radwäsche' – Leistungen, die sonst nirgends auf der Seite stehen. Beim Kunden nachfragen (Reifeneinlagerung als Leistung?)"]}

d("daten")
def dump(name, obj):
    json.dump(obj, open(os.path.join(ROOT, "daten", name), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

dump("unternehmen.json", unternehmen)
dump("leistungen.json", leistungen)
dump("bewertungen.json", {"titel_alt": "Unsere Kunden", "bewertungen": bew, "kundenfahrzeuge_galerie": kunden,
                          "aufruf": "Kundenzufriedenheit ist uns extrem wichtig und wir freuen uns, wenn du uns deine Eindrücke und Feedback mitteilen könntest. Es wäre toll, wenn du dir kurz die Zeit nimmst, eine Bewertung bei Google zu schreiben.",
                          "hinweis": "Kein Google-Bewertungslink und keine Sternezahl auf der alten Seite. Anzahl/Schnitt der Google-Bewertungen beim Kunden erfragen, nicht erfinden."})
dump("startseite.json", {"hero_bild": hero, "headline": "Willkommen bei WIBA Performance", "text": texts("index")[1],
                         "oeffnungszeiten": unternehmen["oeffnungszeiten"],
                         "hinweis": "Alte Startseite hat eine große leere Fläche zwischen Text und Öffnungszeiten (Desktop)."})
dump("ueber-uns.json", ueber_uns)
dump("gewinnspiel.json", gewinnspiel)

nav = [
    {"label": "Start", "alte_url": BASE + "/"}, {"label": "Reifenservice", "alte_url": BASE + "/produkte"},
    {"label": "Felgenservice", "alte_url": BASE + "/services"}, {"label": "Klimaservice", "alte_url": BASE + "/dienstleistungen-1"},
    {"label": "Fahrzeugaufbereitung", "alte_url": BASE + "/dienstleistungen-2"}, {"label": "Ersatzteile & Zubehör", "alte_url": BASE + "/dienstleistungen-3"},
    {"label": "Unsere Kunden und Bewertungen", "alte_url": BASE + "/customer-name"}, {"label": "Über uns", "alte_url": BASE + "/%C3%BCber-uns"},
    {"label": "Kontakt", "alte_url": BASE + "/kontakt"},
    {"label": "AGB & Datenschutz", "alte_url": BASE + "/agb", "ort": "Footer"},
    {"label": "Gewinnspiel", "alte_url": BASE + "/gewinnspiel-jetzt-mitmachen", "ort": "nur über Sitemap/Direktlink"},
]
crawl = json.load(open(os.path.join(RAW, "crawl-render.json"), encoding="utf-8"))

# ---------------- Markdown-Seiten ----------------
page_defs = [("index", "01-startseite"), ("produkte", "02-reifenservice"), ("services", "03-felgenservice"), ("dienstleistungen-1", "04-klimaservice"),
             ("dienstleistungen-2", "05-fahrzeugaufbereitung"), ("dienstleistungen-3", "06-ersatzteile-zubehoer"), ("customer-name", "07-kunden-bewertungen"),
             ("über-uns", "08-ueber-uns"), ("kontakt", "09-kontakt"), ("agb", "10-agb-datenschutz"), ("gewinnspiel-jetzt-mitmachen", "11-gewinnspiel")]
d("inhalte", "seiten")
alle = []
for name, slug in page_defs:
    p = PAGES[name]
    body = []
    for b in p["bloecke"]:
        if b["typ"] == "text": body.append(b["md"])
        elif b["typ"] == "bild":
            hit = [x for x in img_index if x["quelle_url"].endswith(b["uri"])]
            body.append(f"![{b.get('alt','')}]({'../../' + hit[0]['datei'] if hit else b['uri']})")
        elif b["typ"] == "video": body.append("[Video: ../../bilder/video/felgen-rdks-480p.mp4]")
        elif b["typ"] == "button": body.append(f"[Button: {b['text']}]({b['href']})")
    desc = (p["meta"].get("description") or "").replace('"', "'")
    fm = f"---\nalte_url: {p['url']}\nseitentitel: \"{p['titel']}\"\nmeta_description: \"{desc}\"\nmeta_keywords: \"{p['meta'].get('keywords','')}\"\n---\n\n"
    open(os.path.join(ROOT, "inhalte", "seiten", slug + ".md"), "w", encoding="utf-8").write(fm + "\n\n".join(body) + "\n")
    alle.append({"datei": f"inhalte/seiten/{slug}.md", "alte_url": p["url"], "seitentitel": p["titel"], "meta_description": p["meta"].get("description"),
                 "h1": next((h for h in p["headings"] if h.startswith("H1")), None)})
dump("navigation-sitemap.json", {"hauptnavigation": nav, "alle_seiten": alle,
                                 "externe_links": sorted(set(l.split(" | ")[0] for l in crawl["external_links"])),
                                 "hinweis": "Wix-Slugs sind nichtssagend (/services = Felgenservice, /produkte = Reifenservice, /dienstleistungen-1..3, /customer-name). Alle per 301 auf sprechende URLs umleiten."})
dump("bilder-index.json", img_index)

# ---------------- Farben ----------------
d("design")
def quant(path, n=6):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB"); im.thumbnail((300, 300))
    q = im.quantize(n, method=Image.MEDIANCUT); pal = q.getpalette()[:n * 3]; cnt = sorted(q.getcolors(), reverse=True)
    return [{"hex": "#%02X%02X%02X" % tuple(pal[i * 3:i * 3 + 3]), "anteil": round(c / (im.width * im.height), 3)} for c, i in cnt]

bildwelt = {"hero_werkstatt": quant(os.path.join(ROOT, hero)), "reifenservice": quant(os.path.join(ROOT, hdr["reifenservice"])),
            "felgen_alufelge": quant(os.path.join(ROOT, sortiment[0]["bild"])), "felgen_galerie_1": quant(os.path.join(ROOT, felg_gal[1])),
            "klimaservice": quant(os.path.join(ROOT, hdr["klimaservice"])), "aufbereitung": quant(os.path.join(ROOT, hdr["fahrzeugaufbereitung"]))}
json.dump(bildwelt, open(os.path.join(ROOT, "design", "bildwelt-farben.json"), "w"), ensure_ascii=False, indent=2)

farben = {
    "logo": {"schwarz": "#06070A", "hinweis": "Logo ist einfarbig schwarz (Pixelanalyse: #060708). Keine Markenfarbe vorhanden."},
    "alte_seite_tatsaechlich_verwendet": [
        {"hex": "#000000", "rolle": "Footer-Fläche, Cookie-Button"}, {"hex": "#04040C", "rolle": "Text/Überschriften (Wix color_37)"},
        {"hex": "#FFFFFF", "rolle": "Hintergrund"}, {"hex": "#F0F0F0", "rolle": "Kartenköpfe 'bei uns erhältlich', Footer-Unterleiste"},
        {"hex": "#767676", "rolle": "Sekundärtext (color_44)"}],
    "wix_vorlagen_palette_ungenutzt": {"hex": ["#AABCBF", "#E1EFF2", "#A2A2E0", "#4646C1", "#232369", "#4793A3"],
                                        "hinweis": "Standardpalette der Wix-Vorlage (Lila/Petrol), auf der Seite praktisch nicht sichtbar."},
    "bildwelt_dominant": "Werkstatt-Weiß/Grau, Reifenschwarz, Felgen-Anthrazit und gebürstetes Silber; Akzente: Werkzeug-Blau (Montiermaschine, Klimagerät #2E6FB0-artig), Rot der RDKS-Verpackungen.",
}
json.dump(farben, open(os.path.join(ROOT, "design", "farben.json"), "w"), ensure_ascii=False, indent=2)
open(os.path.join(ROOT, "design", "design-tokens.css"), "w").write(""":root {
  /* Alte Seite (Bestand) – WIBA Performance */
  --wiba-logo-schwarz: #06070A;
  --wiba-text: #04040C;
  --wiba-bg: #FFFFFF;
  --wiba-flaeche: #F0F0F0;
  --wiba-sekundaer: #767676;
  --wiba-footer: #000000;
  /* Schriften der alten Seite */
  --wiba-font-head: "Barlow", sans-serif;      /* Medium 500 für Überschriften, ExtraLight 200 für Lead */
  --wiba-font-body: "Avenir LT W01 35 Light", "Avenir", sans-serif;  /* Wix-Lizenzschrift, nicht übertragbar */
}
""")
sw = lambda h, l: f'<div class="sw"><i style="background:{h}"></i><b>{h}</b><span>{l}</span></div>'
bw_html = "".join(f"<h3>{k}</h3><div class='row'>" + "".join(sw(c["hex"], f"{int(c['anteil'] * 100)} %") for c in v) + "</div>" for k, v in bildwelt.items())
open(os.path.join(ROOT, "design", "farbpalette.html"), "w").write(f"""<!doctype html><html lang="de"><meta charset="utf-8"><title>WIBA Farbpalette</title>
<style>body{{font:15px system-ui;margin:32px;color:#111}} .row{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:24px}} .sw{{width:150px}} .sw i{{display:block;height:80px;border-radius:6px;border:1px solid #ddd}} .sw b{{display:block;margin-top:6px}} .sw span{{color:#555;font-size:13px}} img{{height:60px;margin:8px 0 24px}}</style>
<h1>WIBA Performance – Farben der alten Seite</h1>
<img src="../bilder/logos/logo-schwarz-transparent.png" alt="Logo">
<h2>Tatsächlich verwendet</h2><div class="row">{''.join(sw(c['hex'], c['rolle']) for c in farben['alte_seite_tatsaechlich_verwendet'])}</div>
<h2>Wix-Vorlagenpalette (ungenutzt)</h2><div class="row">{''.join(sw(h, 'Vorlage') for h in farben['wix_vorlagen_palette_ungenutzt']['hex'])}</div>
<h2>Bildwelt (Image.quantize)</h2>{bw_html}</html>""")
print("Bilder:", len(img_index), "Bewertungen:", len(bew), "Kunden:", len(kunden))
