# Briefing: Website-Relaunch für wibaperformance.de

> **Für Claude Code:** Diese Datei ist dein vollständiger Auftrag. Lies sie ganz, dann leg los. Arbeite in Phasen, halte die Aufgabenliste aktuell und melde dich nach jeder Phase kurz auf Deutsch.
> **Vorbild:** Derselbe Prozess wurde schon für ein anderes Unternehmen durchgeführt. Das Ergebnis liegt in `/Users/lukabloemendal/Documents/emmerich/`. Schau dir dort Struktur und Code an und verwende ihn als Ausgangspunkt (siehe „Wiederverwendbarer Code“). **Übernimm keine Inhalte, Farben oder Gestaltung von dort:** Das war ein Putzbetrieb, das neue Unternehmen braucht eine eigene Identität.

## Ziel

Der Nutzer baut für Unternehmen neue, hochwertige Websites und bietet sie ihnen zum Kauf an.

1. **Scrapen:** Alle Inhalte der bestehenden Seite **https://wibaperformance.de** sauber strukturiert sichern: Texte, Daten, Bilder, Logos, Farben und Schriften.
2. **Designrichtungen:** Daraus 3 Richtungen als klickbare Mobile-first-Entwürfe vorschlagen. Der Nutzer wählt eine aus.
3. **Website bauen:** Die gewählte Richtung als komplette, statische Website umsetzen, die edler und moderner ist als die alte und **mobile first**.
4. **Testen und Unterlagen:** Gründlich testen, Fragen für den Kunden und Argumente fürs Verkaufsgespräch dokumentieren.

**Kommunikation:** Immer auf Deutsch, knapp und konkret. Bei Designentscheidungen dem Nutzer Auswahlmöglichkeiten geben und eine Empfehlung mit Begründung aussprechen. Nach dem Bau fragt der Nutzer gern nach „Feinschliff“: Dann alle Seiten selbstkritisch prüfen und Schwächen beheben. Zum Zeigen die Seite im Chrome des Nutzers öffnen (Claude in Chrome).

## Arbeitsordner

Arbeite in `/Users/lukabloemendal/Documents/wibaperformance/`. Lege den Ordner an, falls er fehlt. Zielstruktur:

```
wibaperformance/
├── README.md                 Übersicht, Design auf einen Blick, Auffälligkeiten der alten Seite
├── daten/                    strukturierte JSON-Dateien, je nach Inhalt der Seite, z. B.:
│   ├── unternehmen.json      Name, Adresse, Telefon, E-Mail, Register, USt-ID, Inhaber, Gründung, Einsatzgebiet, Slogans, SEO
│   ├── leistungen.json / produkte.json / referenzen.json / team.json / bewertungen.json
│   ├── navigation-sitemap.json  alle alten URLs (für 301-Weiterleitungen), externe Links
│   └── bilder-index.json     jedes Bild: Datei, Größe, Herkunfts-URL, Verwendung, Hinweis
├── inhalte/seiten/*.md       jede Seite als Markdown mit Frontmatter (alte URL, Titel, Meta-Description)
├── bilder/                   logos/, hero/, seiten-header/, <thema>/<nr-name>/ …
├── design/                   farben.json, bildwelt-farben.json, design-tokens.css, farbpalette.html, schriften/
├── screenshots-alte-seite/   Desktop (1440px) und Mobil (390px) jeder Hauptseite
├── entwurf/                  Phase 2: drei Mockups und index.html zum Vergleichen
├── website/                  Phase 3: fertige statische Website
├── website-generator/        build.py, README.md (Pflege, offene Punkte), weiterleitungen.json
└── _raw/                     Original-HTML, CSS, alle Assets, crawl.json, scripts/
```

Temporäre Dateien gehören in das Scratchpad, nicht in den Projektordner.

## Phase 1: Scrapen

