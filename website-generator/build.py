"""Baut die statische Website von WIBA Performance.

Aufruf (aus dem Ordner wibaperformance):
    python3 -I website-generator/build.py

Liest daten/*.json und bilder/, schreibt nach website/.
Seitentexte stehen in diesem Generator (Abschnitt SEITEN), Preise und Bewertungen
kommen aus daten/leistungen.json und daten/bewertungen.json.
CSS, JS und Schrift liegen fest unter website/assets/ und werden nicht überschrieben.
Hinweis: System-Python 3.9 – in f-Strings keine gleichen Anführungszeichen im Ausdruck.
"""
import glob
import html
import json
import os
import shutil
from datetime import date
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "website")
DOMAIN = "https://www.wibaperformance.de"
E = html.escape
HEUTE = date.today()


def lade(name):
    return json.load(open(os.path.join(ROOT, "daten", name), encoding="utf-8"))


FIRMA = lade("unternehmen.json")
LEIST = lade("leistungen.json")
BEW = lade("bewertungen.json")
AGB = lade("agb.json")

FIRMENNAME = "WIBA Performance"
INHABER = "Witali Bakin"
STRASSE, PLZ, ORT = "Hackelbarg 7", "32369", "Rahden"
TEL_ANZEIGE = "0160 4151974"
TEL_INT = "+49 160 4151974"
TEL_LINK = "tel:+491604151974"
MAIL = "info@wibaperformance.de"
MAPS_ROUTE = "https://www.google.com/maps/dir/?api=1&destination=Hackelbarg+7%2C+32369+Rahden"
MAPS_EMBED = "https://www.google.com/maps?q=Hackelbarg+7,+32369+Rahden&output=embed"
GOOGLE_BEWERTUNG = "https://www.google.com/maps/search/?api=1&query=WIBA+Performance+Rahden"
SOZIAL = [("Instagram", FIRMA["social"]["instagram"]), ("Facebook", FIRMA["social"]["facebook"]), ("TikTok", FIRMA["social"]["tiktok"])]

# ---------------------------------------------------------------- Bilder
IMG_OUT = os.path.join(OUT, "assets", "img")
IMG = {}


def quelle(muster):
    treffer = sorted(glob.glob(os.path.join(ROOT, muster)))
    assert treffer, muster
    return treffer[0]


def make_img(key, src, widths=(800, 1600), quality=78, box=None, schwarz_weg=False):
    """Skaliert ein Bild auf mehrere Breiten (progressives JPEG). box = (l, o, r, u) als Anteile."""
    im = Image.open(src if os.path.isabs(src) else os.path.join(ROOT, src)).convert("RGB")
    if schwarz_weg:
        im = im.crop(im.convert("L").point(lambda v: 255 if v > 18 else 0).getbbox())
    if box:
        W, H = im.size
        im = im.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))
    os.makedirs(IMG_OUT, exist_ok=True)
    out = []
    for w in widths:
        w2 = min(w, im.width)
        if any(o[1] == w2 for o in out):
            continue
        h2 = round(im.height * w2 / im.width)
        fn = "{}-{}.jpg".format(key, w2)
        im.resize((w2, h2), Image.LANCZOS).save(os.path.join(IMG_OUT, fn), "JPEG", quality=quality, optimize=True, progressive=True)
        out.append((fn, w2, h2))
    IMG[key] = out
    return key


def pic(key, alt, sizes="100vw", cls="", eager=False, base="", extra=""):
    v = IMG[key]
    klein = v[0]
    srcset = ", ".join("{}assets/img/{} {}w".format(base, fn, w) for fn, w, h in v)
    attrs = ' class="{}"'.format(cls) if cls else ""
    laden = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return ('<img src="{b}assets/img/{f}" srcset="{s}" sizes="{z}" width="{w}" height="{h}" alt="{a}" {l} decoding="async"{c}{x}>'
            .format(b=base, f=klein[0], s=srcset, z=sizes, w=klein[1], h=klein[2], a=E(alt), l=laden, c=attrs, x=extra))


def gross(key, base=""):
    return "{}assets/img/{}".format(base, IMG[key][-1][0])


AUFB_VN = [("01", "Innenraum"), ("02", "Fußraum"), ("04", "Sitze"), ("10", "Türdichtung")]
AUFB_GALERIE = ["05", "06", "07", "08", "09", "11", "12", "13", "14", "15"]
SORTIMENT = [("alufelgen", "Alufelgen", "Verkauf und Ankauf"), ("reifen", "Reifen", "fast aller Hersteller"),
             ("rdkssensoren", "RDKS-Sensoren", "anlernen und programmieren"), ("radnabenkappen", "Radnabenkappen", "für viele Marken"),
             ("radschrauben", "Radschrauben", "passend zur Felge"), ("zentrierringe", "Zentrierringe", "für den sauberen Sitz")]


def bilder_vorbereiten():
    if os.path.isdir(IMG_OUT):
        shutil.rmtree(IMG_OUT)
    make_img("felgen-hero", quelle("bilder/felgenservice/galerie/04-*"), widths=(800, 1600, 2000))
    make_img("werkstatt", "bilder/hero/werkstatt-wiba-wandlogo.jpg")
    make_img("polieren", "bilder/seiten-header/fahrzeugaufbereitung.jpg", schwarz_weg=True)
    make_img("reifenlager", "bilder/seiten-header/reifenservice.jpg")
    make_img("klima", "bilder/seiten-header/klimaservice.jpg")
    make_img("teile", "bilder/seiten-header/ersatzteile-zubehoer.jpg")
    make_img("montage", "bilder/reifenservice/01-reifenmontage.jpg", widths=(480, 800, 1600))
    make_img("radwechsel", "bilder/reifenservice/02-radwechsel.jpg")
    make_img("auswuchten", "bilder/reifenservice/03-auswuchten.jpg")
    make_img("altreifen", "bilder/reifenservice/05-altreifenentsorgung.jpg")
    make_img("nabenkappen", "bilder/ersatzteile/bmw-nabenkappen.jpg")
    make_img("video-poster", "bilder/video/felgen-rdks-poster.jpg", widths=(716,))
    og = Image.open(os.path.join(ROOT, "bilder/hero/werkstatt-wiba-wandlogo.jpg")).convert("RGB")
    W, H = og.size
    h = round(W * 630 / 1200)
    top = int(H * .03)
    og.crop((0, top, W, top + h)).resize((1200, 630), Image.LANCZOS).save(os.path.join(IMG_OUT, "og-wiba.jpg"), "JPEG", quality=82, progressive=True)
    for slug, _, _ in SORTIMENT:
        make_img("sort-" + slug, quelle("bilder/felgenservice/sortiment/*-{}.*".format(slug)), widths=(480, 800, 1200, 1600))
    for i in range(1, 10):
        make_img("felgen-{:02d}".format(i), quelle("bilder/felgenservice/galerie/{:02d}-*".format(i)), widths=(480, 800, 1200, 1600))
    for i in range(1, 23):
        make_img("kunde-{:02d}".format(i), quelle("bilder/kunden/{:02d}-*".format(i)), widths=(480, 800, 1600))
    for n in AUFB_GALERIE:
        make_img("aufb-" + n, quelle("bilder/fahrzeugaufbereitung/{}-*".format(n)), widths=(480, 800, 1600))
    for n, _ in AUFB_VN:  # Collagen: links vorher, rechts nachher
        src = quelle("bilder/fahrzeugaufbereitung/{}-*".format(n))
        make_img("vn-{}-vorher".format(n), src, widths=(720,), box=(0, 0, .5, 1))
        make_img("vn-{}-nachher".format(n), src, widths=(720,), box=(.5, 0, 1, 1))


# ---------------------------------------------------------------- Bausteine
NAV_DESK = [("reifenservice/", "Reifen"), ("felgenservice/", "Felgen"), ("klimaservice/", "Klima"),
            ("fahrzeugaufbereitung/", "Aufbereitung"), ("kunden/", "Kunden"), ("kontakt/", "Kontakt")]
NAV_ALLE = [("", "Start"), ("reifenservice/", "Reifenservice"), ("felgenservice/", "Felgenservice"), ("klimaservice/", "Klimaservice"),
            ("fahrzeugaufbereitung/", "Fahrzeugaufbereitung"), ("ersatzteile-zubehoer/", "Ersatzteile & Zubehör"),
            ("kunden/", "Kunden & Bewertungen"), ("ueber-uns/", "Über uns"), ("kontakt/", "Kontakt")]

