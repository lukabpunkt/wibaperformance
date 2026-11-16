# WIBA Performance – neue Website

Statische Website (HTML, CSS, Vanilla-JS, kein Framework, kein CMS). Gestaltung: Richtung **E „Galerie“**, ergänzt um den **Auftragszettel** (C), den **Vorher-Nachher-Regler** (F) und **hochzählende Preise** (D).

## Ansehen

```bash
python3 -m http.server 8090 --directory website
```

Dann http://localhost:8090 öffnen. Kurz: `npm run serve`.

## Neu erzeugen

```bash
python3 -I website-generator/build.py   # oder: npm run build
```

- Liest `daten/*.json` und `bilder/`, schreibt alle Seiten, Bilder (480/800/1200/1600 px, progressives JPEG, Qualität 78), Logos, Favicon, Video, `sitemap.xml`, `robots.txt`, `.htaccess` und `site.webmanifest` nach `website/`.
- Preise kommen aus `daten/leistungen.json`, Bewertungen aus `daten/bewertungen.json`, AGB aus `daten/agb.json`. Seitentexte stehen im Generator.
- `website/assets/css/style.css`, `assets/js/main.js` und `assets/fonts/` werden **nicht** überschrieben, sie werden direkt bearbeitet.
- System-Python 3.9: in f-Strings keine gleichen Anführungszeichen im Ausdruck.

## Seiten

| Neue URL | Alte URL (301) | Inhalt |
|---|---|---|
| `/` | `/`, `/gewinnspiel-jetzt-mitmachen` | Zoom-Intro, Fülltext, Auftragszettel, Leistungen, Galerie seitwärts, Vorher-Nachher, Kunden |
| `/reifenservice/` | `/produkte` | Text, Bilder, alle Reifenpreise, Zettel |
| `/felgenservice/` | `/services` | Verkauf, Ankauf, Sortiment, Galerie (9), Video |
| `/klimaservice/` | `/dienstleistungen-1` | Text, Preise, Zettel |
| `/fahrzeugaufbereitung/` | `/dienstleistungen-2` | Vorher-Nachher (4 Beispiele), Galerie (10), Zettel |
| `/ersatzteile-zubehoer/` | `/dienstleistungen-3` | Text, Produkt BMW-Nabenkappen |
| `/kunden/` | `/customer-name` | 9 Bewertungen, Google-Aufruf, 22 Kundenautos |
| `/ueber-uns/` | `/über-uns` | Text, Video, Fakten |
| `/kontakt/` | `/kontakt` | Daten, Formular (mailto), Karte nach Einwilligung |
| `/impressum/`, `/datenschutz/`, `/agb/` | `/agb` | Rechtstexte (Impressum und Datenschutz als Entwurf) |
| `/404.html` | | Fehlerseite |

Alle Weiterleitungen: `website-generator/weiterleitungen.json` bzw. `website/.htaccess`.

## Funktionen

- **Intro „Durch das I“** (Startseite): Das Felgenfoto liegt dauerhaft scharf im Hintergrund, darüber eine Kalk-Fläche mit ausgestanztem „WIBA“ (SVG-Maske). Beim Scrollen wird nur diese Fläche skaliert (GPU-Transform), es gibt keinen Bildwechsel und kein Neuzeichnen von Text-Ausschnitten. Die Animation startet erst, wenn Bild **und** Schrift geladen sind (`img.decode()` + `document.fonts.load`), mit 3,5 s Sicherheits-Zeitlimit.
- **Auftragszettel**: Leistung und Größe antippen, Festpreis zählt hoch, „Anfrage senden“ öffnet eine fertige E-Mail. Auf Leistungsseiten vorbelegt (`data-start`).
- **Vorher-Nachher-Regler**: echte Aufbereitungsfotos, per Maus, Finger und Tastatur bedienbar, führt sich beim ersten Sehen selbst vor.
- Galerie läuft seitwärts beim Scrollen, Text füllt sich Wort für Wort, Wort-Reveal der Überschriften, Kundenfotos mit Parallaxe, Preise zählen hoch.
- Lightbox mit `<dialog>`: Pfeiltasten, Wischen, Escape, Zähler.
- Handy: feste Kontaktleiste unten (Anrufen, Anfrage) nach dem Intro bzw. nach etwas Scrollen. Desktop: aufklappbarer Kontakt-Button (Route, Anfrage, Anrufen).
- Cookie-Banner: „Ablehnen“ gleichwertig zu „Zustimmen“, erneut über „Cookie-Einstellungen“ im Footer. Google Maps erst nach Einwilligung.
- Vollbildmenü als Vorhang, Scroll-up-Button, Sprunglink „Zum Inhalt springen“, sichtbarer Fokus.
- Schrift Hanken Grotesk selbst gehostet (nur Latin-Teilmenge, 35 KB). Keine Verbindung zu Google beim Laden.
- „Bewegung reduzieren“: alle Animationen aus, Inhalt vollständig sichtbar. Ohne JavaScript ist die Seite ebenfalls lesbar.
- SEO: Titel, Beschreibung, Canonical, Open Graph auf jeder Seite, Schema.org `TireShop` als JSON-LD, Sitemap, robots.txt, Favicon und Touch-Icon aus dem Logo, Alt-Texte für alle Bilder.