**Vorab prüfen:**
- **Werkzeuge:** `python3 -c "import bs4, requests, PIL"`, Google Chrome unter `/Applications/Google Chrome.app`, `node` (für Playwright, siehe Phase 4).
- **Startseite:** `curl -sIL` und `curl -sL`. Folgt sie Weiterleitungen? Welches CMS steckt dahinter? Hinweise darauf:
  - **WordPress:** `wp-content`, `wp-json`
  - **Wix/Squarespace/Jimdo:** viel JavaScript, wenig HTML
  - **Klassisches PHP:** direkte `.php`-Adressen
- **Wird der Inhalt per JavaScript nachgeladen?** Steht der sichtbare Text im rohen HTML? Wenn nicht, mit Playwright rendern und das gerenderte DOM speichern.
- `robots.txt` und `sitemap.xml` (bei WordPress auch `wp-sitemap.xml`) als Liste der Seiten nutzen.

**Crawler** (Vorlage: `emmerich/_raw/scripts/crawl.py`):
- **Was er macht:**
  - Er folgt allen Links auf der eigenen Domain (Breitensuche) und speichert jedes HTML unter `_raw/html/`.
  - Er sammelt alle Bilder: `img src`, `srcset`, `data-src` (Lazy Loading), `style="background:url()"`, `url()` in CSS-Dateien, verlinkte Bilder (Lightbox-Links zeigen oft auf größere Versionen), Favicon und Apple-Touch-Icon, `og:image`.
  - Er lädt alle Stylesheets, auch die aus CSS-Dateien referenzierten Schriften.
- **Regeln:**
  - `time.sleep(0.3)` zwischen den Anfragen.
  - Externe Links nur auflisten, nicht crawlen.
  - Downloads nur in `_raw/`.
  - Python immer mit `-I` starten.
- **Immer die größte Bildversion suchen:**
  - Thumbnails haben oft Originale unter einem anderen Pfad. Bei Emmerich lag `/_thumbnails_/1381_2__X.jpg` im Original unter `/emmerich/Bilder/Referenzen/_X.jpg`.
  - **WordPress:** Größenanhang wie `-300x200` entfernen. `-scaled.jpg` ist die große Version. Über `/wp-json/wp/v2/media` lassen sich alle Medien mit Original-URL abfragen, ebenso Seiten und Beiträge über `/wp-json/wp/v2/pages` und `/posts`.
  - Mit `sips -g pixelWidth -g pixelHeight` die Maße prüfen.
- **Logo:** Gibt es eine SVG-Version? Ausprobieren und im HTML nach `<svg>`-Logos suchen. Sonst das PNG nehmen und mit PIL freistellen: eine transparente Variante und eine weiße für dunkle Hintergründe.

**Aufbereiten** (Vorlage: `emmerich/_raw/scripts/build.py`):
- **Inhalte:** Hauptinhalt jeder Seite ohne Navigation und Footer als Markdown speichern. **Auskommentierte HTML-Inhalte mitnehmen**, denn dort stehen oft nützliche Fakten. Bei Emmerich war dort das Gründungsjahr versteckt.
- **Wiederkehrende Elemente** wie Referenzen, Produkte oder Team strukturiert als JSON ablegen, mit Bildpfaden. Gleiche Bilder per md5 erkennen und nur einmal speichern.
- **Farben:**
  - Alle Hex-, rgb- und hsl-Werte aus dem *eigenen* CSS zählen und nach Verwendung zuordnen: Überschriften, Text, Buttons, Flächen. Framework-Standardwerte (Bootstrap, Foundation, Theme-Vorgaben) davon trennen.
  - Logofarben per Pixelanalyse bestimmen.
  - Bildwelt-Farben per `Image.quantize` bestimmen.
  - Ablage in `farben.json`, `design-tokens.css` und `farbpalette.html`, letztere visuell prüfen.