I_TEL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>'
I_MAIL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/></svg>'
I_PFEIL = '<svg class="pfeil" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
I_LINKS = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>'
I_RECHTS = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
I_HOCH = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>'
I_ZU = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
I_REGLER = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M9 6l-6 6 6 6M15 6l6 6-6 6"/></svg>'
I_SOZIAL = {
    "Instagram": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    "Facebook": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8.5V6.8c0-.8.5-1.3 1.4-1.3H17V2.2h-2.6C11.6 2.2 10.3 4 10.3 6.6v1.9H7.8V12h2.5v9.8H14V12h2.7l.5-3.5H14z"/></svg>',
    "TikTok": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 2h-3.3v13.2a2.9 2.9 0 1 1-2.1-2.8V9a6.3 6.3 0 1 0 5.4 6.2V8.6a7.6 7.6 0 0 0 4.4 1.4V6.7a4.4 4.4 0 0 1-4.4-4.7z"/></svg>',
}


def preis(v):
    return "{:,.2f} €".format(v).replace(",", "X").replace(".", ",").replace("X", ".")


def zettel_daten():
    """Auftragszettel: alle Festpreise aus daten/leistungen.json."""
    r = LEIST["reifenservice"]["preise"]
    k = LEIST["klimaservice"]["preise"]
    def wert(s):
        return float(s.replace("ab", "").replace("€", "").replace(",", ".").strip())
    return [
        {"name": "Reifenmontage", "frage": "Felgengröße", "info": r[0]["beschreibung"],
         "optionen": [["bis 17″", wert(r[0]["positionen"][0][1])], ["18–19″", wert(r[0]["positionen"][1][1])], ["ab 20″", wert(r[0]["positionen"][2][1])]]},
        {"name": "Radwechsel", "frage": "Fahrzeug", "info": r[1]["beschreibung"],
         "optionen": [["Pkw", wert(r[1]["positionen"][0][1])], ["Transporter", wert(r[1]["positionen"][1][1])]]},
        {"name": "Auswuchten", "frage": "Felge", "info": r[2]["beschreibung"],
         "optionen": [["Stahlfelge", wert(r[2]["positionen"][0][1])], ["Alufelge", wert(r[2]["positionen"][1][1])]]},
        {"name": "RDKS-Sensoren", "frage": "4 Sensoren", "info": "Reifendruck-Kontrollsystem",
         "optionen": [["anlernen", wert(r[3]["positionen"][0][1])], ["programmieren", wert(r[3]["positionen"][1][1])]]},
        {"name": "Klimaservice", "frage": "Umfang", "info": "Kältemittel R134a",
         "optionen": [["Befüllen", wert(k[0][1])], ["Befüllen + Desinfektion", wert(k[1][1])], ["Druckprüfung", wert(k[2][1]), True]]},
        {"name": "Altreifen", "frage": "Entsorgung", "info": r[4]["beschreibung"], "optionen": [["pro Reifen", wert(r[4]["positionen"][0][1])]]},
        {"name": "Aufbereitung", "frage": "Umfang", "info": "Preis nach Fahrzeug und Zustand",
         "optionen": [["Innen", "Auf Anfrage"], ["Außen", "Auf Anfrage"], ["Innen und außen", "Auf Anfrage"]]},
        {"name": "Felgen", "frage": "Anliegen", "info": "Mit Hilfe bei Eintragung, Gutachten und RDKS",
         "optionen": [["kaufen", "Auf Anfrage"], ["verkaufen", "Auf Anfrage"]]},
    ]


def zettel(start="", titel="Ihr Auftrag"):
    return """<div class="drucker" data-start="{s}" data-mail="{m}">
  <div class="schlitz" aria-hidden="true"></div>
  <div class="zettel-clip">
    <form class="zettel" aria-label="Leistung und Preis auswählen">
      <div class="zettel-kopf"><h3>{t}</h3><span>WIBA Performance</span></div>
      <fieldset class="gruppe"><legend>Leistung</legend><div class="chips z-leistung"></div></fieldset>
      <fieldset class="gruppe"><legend class="z-option-titel">Größe</legend><div class="chips z-option"></div></fieldset>
      <div class="summe"><div><b class="z-titel">Reifenmontage</b><small class="z-info"></small></div><output aria-live="polite">–</output></div>
      <p class="zettel-hinweis z-hinweis">Festpreis laut Preisliste, inklusive MwSt. Termine nach Vereinbarung.</p>
      <div class="zettel-aktion"><a class="btn btn-tinte z-mail" href="mailto:{m}">Anfrage senden</a><a class="btn btn-line" href="{tl}">Anrufen</a></div>
    </form>
  </div>
</div>""".format(s=E(start), m=MAIL, t=E(titel), tl=TEL_LINK)


def vn_modul(base):
    reiter = "".join(
        '<button type="button" aria-pressed="{p}" data-vor="{b}assets/img/{v}" data-nach="{b}assets/img/{n}">{l}</button>'.format(
            p="true" if i == 0 else "false", b=base, v=IMG["vn-{}-vorher".format(n)][0][0], n=IMG["vn-{}-nachher".format(n)][0][0], l=l)
        for i, (n, l) in enumerate(AUFB_VN))
    n0 = AUFB_VN[0][0]
    return """<div class="vn-modul" data-reveal>
  <div class="reiter" role="group" aria-label="Beispiel wählen">{r}</div>
  <div class="vn">
    {vor}
    {nach}
    <span class="tag l">Vorher</span><span class="tag r">Nachher</span><span class="linie"></span>
    <input type="range" min="0" max="100" value="50" aria-label="Vorher-Nachher-Vergleich: nach links mehr Nachher, nach rechts mehr Vorher">
    <span class="knopf">{i}</span>
  </div>
</div>""".format(r=reiter, i=I_REGLER,
                 vor=pic("vn-{}-vorher".format(n0), "Vorher: Innenraum", "(min-width: 1000px) 45vw, 100vw", "vor", base=base),
                 nach=pic("vn-{}-nachher".format(n0), "Nachher: Innenraum", "(min-width: 1000px) 45vw, 100vw", "nach", base=base))


def galerie(keys_alts, base, vier=False):
    knoepfe = "".join(
        '<li style="list-style:none"><button type="button" data-full="{f}" data-cursor="Ansehen" aria-label="Bild vergrößern: {a}">{p}</button></li>'.format(
            f=gross(k, base), a=E(a), p=pic(k, a, "(min-width: 1150px) 25vw, (min-width: 760px) 33vw, 50vw", base=base))
        for k, a in keys_alts)
    return '<ul class="galerie{v}" style="padding:0;margin:0">{k}</ul>'.format(v=" vier" if vier else "", k=knoepfe)


def quer_galerie(base, titel="Bei uns erhältlich", mit_felgen=True):
    figs = []
    for slug, name, info in SORTIMENT:
        figs.append((("sort-" + slug), name, info))
    if mit_felgen:
        figs += [("felgen-03", "Kompletträder", "Felge und Reifen"), ("felgen-09", "Alufelgen", "Hilfe bei Eintragung"), ("felgen-06", "Kompletträder", "aus der Werkstatt")]
    items = "".join(
        '<figure data-cursor="Ansehen"><div class="rahmen">{p}</div><figcaption>{n} <small>{i}</small></figcaption></figure>'.format(
            p=pic(k, n, "(min-width: 760px) 400px, 72vw", base=base), n=E(n), i=E(i)) for k, n, i in figs)
    return """<section class="quer" aria-label="{t}">
  <div class="quer-buehne">
    <div class="wrap"><div class="quer-kopf"><h2 class="h2" data-split>{t}</h2><span class="zaehler" aria-hidden="true">1 / {n}</span></div></div>
    <div class="spur">{items}</div>
    <div class="wrap"><div class="balken"><i></i></div></div>
  </div>
</section>""".format(t=E(titel), n=len(figs), items=items)


def stimme(b, kurz=False):
    text = b["text"]
    if b.get("sprache") == "ru":
        inhalt = '<p lang="ru">„{}“</p><p class="uebersetzung">Übersetzt: „{}“</p>'.format(E(text), E(b["uebersetzung_de_sinngemaess"]))
    else:
        inhalt = "<p>„{}“</p>".format(E(text))
    return '<blockquote class="stimme"><div>{}</div><cite>{}</cite></blockquote>'.format(inhalt, E(b["name"]))


def seitenkopf(titel, lead, brot, bild=None, alt="", base=""):
    bildhtml = ""
    if bild:
        bildhtml = '<div class="wrap"><div class="kopfbild" data-reveal>{}</div></div>'.format(pic(bild, alt, "(min-width: 1320px) 1240px, 100vw", eager=True, base=base))
    return """<section class="seitenkopf"><div class="wrap">
  <p class="brotkrumen"><a href="{b}">Start</a> / {br}</p>
  <h1 class="display" data-split>{t}</h1>
  <p class="lead" data-reveal>{l}</p>
</div></section>
{bild}""".format(b=base or "./", br=E(brot), t=E(titel), l=lead, bild=bildhtml)