## Getestet (16.11.2026)

Tests liegen in `website-generator/tests/` und nutzen Playwright mit dem installierten Google Chrome. Einmalig `npm install`, dann bei laufendem Server (`npm run serve`) `npm test` bzw. `npm run test:shots` (Aufnahmen nach `test-ergebnisse/`). Anderer Chrome-Pfad: `CHROME_PATH=/pfad/zu/chrome npm test`.

| Test | Ergebnis |
|---|---|
| `shots.js`: alle 13 Seiten bei 390 px (iPhone-Profil), 320 px und 1440 px: Konsolenfehler, Antworten ≥ 400, horizontaler Überlauf | keine Fehler |
| `small.js`: alle Seiten bei 320 px nach Laden der Schrift, Fokus sichtbar | 0 px Überlauf, Fokus überall sichtbar |
| `interact.js`: 35 Prüfungen (Sprunglink, Cookie, Menü, Kontaktleiste, Scroll-up, Zettel, Regler, Galerie, Lightbox, Formular, Karte, Desktop-Navigation, Kontakt-Button, Zähler, reduzierte Bewegung) | alle bestanden |
| Bildrate beim Scrollen durch das Intro (Chrome, auch mit 4-fach gedrosselter CPU) | ca. 60 Bilder/s, keine langen Frames |

**Nicht getestet:** echtes iPhone und Safari (besonders Intro, `svh`-Höhen und Sticky-Abschnitte), Android-Geräte, Firefox, Screenreader im Detail, Verhalten auf dem späteren Server (`.htaccess`).

## Hosting

- Heute: Website und DNS bei **Wix**, E-Mail bei **IONOS** (MX `mx00/mx01.ionos.de`). Wix kann kein eigenes HTML hosten, ein **neuer Webspace** ist nötig.
- Naheliegend: Webhosting bei IONOS (dort liegt schon die E-Mail). IONOS-Webhosting läuft auf Apache, die `.htaccess` passt dann (Weiterleitungen, HTTPS, Caching, Sicherheits-Header). Bei einem Nginx-Hoster müssen die Regeln übertragen werden.
- Hochladen: Inhalt von `website/` per SFTP in das Web-Verzeichnis. Danach die Nameserver bzw. A-Records der Domain von Wix auf den neuen Hoster umstellen, **MX-Einträge für IONOS-Mail dabei unverändert lassen**.
- Bei der Gelegenheit einen **SPF-Eintrag** setzen (fehlt heute, E-Mails landen leichter im Spam).
- In der Datenschutzerklärung den Hoster eintragen und einen Vertrag zur Auftragsverarbeitung abschließen.

## Vor dem Go-live mit dem Kunden klären