- **Schriften:** Familie und Schnitte bestimmen. Die Dateien sichern, wenn sie lokal liegen. Kommen sie von Google Fonts, nur notieren.
- **Screenshots der alten Seite:** Mit Playwright im iPhone-Profil aufnehmen, nicht mit Headless-Chrome (Fallstricke siehe Phase 4). Darauf mobile Fehler suchen und festhalten: Überlappungen, abgeschnittener Text, winzige Klickflächen. Das sind Verkaufsargumente.
- **README** mit „Auffälligkeiten für den Pitch“. Danach gezielt suchen:
  - mobile Fehler
  - veraltete Angaben, etwa „seit X Jahren“ oder Jahreszahlen
  - Impressum noch mit TMG statt DDG, Datenschutz ohne DSGVO-Bezug
  - Google Fonts oder Maps ohne Einwilligung
  - widersprüchliche Kontaktdaten
  - Tippfehler
  - fehlende Alt-Texte, Favicon, Sitemap oder Meta-Descriptions
  - Platzhaltertexte
  - **Bilder mit fraglichen Rechten**, z. B. Hersteller-Pressebilder oder Stockfotos mit Wasserzeichen. Am Dateinamen und Bildinhalt prüfen.

## Phase 2: Designrichtungen

- **Zuerst den Skill `frontend-design` laden.** Die Gestaltung aus der Branche, den Materialien und der Fachsprache des Unternehmens ableiten, keine generischen Vorlagen.
- **3 deutlich verschiedene Richtungen** als echte, scrollbare Mobile-first-Startseiten in `entwurf/` bauen, mit Originalfotos und -texten.
  - Jede Richtung bekommt: eine eigene Farbpalette, eine bewusst gewählte Schrift und **ein Erkennungsmerkmal**, also eine Einstiegsanimation oder ein Element, das es nur für diese Branche gibt.
  - Bei Emmerich waren das z. B. „Putz zum Anfassen“ (Nahaufnahmen der Putzstrukturen) und Formen mit einer abgerundeten Ecke wie eine Glättkelle.
- **In allen Entwürfen Pflicht:**
  - Animationen, sparsam und gezielt: eine Einstiegsanimation plus dezentes Einblenden beim Scrollen; `prefers-reduced-motion` beachten
  - Scroll-up-Button
  - Cookie-Banner nach DSGVO, bei dem „Ablehnen“ gleichwertig zu „Zustimmen“ gestaltet ist
  - schwebender Kontakt-Button (Anrufen, E-Mail/Anfrage, Route)
- **Vergleichsseite `entwurf/index.html`:** jeder Entwurf in einem 390px-Handyrahmen als iframe, dazu Palette, Schrift, Erkennungsmerkmal und Wirkung. Unten die alte Seite im gleichen Rahmen zum Vergleich.
- Dem Nutzer die Vergleichsseite zeigen, **eine Empfehlung mit Begründung geben** (welche Richtung zur Zielgruppe passt, was man aus den anderen übernehmen sollte) und **auf seine Wahl warten**.

## Phase 3: Website bauen

**Technik:**
- Statisches HTML, CSS und Vanilla-JS, kein Framework und kein CMS.
- Ein **Python-Generator** `website-generator/build.py` baut alle Seiten aus `daten/`, damit wiederkehrende Seiten wie Referenzen oder Produkte einheitlich bleiben. Vorlage: `emmerich/website-generator/build.py`.
- **Achtung:** Das System-Python ist 3.9. Dort darf ein f-String im Ausdruck keine Anführungszeichen derselben Art enthalten, also kein `f"{d["x"]}"`. Hilfsvariablen verwenden.

**Was die Seite enthalten muss:**
- **Seiten:** alle Inhalte der alten Seite, sinnvoll neu gegliedert, außerdem Impressum, Datenschutz und eine 404-Seite.
- **Kontakt:**
  - Kontaktseite mit Formular. Ohne Backend erzeugt es per JS eine `mailto:`-Nachricht; ein echter Formularversand gehört zu den offenen Punkten.
  - Google Maps erst nach Einwilligung laden, vorher Platzhalter mit „Karte laden“.
  - Auf dem Handy eine feste Kontaktleiste unten (Anrufen, Anfrage), die nach etwas Scrollen erscheint. Am Desktop ein aufklappbarer Kontakt-Button.