def jsonld():
    data = {
        "@context": "https://schema.org", "@type": "TireShop",
        "name": FIRMENNAME, "description": "Felgen- und Reifenhandel in Rahden: Reifenservice, Felgen, RDKS, Klimaservice, Fahrzeugaufbereitung und Ersatzteile.",
        "url": DOMAIN + "/", "telephone": TEL_INT, "email": MAIL,
        "image": DOMAIN + "/" + gross("werkstatt"), "logo": DOMAIN + "/assets/logo/logo-schwarz.png",
        "address": {"@type": "PostalAddress", "streetAddress": STRASSE, "postalCode": PLZ, "addressLocality": ORT, "addressRegion": "NRW", "addressCountry": "DE"},
        "founder": {"@type": "Person", "name": INHABER},
        "sameAs": [u for _, u in SOZIAL],
        "currenciesAccepted": "EUR",
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


SITEMAP = []


def band(base):
    return """<section class="band"><div class="wrap band-grid">
  <div><h2 class="h2" data-split>Termin nach Vereinbarung</h2><p class="lead leise" data-reveal>Rufen Sie an oder schreiben Sie uns. Wir finden einen Termin, auch samstags.</p></div>
  <div class="band-rechts" data-reveal>
    <a class="tel-gross" href="{tl}">{ta}</a>
    <div class="btn-row"><a class="btn btn-lack" href="{b}kontakt/#anfrage">Anfrage schreiben {p}</a><a class="btn btn-line" href="{r}" target="_blank" rel="noopener">Route planen</a></div>
  </div>
</div></section>""".format(tl=TEL_LINK, ta=TEL_ANZEIGE, b=base, p=I_PFEIL, r=MAPS_ROUTE)


def page(path, title, desc, body, aktiv=None, mit_band=True, og=None, start=False):
    depth = path.count("/")
    base = "/" if path == "404.html" else "../" * depth
    nav_desk = "".join('<a href="{}{}"{}>{}</a>'.format(base, h, ' aria-current="page"' if h == aktiv else "", l) for h, l in NAV_DESK)
    nav_alle = "".join('<a href="{}{}"{}>{}</a>'.format(base or ("./" if not h else ""), h, ' aria-current="page"' if h == (aktiv if aktiv is not None else "") and (aktiv is not None) else "", l) for h, l in NAV_ALLE)
    url_pfad = "" if path == "index.html" else path.replace("index.html", "")
    canonical = DOMAIN + "/" + url_pfad
    og_img = DOMAIN + "/assets/img/og-wiba.jpg"
    leist_links = "".join('<li><a href="{}{}">{}</a></li>'.format(base, h, l) for h, l in NAV_ALLE[1:6])
    sozial = "".join('<a href="{}" target="_blank" rel="noopener" aria-label="{} von WIBA Performance">{}</a>'.format(u, n, I_SOZIAL[n]) for n, u in SOZIAL)
    hat_galerie = 'class="galerie' in body
    hat_zettel = 'class="drucker"' in body
    preload = ""
    if start:
        v = IMG["felgen-hero"]
        preload = '<link rel="preload" as="image" imagesrcset="{}" imagesizes="100vw" fetchpriority="high">\n'.format(
            ", ".join("{}assets/img/{} {}w".format(base, fn, w) for fn, w, h in v))
    doc = """<!doctype html>
<html lang="de" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="WIBA Performance">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F4F4F1">
<link rel="icon" href="{base}favicon.ico" sizes="32x32">
<link rel="icon" href="{base}assets/logo/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="{base}assets/logo/apple-touch-icon.png">
<link rel="preload" href="{base}assets/fonts/hanken-grotesk-latin-var.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="{base}assets/css/style.css">
{jsonld}
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{home}"><img src="{base}assets/logo/logo-schwarz.png" width="720" height="68" alt="WIBA Performance, zur Startseite"></a>
    <nav class="nav-desk" aria-label="Hauptmenü">{nav_desk}</nav>
    <a class="btn btn-tinte kopf-tel" href="{tel_link}">{i_tel}{tel}</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="vorhang"><span>Menü</span><i></i></button>
  </div>
</header>
<div class="vorhang" id="vorhang">
  <nav aria-label="Alle Seiten">{nav_alle}</nav>
  <div class="vorhang-fuss"><a href="{tel_link}">{tel}</a><a href="mailto:{mail}">{mail}</a><span>{strasse}, {plz} {ort}</span></div>
</div>
<main id="inhalt" tabindex="-1">
{body}
</main>
{band}
<footer class="site-footer">
  <div class="wrap">
    <div class="fuss-grid">
      <div>
        <img src="{base}assets/logo/logo-weiss.png" width="720" height="68" alt="WIBA Performance" loading="lazy">
        <p>Felgen- und Reifenhandel in Rahden. Reifenservice, Felgen, Klimaservice, Fahrzeugaufbereitung und Ersatzteile aus einer Hand.</p>
        <div class="sozial">{sozial}</div>
      </div>
      <div>
        <h2>Kontakt</h2>
        <ul><li>{firma}</li><li>{inhaber}</li><li>{strasse}</li><li>{plz} {ort}</li>
        <li style="margin-top:8px"><a href="{tel_link}">{tel}</a></li><li><a href="mailto:{mail}">{mail}</a></li></ul>
      </div>
      <div>
        <h2>Leistungen</h2>
        <ul>{leist_links}</ul>
      </div>
      <div>
        <h2>Öffnungszeiten</h2>
        <ul><li>Mo – Fr: nach Vereinbarung</li><li>Sa: nach Vereinbarung</li><li>So: geschlossen</li></ul>
        <h2 style="margin-top:22px">Mehr</h2>
        <ul><li><a href="{base}kunden/">Kunden &amp; Bewertungen</a></li><li><a href="{base}ueber-uns/">Über uns</a></li></ul>
      </div>
    </div>
    <div class="fuss-unten">
      <span>© {jahr} WIBA Performance</span>
      <nav aria-label="Rechtliches"><a href="{base}impressum/">Impressum</a><a href="{base}datenschutz/">Datenschutz</a><a href="{base}agb/">AGB</a><button type="button" data-cookie-settings>Cookie-Einstellungen</button></nav>
    </div>
  </div>
</footer>

<nav class="kontaktleiste" aria-label="Schnellkontakt">
  <a class="anrufen" href="{tel_link}">{i_tel}Anrufen</a>
  <a class="anfrage" href="{base}kontakt/#anfrage">{i_mail}Anfrage</a>
  <button class="leiste-hoch" type="button" data-nach-oben aria-label="Nach oben">{i_hoch}</button>
</nav>
<div class="fab" id="fab">
  <div class="fab-menu" id="fab-menu">
    <a href="{route}" target="_blank" rel="noopener">Route planen</a>
    <a href="{base}kontakt/#anfrage">Anfrage schreiben</a>
    <a href="{tel_link}">{tel} anrufen</a>
  </div>
  <button class="fab-toggle" type="button" aria-expanded="false" aria-controls="fab-menu">{i_tel}Kontakt</button>
</div>
<button class="to-top" id="toTop" type="button" aria-label="Nach oben">{i_hoch}</button>
<div class="cookie" id="cookie" role="dialog" aria-labelledby="cookie-titel" aria-describedby="cookie-text">
  <h2 id="cookie-titel">Ihre Privatsphäre</h2>
  <p id="cookie-text">Wir verwenden nur, was die Seite zum Funktionieren braucht. Google Maps laden wir erst, wenn Sie zustimmen. <a href="{base}datenschutz/">Mehr dazu</a></p>
  <div class="row"><button type="button" data-consent="notwendig">Ablehnen</button><button type="button" data-consent="alle">Zustimmen</button></div>
</div>
{lightbox}{preisdaten}<div class="cursor" aria-hidden="true"></div>
<script src="{base}assets/js/main.js" defer></script>
</body>
</html>
""".format(title=E(title), desc=E(desc), canonical=canonical, og_img=og_img, base=base, preload=preload,
           jsonld=jsonld() if path == "index.html" or path == "kontakt/index.html" else "",
           home=base or "./", nav_desk=nav_desk, nav_alle=nav_alle, tel_link=TEL_LINK, tel=TEL_ANZEIGE, i_tel=I_TEL, i_mail=I_MAIL,
           mail=MAIL, strasse=STRASSE, plz=PLZ, ort=ORT, body=body, band=band(base) if mit_band else "", sozial=sozial,
           firma=FIRMENNAME, inhaber=INHABER, leist_links=leist_links, jahr=HEUTE.year, route=MAPS_ROUTE, i_hoch=I_HOCH,
           lightbox=('<dialog class="lightbox" id="lightbox" aria-label="Bildansicht"><div class="lb-oben"><span class="lb-zahl"></span>'
                     '<button class="rund lb-zu" type="button" aria-label="Schließen">' + I_ZU + '</button></div><div class="lb-bild"><img alt=""></div>'
                     '<div class="lb-unten"><button class="rund lb-zurueck" type="button" aria-label="Vorheriges Bild">' + I_LINKS + '</button>'
                     '<button class="rund lb-weiter" type="button" aria-label="Nächstes Bild">' + I_RECHTS + '</button></div></dialog>\n') if hat_galerie else "",
           preisdaten=('<script type="application/json" id="preisdaten">' + json.dumps(zettel_daten(), ensure_ascii=False) + "</script>\n") if hat_zettel else "")
    dest = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w", encoding="utf-8").write(doc)
    if path != "404.html":
        SITEMAP.append(canonical)


def p_gruppe(titel, klein, zeilen, zaehlen=True):
    rows = []
    for name, wert in zeilen:
        ab = wert.strip().startswith("ab")
        zahl = float(wert.replace("ab", "").replace("€", "").replace(",", ".").strip())
        anzeige = ("ab " if ab else "") + preis(zahl)
        attr = ' data-count="{}"{}'.format(zahl, ' data-prefix="ab "' if ab else "") if zaehlen else ""
        rows.append('<div class="p-zeile"><span>{}</span><b{}>{}</b></div>'.format(E(name), attr, anzeige))
    return '<div class="preisgruppe" data-reveal><h3>{}</h3>{}{}</div>'.format(E(titel), "<small>{}</small>".format(E(klein)) if klein else "", "".join(rows))


# ---------------------------------------------------------------- Seiten
def build_index():
    b = ""
    v = IMG["felgen-hero"]
    srcset = ", ".join("assets/img/{} {}w".format(fn, w) for fn, w, h in v)
    stimmen = "".join(stimme(x) for x in BEW["bewertungen"] if x["name"] in ("D. Lewen", "Viktor Reiswich", "Manfred Bodemann", "Peter.D", "Christina Kohlwes"))
    leistungen = [
        ("reifenservice/", "Reifenservice", "Montage, Radwechsel, Auswuchten und RDKS. Reifen fast aller Hersteller, auf Wunsch bestellt.", "montage"),
        ("felgenservice/", "Felgenservice", "Verkauf und Ankauf. Hilfe bei Eintragung, Gutachten und RDKS-Sensoren.", "felgen-08"),
        ("klimaservice/", "Klimaservice", "Befüllen, Desinfektion und Druckprüfung zum Festpreis.", "klima"),
        ("fahrzeugaufbereitung/", "Aufbereitung", "Innen und außen. Für Glanz, Werterhalt und eine längere Lebensdauer.", "polieren"),
        ("ersatzteile-zubehoer/", "Ersatzteile", "Autoteile aus unserem Herstellersortiment, spezielle Wünsche inklusive.", "teile"),
    ]
    liste = "".join('<li data-reveal><a href="{}"><div><h3>{}</h3><p>{}</p></div><div class="thumb">{}</div></a></li>'.format(
        h, E(t), E(p), pic(k, "", "150px")) for h, t, p, k in leistungen)
    spalten = [["kunde-20", "kunde-13", "kunde-05"], ["kunde-09", "kunde-21", "kunde-02"], ["kunde-17", "kunde-12", "kunde-16"], ["kunde-22", "kunde-03", "kunde-07"]]
    speeds = ["-.08", ".1", "-.04", ".06"]
    mosaik = "".join('<div class="sp" data-speed="{}">{}</div>'.format(speeds[i], "".join(pic(k, "Fahrzeug eines Kunden", "(min-width: 900px) 25vw, 33vw") for k in sp)) for i, sp in enumerate(spalten))
    body = """
<section class="zoom" aria-labelledby="claim-titel">
  <div class="zoom-buehne">
    <div class="zoom-rahmen"><img class="zoom-bild" src="assets/img/{img_s}" srcset="{srcset}" sizes="100vw" width="{w}" height="{h}" alt="Mehrspeichen-Alufelgen mit Reifen bei WIBA Performance" fetchpriority="high" decoding="async"></div>
    <div class="zoom-schleier"></div>
    <svg class="zoom-maske" aria-hidden="true" focusable="false">
      <defs><mask id="wiba-maske" maskUnits="userSpaceOnUse"><rect x="0" y="0" width="100%" height="100%" fill="#fff"/><text class="maske-text" text-anchor="middle">WIBA</text></mask></defs>
      <rect class="flaeche" x="0" y="0" width="100%" height="100%" mask="url(#wiba-maske)"/>
    </svg>
    <div class="zoom-vorn" aria-hidden="true"><div class="zoom-zeile"><span>Felgen- und Reifenhandel<br>in Rahden</span><span>{strasse}<br>{plz} {ort}</span></div><div class="zoom-hinweis"></div></div>
    <div class="zoom-claim">
      <h1 class="display" id="claim-titel">Die passende Felge. Der passende Reifen.</h1>
      <div class="btn-row"><a class="btn btn-weiss" href="#auftrag">Preis ansehen {pfeil}</a><a class="btn btn-line" href="{tel_link}">{i_tel}Anrufen</a></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="fuell-grid">
      <div><p class="fuell">WIBA Performance steht für die beste Auswahl an Felgen, Reifen und Kfz-Teilen. Wir arbeiten eng mit Ihnen zusammen und finden die passenden Teile zum passenden Preis. Sie kaufen nur, was Sie wirklich brauchen.</p>
      <div class="fuell-fuss" data-reveal><span>Inhaber {inhaber}, {ort}</span><a class="textlink" href="ueber-uns/">Über uns</a></div></div>
      <figure class="fuell-bild" data-reveal>{werkstatt}</figure>
    </div>
  </div>
</section>

<section class="section weiss" id="auftrag">
  <div class="wrap auftrag-grid">
    <div class="auftrag-text">
      <h2 class="h2" data-split>Ihr Preis, sofort.</h2>
      <p class="lead leise" data-reveal>Für Reifen- und Klimaservice gelten feste Preise. Wählen Sie die Leistung, und der Zettel zeigt den Preis. Die Anfrage schreibt er gleich mit.</p>
      <ul data-reveal><li><b>1</b>Leistung wählen</li><li><b>2</b>Größe oder Umfang antippen</li><li><b>3</b>Anfrage senden oder anrufen</li></ul>
      <a class="textlink" href="reifenservice/#preise" data-reveal>Alle Preise im Überblick</a>
    </div>
    {zettel}
  </div>
</section>

<section class="section" id="leistungen">
  <div class="wrap">
    <div class="kopfzeile"><h2 class="h2" data-split>Leistungen</h2><p class="lead leise" data-reveal>Fünf Bereiche, ein Ansprechpartner in Rahden.</p></div>
    <ul class="liste">{liste}</ul>
  </div>
</section>

{quer}

<section class="section" id="aufbereitung">
  <div class="wrap vn-grid">
    <div>
      <h2 class="h2" data-split>Vorher. Nachher.</h2>
      <p class="lead leise" data-reveal>Durch die Aufbereitung erstrahlt Ihr Fahrzeug wieder und behält seinen Wert. Ziehen Sie den Regler: echte Arbeiten aus unserer Werkstatt.</p>
      <p data-reveal style="margin-top:24px"><a class="btn btn-line" href="fahrzeugaufbereitung/">Zur Fahrzeugaufbereitung {pfeil}</a></p>
    </div>
    {vn}
  </div>
</section>

<section class="section" id="kunden" style="padding-top:0">
  <div class="wrap">
    <div class="kopfzeile"><h2 class="h2" data-split>Kunden und Stimmen</h2><a class="textlink" href="kunden/" data-reveal>Alle Bewertungen und Fotos</a></div>
    <div class="mosaik" aria-hidden="true">{mosaik}</div>
    <div class="stimmen">{stimmen}</div>
    <div class="wisch"><button class="rund" type="button" data-dir="-1" aria-label="Vorherige Bewertung">{links}</button><button class="rund" type="button" data-dir="1" aria-label="Nächste Bewertung">{rechts}</button></div>
  </div>
</section>
""".format(img_s=v[0][0], srcset=srcset, w=v[0][1], h=v[0][2], strasse=STRASSE, plz=PLZ, ort=ORT, pfeil=I_PFEIL, tel_link=TEL_LINK, i_tel=I_TEL,
           inhaber=INHABER, werkstatt=pic("polieren", "Mitarbeiter von WIBA Performance poliert ein Auto vor dem Wandlogo", "(min-width: 1000px) 34vw, 100vw"), zettel=zettel("Reifenmontage"), liste=liste, quer=quer_galerie(""), vn=vn_modul(""), mosaik=mosaik, stimmen=stimmen,
           links=I_LINKS, rechts=I_RECHTS)
    page("index.html", "WIBA Performance – Felgen, Reifen und Kfz-Service in Rahden",
         "Felgen- und Reifenhandel in Rahden: Reifenmontage ab 12,50 €, Felgen mit Eintragung und RDKS, Klimaservice, Fahrzeugaufbereitung und Ersatzteile. Termine nach Vereinbarung.",
         body, aktiv="", start=True, og=gross("felgen-hero"))


def build_reifenservice():
    base = "../"
    r = LEIST["reifenservice"]
    gruppen = "".join(p_gruppe(g["titel"], g["beschreibung"], g["positionen"]) for g in r["preise"])
    bilder = [("montage", "Reifen wird auf der Montiermaschine auf eine Alufelge gezogen"), ("radwechsel", "Radschrauben werden beim Radwechsel angezogen"),
              ("auswuchten", "Komplettrad auf der Auswuchtmaschine"), ("altreifen", "Gestapelte Altreifen zur Entsorgung")]
    body = seitenkopf("Reifenservice", "Wir bieten Ihnen eine große Auswahl passender Reifen. Mit uns fahren Sie gut und vor allem sicher.",
                      "Reifenservice", "reifenlager", "Reifenlager und Montiermaschine in der Werkstatt von WIBA Performance", base) + """
<section class="section"><div class="wrap zwei">
  <div class="text-block" data-reveal><h2 class="h3">Reifen fast aller Hersteller</h2>
    <p>Wir führen Reifen fast aller Hersteller. Natürlich bestellen wir auch gerne das gewünschte Modell für Sie, falls wir etwas nicht auf Lager haben sollten.</p>
    <p>Kommen Sie zu uns und lassen Sie sich beraten. Wir kennen die Neuigkeiten, sowohl bei den Produkten als auch bei den gesetzlichen Bestimmungen.</p></div>
  <div data-reveal>{g}</div>
</div></section>
<section class="section dunkel" id="preise"><div class="wrap">
  <div class="kopfzeile"><h2 class="h2" data-split>Preise</h2><p class="lead leise" data-reveal>Feste Preise inklusive MwSt.</p></div>
  <div class="preisgruppen">{gr}</div>
</div></section>
<section class="section weiss"><div class="wrap auftrag-grid">
  <div class="auftrag-text"><h2 class="h2" data-split>Anfrage mit Festpreis</h2><p class="lead leise" data-reveal>Leistung und Felgengröße wählen, Anfrage senden. Wir melden uns mit einem Terminvorschlag.</p></div>
  {z}
</div></section>""".format(g=galerie(bilder, base), gr=gruppen, z=zettel("Reifenmontage"))
    page("reifenservice/index.html", "Reifenservice in Rahden: Montage, Radwechsel, Auswuchten | WIBA Performance",
         "Reifenmontage ab 12,50 €, Radwechsel ab 25 €, Auswuchten, RDKS-Sensoren und Altreifenentsorgung zu festen Preisen. WIBA Performance in Rahden.",
         body, aktiv="reifenservice/", og=gross("reifenlager"))


def build_felgenservice():
    base = "../"
    f = LEIST["felgenservice"]
    verkauf = f["felgenverkauf"].replace("RDSK - Sensoren", "RDKS-Sensoren").replace("RDKS-Sensoren oder", "RDKS-Sensoren oder")
    gal = [("felgen-{:02d}".format(i), "Kompletträder mit Alufelgen bei WIBA Performance") for i in range(1, 10)]
    body = seitenkopf("Felgenservice", "Ob eine Felge an Ihr Fahrzeug passt, hängt von vielen Faktoren ab. Wir helfen Ihnen dabei, von der Auswahl bis zur Eintragung.",
                      "Felgenservice", "felgen-08", "Alufelgen in Anthrazit mit Reifen", base) + """
<section class="section"><div class="wrap zwei">
  <div class="text-block" data-reveal><h2 class="h3">Felgenverkauf</h2><p>{v}</p></div>
  <div class="text-block" data-reveal><h2 class="h3">Felgenankauf</h2><p>Wir sind stets auf der Suche nach authentischen und hochwertigen Alufelgen und Kompletträdern. Wenn Sie einen solchen Radsatz verkaufen möchten, schreiben Sie uns. Wir machen Ihnen ein faires Angebot, das Ihren Erwartungen entspricht.</p>
    <p><a class="btn btn-lack" href="../kontakt/?thema=Felgenankauf#anfrage">Radsatz anbieten {p}</a></p></div>
</div></section>
{q}
<section class="section"><div class="wrap">
  <div class="kopfzeile"><h2 class="h2" data-split>Aus der Werkstatt</h2><p class="lead leise" data-reveal>Kompletträder, die bei uns montiert wurden. Tippen zum Vergrößern.</p></div>
  <div data-reveal>{gal}</div>
</div></section>
<section class="section weiss"><div class="wrap zwei" style="align-items:center">
  <div class="text-block" data-reveal><h2 class="h3">Felgen und RDKS im Video</h2><p>Ein kurzer Einblick: Felgen, Reifen und RDKS-Sensoren bei WIBA Performance in Rahden.</p></div>
  <div class="video" data-reveal><video preload="none" playsinline poster="{b}assets/img/{poster}"><source src="{b}assets/video/felgen-rdks.mp4" type="video/mp4">Ihr Browser kann dieses Video nicht abspielen.</video><button class="video-play" type="button" aria-label="Video abspielen"><svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg></button></div>
</div></section>""".format(v=E(verkauf), p=I_PFEIL, q=quer_galerie(base, "Bei uns erhältlich", mit_felgen=False), gal=galerie(gal, base),
                           b=base, poster=IMG["video-poster"][0][0])
    page("felgenservice/index.html", "Felgenservice: Alufelgen kaufen und verkaufen, Eintragung, RDKS | WIBA Performance",
         "Alufelgen und Kompletträder in Rahden: Beratung, Eintragung, Gutachten, RDKS-Sensoren und fairer Felgenankauf bei WIBA Performance.",
         body, aktiv="felgenservice/", og=gross("felgen-08"))


def build_klimaservice():
    base = "../"
    k = LEIST["klimaservice"]
    body = seitenkopf("Klimaservice", "Die Klimaanlage kühlt nicht richtig? Wir regeln das.", "Klimaservice", "klima", "Klimaservice-Gerät an einem Auto mit geöffneter Motorhaube", base) + """
<section class="section"><div class="wrap zwei">
  <div class="text-block" data-reveal><h2 class="h3">Frische Luft, Sommer wie Winter</h2>
    <p>Eine Klimaanlage ist nicht wartungsfrei. Sie verliert pro Jahr bis zu 15 % Kältemittel, das ausgeglichen werden muss, damit sie voll funktioniert. Eine Desinfektion schützt vor Bakterien und Schimmel.</p></div>
  <div data-reveal>{g}</div>
</div></section>
<section class="section weiss"><div class="wrap auftrag-grid">
  <div class="auftrag-text"><h2 class="h2" data-split>Klimaservice anfragen</h2><p class="lead leise" data-reveal>Umfang wählen, Anfrage senden. Kältemittel R134a.</p></div>
  {z}
</div></section>""".format(g=p_gruppe("Preise", "Kältemittel R134a, inklusive MwSt.", [("Klimaanlage befüllen", k["preise"][0][1]), ("Befüllen und desinfizieren", k["preise"][1][1]), ("Druckprüfung", k["preise"][2][1])]),
                           z=zettel("Klimaservice"))
    page("klimaservice/index.html", "Klimaservice in Rahden: Klimaanlage befüllen ab 120 € | WIBA Performance",
         "Klimaanlage befüllen (R134a) 120 €, mit Desinfektion 150 €, Druckprüfung ab 40 €. Klimaservice bei WIBA Performance in Rahden.",
         body, aktiv="klimaservice/", og=gross("klima"))


def build_aufbereitung():
    base = "../"
    gal = [("aufb-" + n, "Fahrzeugaufbereitung bei WIBA Performance") for n in AUFB_GALERIE]
    body = seitenkopf("Fahrzeug\u00adaufbereitung", "Durch die Aufbereitung erstrahlt Ihr Fahrzeug wieder in voller Schönheit und behält seinen Wert, oft steigert sie ihn sogar.",
                      "Fahrzeugaufbereitung", "polieren", "Mitarbeiter von WIBA Performance poliert ein Fahrzeug vor dem Wandlogo", base) + """
<section class="section"><div class="wrap vn-grid">
  <div class="text-block"><h2 class="h2" data-split>Vorher. Nachher.</h2>
    <p data-reveal>Regelmäßige Pflege verhindert Rostschäden und sorgt dafür, dass Dichtungen und andere Verschleißteile länger halten. Ein gepflegtes Fahrzeug sieht nicht nur besser aus, es hat auch eine deutlich höhere Lebensdauer.</p>
    <p data-reveal>Ziehen Sie den Regler, um echte Arbeiten aus unserer Werkstatt zu vergleichen.</p></div>
  {vn}
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="kopfzeile"><h2 class="h2" data-split>Galerie</h2><p class="lead leise" data-reveal>Innenraum, Lack und Motorraum. Tippen zum Vergrößern.</p></div>
  <div data-reveal>{gal}</div>
</div></section>
<section class="section weiss"><div class="wrap auftrag-grid">
  <div class="auftrag-text"><h2 class="h2" data-split>Aufbereitung anfragen</h2><p class="lead leise" data-reveal>Der Preis richtet sich nach Fahrzeug und Zustand. Wählen Sie den Umfang, wir melden uns mit einem Angebot.</p></div>
  {z}
</div></section>""".format(vn=vn_modul(base), gal=galerie(gal, base, vier=True), z=zettel("Aufbereitung"))
    page("fahrzeugaufbereitung/index.html", "Fahrzeugaufbereitung in Rahden: innen und außen | WIBA Performance",
         "Fahrzeugaufbereitung bei WIBA Performance in Rahden: Innenraumreinigung, Polieren und Pflege für Glanz und Werterhalt. Vorher-Nachher-Beispiele.",
         body, aktiv="fahrzeugaufbereitung/", og=gross("polieren"))


def build_ersatzteile():
    base = "../"
    e = LEIST["ersatzteile_zubehoer"]
    body = seitenkopf("Ersatzteile & Zubehör", "Wir verkaufen Autoteile in hoher Qualität. Wir helfen Ihnen gerne bei der Auswahl aus unserem Herstellersortiment.",
                      "Ersatzteile & Zubehör", "teile", "Felgen, Reifen und Ersatzteile verschiedener Hersteller", base) + """
<section class="section"><div class="wrap zwei">
  <div class="text-block" data-reveal><h2 class="h3">Für jeden das passende Teil</h2>
    <p>Kompetente Beratung bei der Produktauswahl, für Alltag und Tuning. Spezielle Wünsche nehmen wir gerne entgegen.</p>
    <p><a class="btn btn-lack" href="../kontakt/?thema=Ersatzteile#anfrage">Teil anfragen {p}</a></p></div>
  <div class="produkt" data-reveal>{img}<div><h2 class="h3">BMW Nabenkappen</h2><span class="preis">20,00 €</span><a class="textlink" href="mailto:{m}?subject=Anfrage%3A%20BMW%20Nabenkappen">Verfügbarkeit anfragen</a></div></div>
</div></section>
{q}""".format(p=I_PFEIL, img=pic("nabenkappen", "BMW Nabenkappen", "(min-width: 900px) 40vw, 100vw", base=base), m=MAIL, q=quer_galerie(base, "Zubehör im Sortiment", mit_felgen=False))
    page("ersatzteile-zubehoer/index.html", "Ersatzteile und Zubehör | WIBA Performance Rahden",
         "Kfz-Ersatzteile und Zubehör aus dem Herstellersortiment von WIBA Performance in Rahden. Beratung und Bestellung auf Wunsch.",
         body, aktiv="ersatzteile-zubehoer/", og=gross("teile"))


def build_kunden():
    base = "../"
    alle = "".join(stimme(b) for b in BEW["bewertungen"])
    gal = [("kunde-{:02d}".format(i), "Fahrzeug eines Kunden von WIBA Performance") for i in range(1, 23)]
    body = seitenkopf("Kunden und Bewertungen", "Was unsere Kunden über Beratung, Preise und Arbeit sagen, und welche Fahrzeuge bei uns waren.", "Kunden & Bewertungen", base=base) + """
<section class="section" style="padding-top:20px"><div class="wrap">
  <div class="bewertungen" data-reveal>{alle}</div>
  <div class="band-grid" style="margin-top:56px" data-reveal>
    <div><h2 class="h3">Waren Sie zufrieden?</h2><p class="leise" style="margin-top:10px">Kundenzufriedenheit ist uns sehr wichtig. Wir freuen uns, wenn Sie sich kurz Zeit für eine Bewertung bei Google nehmen.</p></div>
    <div><a class="btn btn-lack" href="{g}" target="_blank" rel="noopener">Bei Google bewerten {p}</a></div>
  </div>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="kopfzeile"><h2 class="h2" data-split>Kundenautos</h2><p class="lead leise" data-reveal>Tippen zum Vergrößern.</p></div>
  <div data-reveal>{gal}</div>
</div></section>""".format(alle=alle, g=GOOGLE_BEWERTUNG, p=I_PFEIL, gal=galerie(gal, base, vier=True))
    page("kunden/index.html", "Kunden und Bewertungen | WIBA Performance Rahden",
         "Bewertungen von Kunden über Beratung, Preise und Arbeit von WIBA Performance in Rahden, dazu Fotos von Kundenfahrzeugen.",
         body, aktiv="kunden/", og=gross("kunde-20"))


def build_ueber_uns():
    base = "../"
    body = seitenkopf("Über uns", "Wir haben WIBA Performance gegründet, um Auto-Liebhabern einen Ort zu bieten, an dem sie alles finden, was ihr Herz begehrt.",
                      "Über uns", "werkstatt", "Werkstatt von WIBA Performance mit Wandlogo und Reifensätzen", base) + """
<section class="section"><div class="wrap zwei">
  <div class="text-block" data-reveal>
    <h2 class="h3">Aus Leidenschaft fürs Auto</h2>
    <p>Unser Ziel ist es, Kreativität und Unternehmergeist zu fördern und als Felgen- und Reifenhändler aus der Masse herauszuragen.</p>
    <p>Unser Team besteht aus Automobil-Liebhabern mit vielen Jahren Erfahrung. Wir informieren Sie ehrlich über unsere Produkte, damit Sie nur kaufen, was Sie wirklich brauchen.</p>
    <p><a class="btn btn-lack" href="../kontakt/">Kontakt aufnehmen {p}</a></p>
  </div>
  <div class="video" data-reveal><video preload="none" playsinline poster="{b}assets/img/{poster}"><source src="{b}assets/video/felgen-rdks.mp4" type="video/mp4">Ihr Browser kann dieses Video nicht abspielen.</video><button class="video-play" type="button" aria-label="Video abspielen"><svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg></button></div>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="fakten" data-reveal>
    <div><b>{inh}</b><span>Inhaber</span></div>
    <div><b>{ort}</b><span>{str}, {plz}</span></div>
    <div><b>Nach Vereinbarung</b><span>Termine Mo – Sa</span></div>
    <div><b>5 Bereiche</b><span>Reifen, Felgen, Klima, Aufbereitung, Teile</span></div>
  </div>
</div></section>""".format(p=I_PFEIL, b=base, poster=IMG["video-poster"][0][0], inh=INHABER, ort=ORT, str=STRASSE, plz=PLZ)
    page("ueber-uns/index.html", "Über uns | WIBA Performance Rahden",
         "WIBA Performance in Rahden: Felgen- und Reifenhandel von Auto-Liebhabern mit vielen Jahren Erfahrung. Inhaber Witali Bakin.",
         body, aktiv="ueber-uns/", og=gross("werkstatt"))


def build_kontakt():
    base = "../"
    themen = ["Reifenservice", "Felgenservice", "Felgenankauf", "Klimaservice", "Fahrzeugaufbereitung", "Ersatzteile", "Sonstiges"]
    opts = "".join("<option>{}</option>".format(t) for t in themen)
    sozial = "".join('<a href="{}" target="_blank" rel="noopener" aria-label="{} von WIBA Performance">{}</a>'.format(u, n, I_SOZIAL[n]) for n, u in SOZIAL)
    body = seitenkopf("Kontakt", "Suchen Sie nicht weiter: Kommen Sie vorbei und lassen Sie sich von unserer großen Auswahl und unseren Preisen überzeugen.", "Kontakt", base=base) + """
<section class="section" style="padding-top:10px"><div class="wrap kontakt-grid">
  <div class="kontakt-daten" data-reveal>
    <p class="leise" style="margin:0">Telefon, mobil</p>
    <a class="tel-gross" href="{tl}">{ta}</a><br>
    <a class="textlink" href="mailto:{m}">{m}</a>
    <address>{firma}<br>Inhaber {inh}<br>{str}<br>{plz} {ort}</address>
    <dl class="zeiten"><dt>Mo – Fr</dt><dd>nach Vereinbarung</dd><dt>Sa</dt><dd>nach Vereinbarung</dd><dt>So</dt><dd>geschlossen</dd></dl>
    <div class="btn-row" style="margin-top:28px"><a class="btn btn-line" href="{route}" target="_blank" rel="noopener">Route planen</a></div>
    <div class="sozial" style="margin-top:24px">{sozial}</div>
  </div>
  <div id="anfrage" data-reveal>
    <h2 class="h3" style="margin-bottom:20px">Anfrage schreiben</h2>
    <form class="formular" id="anfrage-form" data-to="{m}" novalidate>
      <div class="feld-reihe">
        <div class="feld"><label for="f-name">Name *</label><input id="f-name" name="name" autocomplete="name" required></div>
        <div class="feld"><label for="f-tel">Telefon</label><input id="f-tel" name="telefon" type="tel" autocomplete="tel"></div>
      </div>
      <div class="feld-reihe">
        <div class="feld"><label for="f-mail">E-Mail</label><input id="f-mail" name="email" type="email" autocomplete="email"></div>
        <div class="feld"><label for="f-thema">Anliegen *</label><select id="f-thema" name="thema" required>{opts}</select></div>
      </div>
      <div class="feld"><label for="f-fz">Fahrzeug und Reifen- oder Felgengröße</label><input id="f-fz" name="fahrzeug" placeholder="z. B. BMW 3er, 225/45 R18"></div>
      <div class="feld"><label for="f-text">Nachricht *</label><textarea id="f-text" name="nachricht" required></textarea></div>
      <p class="hinweis">Das Formular öffnet Ihr E-Mail-Programm mit der fertigen Nachricht. Es speichert keine Daten. Hinweise im <a href="../datenschutz/">Datenschutz</a>.</p>
      <button class="btn btn-lack" type="submit">Anfrage vorbereiten {p}</button>
      <p class="form-status" role="status"></p>
    </form>
  </div>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <h2 class="h3" style="margin-bottom:18px">Anfahrt</h2>
  <div class="karte" data-src="{embed}" data-reveal>
    <p>Die Karte wird von Google Maps geladen. Dabei werden Daten wie Ihre IP-Adresse an Google übertragen.</p>
    <button class="btn btn-tinte" type="button" data-karte-laden>Karte laden</button>
    <a class="textlink" href="{route}" target="_blank" rel="noopener">Oder Route direkt in Google Maps öffnen</a>
  </div>
</div></section>""".format(tl=TEL_LINK, ta=TEL_ANZEIGE, m=MAIL, firma=FIRMENNAME, inh=INHABER, str=STRASSE, plz=PLZ, ort=ORT, route=MAPS_ROUTE,
                           sozial=sozial, opts=opts, p=I_PFEIL, embed=MAPS_EMBED)
    page("kontakt/index.html", "Kontakt und Anfahrt | WIBA Performance Rahden",
         "WIBA Performance, Hackelbarg 7, 32369 Rahden. Telefon 0160 4151974, E-Mail info@wibaperformance.de. Termine nach Vereinbarung.",
         body, aktiv="kontakt/", mit_band=False, og=gross("werkstatt"))


def rechtsseite(path, titel, inhalt, desc):
    body = """<section class="seitenkopf"><div class="wrap"><p class="brotkrumen"><a href="../">Start</a> / {t}</p><h1 class="display" data-split>{t}</h1></div></section>
<section class="section" style="padding-top:0"><div class="wrap"><div class="prose">{i}</div></div></section>""".format(t=E(titel), i=inhalt)
    page(path, "{} | WIBA Performance".format(titel), desc, body, mit_band=False)


def build_impressum():
    inhalt = """
<!-- ENTWURF: Rechtsform, USt-IdNr. und ggf. Kammer/Register beim Inhaber erfragen und vor Veröffentlichung prüfen lassen. -->
<h2>Angaben gemäß § 5 DDG</h2>
<p>{firma}<br>Inhaber: {inh}<br>{str}<br>{plz} {ort}<br>Deutschland</p>
<h2>Kontakt</h2>
<p>Telefon: <a href="{tl}">{ti}</a><br>E-Mail: <a href="mailto:{m}">{m}</a></p>
<h2>Umsatzsteuer</h2>
<p>Umsatzsteuer-Identifikationsnummer gemäß § 27a Umsatzsteuergesetz: <span class="fehlt">wird vom Inhaber ergänzt</span></p>
<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>
<p>{inh}<br>{str}, {plz} {ort}</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Haftung für Inhalte und Links</h2>
<p>Wir erstellen die Inhalte dieser Seiten mit Sorgfalt. Für die Inhalte verlinkter externer Seiten sind ausschließlich deren Betreiber verantwortlich. Bei Bekanntwerden von Rechtsverletzungen entfernen wir entsprechende Inhalte oder Links umgehend.</p>
<h2>Bildnachweis</h2>
<p>Alle Fotos: {firma}.</p>""".format(firma=FIRMENNAME, inh=INHABER, str=STRASSE, plz=PLZ, ort=ORT, tl=TEL_LINK, ti=TEL_INT, m=MAIL)
    rechtsseite("impressum/index.html", "Impressum", inhalt, "Impressum von WIBA Performance, Inhaber Witali Bakin, Hackelbarg 7, 32369 Rahden.")


def build_datenschutz():
    inhalt = """
<!-- ENTWURF: Beschreibt die Technik dieser neuen Website. Vor Veröffentlichung rechtlich prüfen lassen
     und Hosting-Anbieter (inkl. Vertrag zur Auftragsverarbeitung) ergänzen. -->
<p class="lead">Hier erfahren Sie, welche personenbezogenen Daten beim Besuch dieser Website verarbeitet werden und welche Rechte Sie haben.</p>
<h2>1. Verantwortlicher</h2>
<p>{firma}, Inhaber {inh}<br>{str}, {plz} {ort}<br>Telefon: {ti}<br>E-Mail: <a href="mailto:{m}">{m}</a></p>
<h2>2. Hosting und Server-Logdateien</h2>
<p>Diese Website wird bei <span class="fehlt">Hosting-Anbieter wird ergänzt</span> betrieben. Beim Aufruf speichert der Server automatisch Informationen, die Ihr Browser übermittelt: IP-Adresse, Datum und Uhrzeit, aufgerufene Seite, Referrer-URL, Browsertyp und Betriebssystem. Das ist technisch nötig, um die Website auszuliefern und ihre Sicherheit zu gewährleisten (Art. 6 Abs. 1 lit. f DSGVO). Mit dem Anbieter besteht ein Vertrag zur Auftragsverarbeitung. Die Logdateien werden nach kurzer Zeit gelöscht, sofern sie nicht zur Aufklärung eines Sicherheitsvorfalls benötigt werden.</p>
<h2>3. Schriftarten und Videos</h2>
<p>Schriftarten und Videos liegen auf unserem eigenen Server. Beim Laden der Seite wird keine Verbindung zu Google oder anderen Drittanbietern aufgebaut.</p>
<h2>4. Cookies und lokale Speicherung</h2>
<p>Wir setzen keine Cookies zu Analyse- oder Werbezwecken ein und verwenden keine Tracking-Dienste. Ihre Auswahl im Hinweis zur Privatsphäre speichern wir im lokalen Speicher Ihres Browsers, damit er nicht bei jedem Aufruf erneut erscheint. Diese Speicherung ist für den von Ihnen gewünschten Dienst unbedingt erforderlich (§ 25 Abs. 2 TDDDG). Sie können Ihre Auswahl jederzeit über „Cookie-Einstellungen“ am Ende jeder Seite ändern.</p>
<h2>5. Google Maps</h2>
<p>Auf der Kontaktseite können Sie eine Karte von Google Maps anzeigen lassen. Anbieter ist die Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland. Die Karte wird erst geladen, wenn Sie zustimmen (Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG). Dabei wird unter anderem Ihre IP-Adresse an Google übertragen, möglicherweise auch in die USA. Google ist nach dem EU-US Data Privacy Framework zertifiziert. Ihre Einwilligung können Sie jederzeit über die Cookie-Einstellungen widerrufen. Weitere Informationen: <a href="https://policies.google.com/privacy" rel="noopener">Datenschutzerklärung von Google</a>.</p>
<h2>6. Kontakt per Telefon, E-Mail oder Formular</h2>
<p>Wenn Sie uns anrufen, eine E-Mail schreiben oder das Anfrageformular bzw. den Auftragszettel nutzen, verarbeiten wir Ihre Angaben, um Ihre Anfrage zu beantworten und gegebenenfalls einen Auftrag abzuwickeln (Art. 6 Abs. 1 lit. b DSGVO). Formular und Auftragszettel speichern selbst keine Daten, sondern öffnen Ihr E-Mail-Programm mit einer vorbereiteten Nachricht. Wir löschen Ihre Daten, wenn sie nicht mehr erforderlich sind und keine gesetzlichen Aufbewahrungspflichten bestehen.</p>
<h2>7. Links zu sozialen Netzwerken</h2>
<p>Auf Instagram, Facebook und TikTok verweisen wir nur mit einfachen Links. Erst wenn Sie einen Link anklicken, werden Sie zum jeweiligen Anbieter weitergeleitet, dessen Datenschutzbestimmungen dann gelten.</p>
<h2>8. Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) und Widerspruch (Art. 21). Eine erteilte Einwilligung können Sie jederzeit mit Wirkung für die Zukunft widerrufen. Anfragen richten Sie bitte an <a href="mailto:{m}">{m}</a>.</p>
<p>Sie können sich außerdem bei einer Datenschutz-Aufsichtsbehörde beschweren, zum Beispiel bei der Landesbeauftragten für Datenschutz und Informationsfreiheit Nordrhein-Westfalen.</p>
<p class="leise">Stand: {stand}</p>""".format(firma=FIRMENNAME, inh=INHABER, str=STRASSE, plz=PLZ, ort=ORT, ti=TEL_INT, m=MAIL, stand=HEUTE.strftime("%m/%Y"))
    rechtsseite("datenschutz/index.html", "Datenschutz", inhalt, "Datenschutzerklärung von WIBA Performance, Rahden.")


def build_agb():
    teile = ['<p class="leise">Allgemeine Geschäftsbedingungen von {}, {}.</p>'.format(FIRMENNAME, INHABER)]
    for a in AGB["abschnitte"]:
        teile.append("<h2>§ {} {}</h2>".format(a["nr"], E(a["titel"])))
        teile.extend("<p>{}</p>".format(E(x)) for x in a["absaetze"])
    rechtsseite("agb/index.html", "AGB", "".join(teile), "Allgemeine Geschäftsbedingungen von WIBA Performance, Rahden.")


def build_404():
    body = """<section class="seitenkopf nichtgefunden"><div class="wrap">
  <h1 class="display" data-split>Diese Seite gibt es nicht.</h1>
  <p class="lead leise" data-reveal>Vielleicht hat sich die Adresse mit der neuen Website geändert. Hier geht es weiter:</p>
  <div class="btn-row" data-reveal style="margin-top:28px"><a class="btn btn-lack" href="/">Zur Startseite</a><a class="btn btn-line" href="/reifenservice/">Reifenservice</a><a class="btn btn-line" href="/kontakt/">Kontakt</a></div>
</div></section>"""
    page("404.html", "Seite nicht gefunden | WIBA Performance", "Diese Seite gibt es nicht.", body, mit_band=False)


# ---------------------------------------------------------------- Logos, Favicon, Video, SEO, Server
def build_assets():
    d = os.path.join(OUT, "assets", "logo")
    os.makedirs(d, exist_ok=True)
    for src, ziel in (("logo-schwarz-transparent.png", "logo-schwarz.png"), ("logo-weiss-transparent.png", "logo-weiss.png")):
        im = Image.open(os.path.join(ROOT, "bilder", "logos", src)).convert("RGBA")
        im = im.resize((720, round(im.height * 720 / im.width)), Image.LANCZOS)
        im.save(os.path.join(d, ziel), optimize=True)
    # Icon: „W“ aus dem Logo, weiß auf Tinte
    logo = Image.open(os.path.join(ROOT, "bilder", "logos", "logo-weiss-transparent.png")).convert("RGBA")
    w = logo.crop((0, 0, 118, logo.height))
    w = w.crop(w.getbbox())

    def icon(size, pad, rund=True):
        c = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        if rund:
            ImageDraw.Draw(c).rounded_rectangle((0, 0, size - 1, size - 1), radius=size // 5, fill=(21, 24, 29, 255))
        else:
            c.paste((21, 24, 29, 255), (0, 0, size, size))
        s = w.copy()
        s.thumbnail((size - 2 * pad, size - 2 * pad), Image.LANCZOS)
        c.alpha_composite(s, ((size - s.width) // 2, (size - s.height) // 2))
        return c
    icon(180, 34, rund=False).convert("RGB").save(os.path.join(d, "apple-touch-icon.png"))
    icon(192, 34).save(os.path.join(d, "icon-192.png"))
    icon(512, 90).save(os.path.join(d, "icon-512.png"))
    icon(48, 7).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    v = os.path.join(OUT, "assets", "video")
    os.makedirs(v, exist_ok=True)
    shutil.copy(os.path.join(ROOT, "bilder", "video", "felgen-rdks-480p.mp4"), os.path.join(v, "felgen-rdks.mp4"))


WEITERLEITUNGEN = [
    ("^/produkte/?$", "/reifenservice/"), ("^/services/?$", "/felgenservice/"), ("^/dienstleistungen-1/?$", "/klimaservice/"),
    ("^/dienstleistungen-2/?$", "/fahrzeugaufbereitung/"), ("^/dienstleistungen-3/?$", "/ersatzteile-zubehoer/"),
    ("^/customer-name/?$", "/kunden/"), ("^/über-uns/?$", "/ueber-uns/"), ("^/%C3%BCber-uns/?$", "/ueber-uns/"),
    ("^/kontakt$", "/kontakt/"), ("^/agb$", "/agb/"), ("^/gewinnspiel-jetzt-mitmachen/?$", "/"),
]


def build_server_files():
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\nSitemap: {}/sitemap.xml\n".format(DOMAIN))
    urls = "".join("  <url><loc>{}</loc><lastmod>{}</lastmod></url>\n".format(u, HEUTE.isoformat()) for u in SITEMAP)
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{}</urlset>\n'.format(urls))
    open(os.path.join(OUT, "site.webmanifest"), "w").write(json.dumps({
        "name": "WIBA Performance", "short_name": "WIBA", "icons": [{"src": "/assets/logo/icon-192.png", "sizes": "192x192", "type": "image/png"},
                                                                    {"src": "/assets/logo/icon-512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#F4F4F1", "background_color": "#F4F4F1", "display": "browser"}, ensure_ascii=False, indent=2))
    redirects = "\n".join('RedirectMatch 301 "{}" "{}"'.format(a, b) for a, b in WEITERLEITUNGEN)
    htaccess = """# WIBA Performance – Apache-Konfiguration
DirectoryIndex index.html
ErrorDocument 404 /404.html
AddDefaultCharset UTF-8
Options -Indexes
AddType video/mp4 .mp4
AddType application/manifest+json .webmanifest

# HTTPS und www erzwingen
RewriteEngine On
RewriteCond %{{HTTPS}} off [OR]
RewriteCond %{{HTTP_HOST}} !^www\\. [NC]
RewriteRule ^ https://www.wibaperformance.de%{{REQUEST_URI}} [L,R=301]

# Alte Wix-Adressen dauerhaft auf die neuen Seiten weiterleiten (SEO)
{r}

# Sicherheit
<IfModule mod_headers.c>
  Header always set Strict-Transport-Security "max-age=31536000"
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
  Header set X-Frame-Options "SAMEORIGIN"
  Header set Permissions-Policy "camera=(), microphone=(), geolocation=()"
  Header set Content-Security-Policy "default-src 'self'; img-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; media-src 'self'; frame-src https://www.google.com https://maps.google.com; base-uri 'self'; form-action 'self'"
</IfModule>

# Caching
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/x-icon "access plus 1 year"
  ExpiresByType video/mp4 "access plus 1 year"
  ExpiresByType font/woff2 "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
  ExpiresByType text/html "access plus 0 seconds"
</IfModule>
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/json text/plain application/xml
</IfModule>
""".format(r=redirects)
    open(os.path.join(OUT, ".htaccess"), "w").write(htaccess)
    json.dump([{"alt": a, "neu": b} for a, b in WEITERLEITUNGEN], open(os.path.join(ROOT, "website-generator", "weiterleitungen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    for f in os.listdir(OUT) if os.path.isdir(OUT) else []:
        p = os.path.join(OUT, f)
        if f == "assets":
            continue
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    bilder_vorbereiten()
    build_assets()
    build_index()
    build_reifenservice()
    build_felgenservice()
    build_klimaservice()
    build_aufbereitung()
    build_ersatzteile()
    build_kunden()
    build_ueber_uns()
    build_kontakt()
    build_impressum()
    build_datenschutz()
    build_agb()
    build_404()
    build_server_files()
    n = sum(len(v) for v in IMG.values())
    print("{} Seiten in der Sitemap, {} Bilddateien erzeugt".format(len(SITEMAP), n))