1. **Impressum:** Rechtsform (Einzelunternehmen?), USt-IdNr. bzw. Steuernummer, ggf. Handwerkskammer. Im Impressum gelb markiert.
2. **Kontaktdaten:** Öffentlich steht jetzt `info@wibaperformance.de` (die alte Seite nennt auch `w.bakin@…`). Nur die Mobilnummer 0160 4151974 ist eingebaut. Festnetz 05776 3060088 und Fax 05776 9619998 weglassen oder ergänzen? Soll WhatsApp als Kontaktweg dazu (in den AGB erwähnt)?
3. **Datenschutz** von einer Fachperson prüfen lassen, Hoster ergänzen.
4. **Formular-Backend:** Formular und Zettel öffnen heute das E-Mail-Programm. Echter Versand braucht ein kleines PHP-Skript beim Hoster oder einen Formulardienst (dann Datenschutz anpassen).
5. **Bildrechte und Personen:** Einverständnis der Mitarbeiter auf Hero- und Aufbereitungsfotos. **Kennzeichen** auf Kundenfotos unkenntlich machen oder Zustimmung der Kunden einholen.
6. **Bewertungen:** Link zum Google-Profil (heute eine Google-Maps-Suche), aktuellen Sternedurchschnitt nennen? Die Bewertung von D. Kindermann beginnt mitten im Satz; vollständigen Text bei Google nachsehen.
7. **Preise:** aktuell? Reifenmontage pro Rad? Klimaservice auch mit R1234yf (neuere Fahrzeuge)? Laut AGB §5 verstehen sich alle Preise inklusive MwSt., so steht es jetzt auf der Seite.
8. **Aufbereitung:** Pakete oder Richtpreise? Heute „Preis auf Anfrage“.
9. **Weitere Leistungen** aus dem alten Gewinnspiel: Reifeneinlagerung, Radwäsche. Gehören sie ins Angebot?
10. **Gründungsjahr** (vermutlich 2021) und Teamgröße, falls sie genannt werden sollen.
11. **Logo als Vektordatei** (SVG/PDF), falls vorhanden. Bisher nur PNG.
12. **Video** gibt es bei Wix nur in 480p. Gibt es das Original in höherer Auflösung?
13. **Ersatzteile:** BMW-Nabenkappen 20 € pro Stück oder pro Satz? Noch aktuell?

## Feinschliff (16.11.2026)

- Startseite: Werkstattfoto neben dem Fülltext, Galerie-Unterschriften untereinander statt rechtsbündig, Bewertungen mit ähnlich langen Zitaten (die langen stehen auf /kunden/), Leistungsbeschreibungen am Desktop größer.
- Auftragszettel: feine Linie statt abgeschnittenem Schatten, mehr Luft unter dem Druckerschlitz, Buttons auf dem Handy einzeilig, Summenzeile bricht sauber um.
- Handy: Scroll-up sitzt jetzt in der Kontaktleiste statt über dem Inhalt; E-Mail-Adresse im Footer bricht nicht mehr mitten im Wort.
- Desktop: Kontakt-Button verdeckt den Footer nicht mehr; Rechtstexte bündig unter der Überschrift.
- Ersatzteile: größere Produktkarte und zusätzlich die Zubehör-Galerie (Radschrauben, Zentrierringe, Nabenkappen, RDKS).
- Fehlenden Punkt in einer Bewertung ergänzt (Zeilenumbruch im Original), Mittelpunkt-Trenner entfernt.
- Tests danach: alle Seiten fehlerfrei bei 390/320/1440 px, 35 von 35 Klick- und Tastaturprüfungen bestanden.

## Feinschliff 2 (16.11.2026)

- Barrierefreiheit: Bei geöffnetem Menü ist der Rest der Seite gesperrt (`inert`), der Fokus springt ins Menü und bleibt dort.
- Navigation: Menü-Knopf auch am Desktop, damit Ersatzteile und Über uns erreichbar sind; volle Navigation ab 1240 px, darunter Telefon und Menü.
- Video mit eigenem Play-Knopf statt der Standard-Steuerung; Steuerung erscheint erst beim Abspielen.
- Auftragszettel: Hinweis passt sich an (Festpreis bzw. Angebot nach Aufwand).
- Übersetzung der russischen Bewertung sauber abgesetzt.
- Teilen-Vorschaubild 1200×630 (Werkstatt mit Wandlogo) für alle Seiten.
- Bildstufen 480/800/1200/1600 für Galerien und Vorschaubilder: Startseite komplett durchgescrollt auf dem iPhone 3,8 MB statt 4,9 MB, erster Bildschirm ca. 250 KB.
- Sanfte Seitenübergänge (View Transitions) in Browsern, die sie unterstützen; bei „Bewegung reduzieren“ aus.
- Tests danach: alle Seiten fehlerfrei bei 390/320/1440 px, 37 von 37 Prüfungen bestanden.