- **Weitere Elemente:** Scroll-up-Button, Cookie-Banner mit „Cookie-Einstellungen“ im Footer zum erneuten Öffnen, mobiles Vollbildmenü.
- **Galerien** mit Lightbox per `<dialog>`, bedienbar mit Pfeiltasten, Wischen und Escape. Filter bei Listen, wenn es Kategorien gibt.
- **Bilder:** Mit PIL in 800 und 1600 px als progressives JPEG mit Qualität 78 speichern und per `srcset/sizes` ausliefern. `loading="lazy"`, nur beim Hero-Bild `fetchpriority="high"`.
- **Schriften selbst hosten**, nicht bei Google laden (DSGVO). Die woff2-URLs bekommt man von der Google-Fonts-CSS-API mit einem modernen Browser als User-Agent; nur die `latin`-Teilmenge laden.
- **SEO:**
  - Titel, Meta-Description, Canonical und Open Graph auf jeder Seite
  - Schema.org-LocalBusiness als JSON-LD
  - `sitemap.xml`, `robots.txt`
  - Favicon aus dem Logo erzeugen
  - Alt-Texte für alle Bilder
- **`.htaccess`** (sofern der Server Apache ist, siehe Phase 5): 301-Weiterleitungen aller alten URLs auf die neuen, HTTPS und www erzwingen, `ErrorDocument 404`, Caching, Sicherheits-Header.
- **Texte:**
  - Tippfehler korrigieren, veraltete Angaben aktualisieren.
  - **Keine Fakten erfinden**: keine Öffnungszeiten, Garantien oder Zahlen, die nicht belegt sind.
  - Impressum nach § 5 DDG.
  - Datenschutz als Entwurf passend zur tatsächlichen Technik, mit dem Hinweis „vor Veröffentlichung rechtlich prüfen“.
- **Barrierefreiheit:**
  - Sprunglink „Zum Inhalt springen“ und sichtbarer Fokus
  - Kontrast mindestens 4,5:1 für kleinen Text; mittlere Grautöne auf hellem Grund nachrechnen
  - Silbentrennung (`hyphens: auto`) **nur auf kleinen Bildschirmen**, am Desktop sieht sie unruhig aus; nicht bei Zitaten und großen Überschriften

## Phase 4: Testen (Pflicht, vor jeder Fertigmeldung)

- **Lokaler Server:** In `.claude/launch.json` die Konfiguration `python3 -m http.server 8080 --directory website` eintragen und starten.
- **Playwright mit dem System-Chrome:** `npm install playwright-core` im Scratchpad, dann `chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' })`. Vorlagen liegen in `emmerich/website-generator/tests/`: `shots.js` (Screenshots und Fehlerprüfung), `small.js` (320px und Tastatur), `interact.js` (Klick-Test). Das Vorgehen:
  - Jede Seite mit iPhone-Profil (390px) und Desktop (1440px) laden.
  - Konsolenfehler, Antworten ≥ 400 und horizontalen Überlauf (`scrollWidth - innerWidth`) sammeln.
  - **Alle Seiten zusätzlich bei 320px auf Überlauf prüfen.**
  - Klick-Test: Menü auf/zu, Cookie-Banner (erscheint, schließt, speichert die Wahl), Scroll-up, Kontaktleiste, Filter, Lightbox (öffnen, weiter, Escape), Formular.
  - Tastatur: Der erste Tab muss den Sprunglink fokussieren.
- **Bekannte Fallstricke** (alle schon einmal passiert):
  - **Headless-Chrome-Screenshots** rendern nie schmaler als etwa 500px, deshalb für Mobil immer Playwright nutzen. In iframes laufen dort außerdem keine Animationen; Inhalte wirken dann unsichtbar, sind es aber nicht.
  - **Ganzseiten-Screenshots** bei Faktor 3 werden über 16.384px abgeschnitten. `deviceScaleFactor: 1` verwenden, vorher durch die Seite scrollen, damit Lazy-Bilder laden, und `[data-reveal]` vorher auf sichtbar setzen.
  - **Fixe Elemente** (Header, Kontaktleiste) erscheinen in Ganzseiten-Screenshots mitten im Bild. Das ist kein Fehler; im Zweifel per `getComputedStyle` prüfen.
  - **`backdrop-filter` am Header** sperrt ein darin liegendes `position: fixed`-Menü auf Header-Höhe ein, das Vollbildmenü wird dann durchsichtig. Lösung: den Filter bei geöffnetem Menü abschalten.
  - **Abgerundete Ecken mit `overflow: hidden`** schneiden Beschriftungen ab, die in dieser Ecke sitzen.
  - **Textfarben in dunklen Sektionen** für *alle* Elemente prüfen; bei Emmerich waren Jahreszahlen dunkel auf dunkel.
  - **`navigate` im eingebauten Browserfenster** kann für localhost gesperrt sein. Dann Playwright für Tests verwenden und Claude in Chrome zum Zeigen.
- **Screenshots selbst ansehen** und kritisch bewerten, bevor du dem Nutzer etwas als fertig meldest. Ehrlich sagen, was nicht getestet wurde, z. B. echtes iPhone und Safari.

## Phase 5: Hosting und Übergabe

- **Hosting bestimmen**, nur aus öffentlichen Angaben, keine Login-Versuche:
  - `dig` (A, NS, MX, TXT, SOA)
  - `whois` der IP
  - `whois -h whois.denic.de` bei .de-Domains
  - Server-Header, SSL-Aussteller (`openssl s_client`), CMS-Spuren
  - Daraus ableiten: Läuft dort Apache, passt die `.htaccess` dann? Wie wird hochgeladen? Was gehört in die Datenschutzerklärung (Hoster, Vertrag zur Auftragsverarbeitung)?
- **`website-generator/README.md`:** Ansehen, neu erzeugen, Seitenliste, Funktionen, was getestet wurde und was nicht, und **„Vor dem Go-live mit dem Kunden klären“** (Kontaktdaten, Bildrechte, Datenschutz prüfen lassen, Formular-Backend, Logo als Vektordatei, Zahlen aktualisieren).
- Am Ende anbieten, eine Vorher-Nachher-Präsentation für das Verkaufsgespräch zu erstellen.

## Wiederverwendbarer Code aus dem Emmerich-Projekt

| Datei | Wofür |
|---|---|
| `emmerich/_raw/scripts/crawl.py` | Crawler: Seiten, CSS und Assets |
| `emmerich/_raw/scripts/build.py` | Aufbereitung: Markdown, JSON, Bildordner, Logo-Varianten |
| `emmerich/entwurf/shared.js`, `entwurf/index.html` | Gemeinsame Funktionen der Entwürfe, Vergleichsseite mit Handyrahmen |
| `emmerich/website-generator/build.py` | Seitengenerator: Layout, Bildpipeline, SEO, `.htaccess`, Favicon |
| `emmerich/website/assets/js/main.js` | Menü, Cookie, Scroll-up, Kontaktleiste/-Button, Reveal, Filter, Lightbox, Karte nach Einwilligung, mailto-Formular |
| `emmerich/website/assets/css/style.css` | Aufbau und Komponenten. **Farben, Schriften und Formen komplett neu gestalten.** |
| `emmerich/website-generator/tests/*.js` | Playwright-Tests: Screenshots, 320px-Überlauf, Tastatur, Klick-Test. Seitenliste und Selektoren anpassen. |

Die Emmerich-Ordner nur lesen und nicht verändern.

## Grenzen

- Nur öffentlich zugängliche Inhalte scrapen, zurückhaltend und mit Pausen zwischen den Anfragen.
- Keine Logins, keine Formulare der alten Seite absenden.
- Bilder und Texte gehören dem Kunden bzw. den Urhebern. Sie dienen dem Angebot an genau dieses Unternehmen; fragliche Rechte im README vermerken.
- Nichts veröffentlichen oder deployen, ohne dass der Nutzer es ausdrücklich verlangt.
