# Analyse der alten Website

Alte Seite: https://www.wibaperformance.de (Wix, Stand des Abrufs: 13.11.2026)
Inhaber: Witali Bakin · Hackelbarg 7 · 32369 Rahden · Felgen- und Reifenhandel, Kfz-Service

## Ordner

| Ordner | Inhalt |
|---|---|
| `daten/` | `unternehmen.json`, `leistungen.json` (Reifen-, Felgen-, Klimaservice, Aufbereitung, Ersatzteile inkl. Preise), `bewertungen.json` (9 Bewertungen + 22 Kundenfahrzeuge), `startseite.json`, `ueber-uns.json`, `gewinnspiel.json`, `navigation-sitemap.json` (alle alten URLs, externe Links), `bilder-index.json` (75 Dateien) |
| `inhalte/seiten/` | 11 Seiten als Markdown mit Frontmatter |
| `bilder/` | `logos/`, `hero/`, `seiten-header/`, `felgenservice/{sortiment,galerie}`, `reifenservice/`, `fahrzeugaufbereitung/`, `ersatzteile/`, `kunden/`, `video/`, `icons-alte-seite/`. Alle Fotos in Originalauflösung (meist 3024×4032), EXIF-Drehung angewendet |
| `design/` | `farben.json`, `bildwelt-farben.json`, `design-tokens.css`, `farbpalette.html`, `schriften/README.md` |
| `screenshots-alte-seite/` | Desktop 1440px und Mobil (iPhone-Profil; Wix rendert mobil fest mit 320px) jeder Seite |
| `_raw/` | Skripte, `crawl-render.json`, `extract.json`. Rohes HTML und Medien-Originale sind nicht im Repository (siehe `.gitignore`) |

Neu erzeugen (im Projektordner, nach `npm install`): `npm run scrape`

## Seitenstruktur alt

| Alte URL | Inhalt |
|---|---|
| `/` | Willkommen, Öffnungszeiten |
| `/produkte` | **Reifenservice** mit Preisliste |
| `/services` | **Felgenservice** (Verkauf, Ankauf, Sortiment, Galerie, Video) |
| `/dienstleistungen-1` | Klimaservice mit 3 Preisen |
| `/dienstleistungen-2` | Fahrzeugaufbereitung, Galerie mit 15 Bildern |
| `/dienstleistungen-3` | Ersatzteile & Zubehör (1 Produkt: BMW-Nabenkappen 20 €) |
| `/customer-name` | Unsere Kunden: 22 Fahrzeugfotos und 9 Bewertungen |
| `/über-uns` | Kurztext und Video |
| `/kontakt` | Adresse, E-Mail, Mobil, Fax, Formular |
| `/agb` | AGB **und** Datenschutzerklärung auf einer Seite (Seitentitel „Datenschutz“) |
| `/gewinnspiel-jetzt-mitmachen` | Gewinnspiel 12.02.–04.03.2026 (abgelaufen) |

## Design auf einen Blick

- **Logo:** schwarz, kursive Sportwagen-Schrift „WIBA PERFORMANCE“ mit Fahrzeug-Silhouette (Linienzeichnung). Nur PNG, kein Vektor. Varianten schwarz und weiß transparent liegen in `bilder/logos/`.
- **Farben:** faktisch schwarz/weiß/hellgrau (#000, #04040C, #F0F0F0). Keine Markenfarbe. Die Wix-Vorlagenpalette (Lila/Petrol) wird nicht genutzt.
- **Bildwelt:** eigene iPhone-Fotos aus der Werkstatt: weiße Wände, Wandlogo, eingeschweißte Reifensätze, Felgen in Anthrazit, Schwarz und Silber, blaue Werkzeugmaschinen (#2289C9), Kundenautos auf Pflaster. Authentisch, aber oft schief, mit Gegenlicht oder unruhigem Hintergrund.
- **Schriften:** Barlow Medium/ExtraLight (frei) und Avenir Light (Wix-Lizenz, nicht übertragbar).
- **Ton:** „Sie“ auf allen Seiten, „du“ in Datenschutz, Bewertungsaufruf und Gewinnspiel (uneinheitlich).

## Auffälligkeiten für den Pitch

### Rechtliches (dringend)
1. **Kein Impressum vorhanden.** Auf keiner Seite, auch nicht im Footer. Pflicht nach § 5 DDG, abmahnfähig.
2. **Datenschutzerklärung mit Platzhalter:** „Anfragen kannst du richten an: [E-Mail-Adresse]“. Hoster (Wix), Cookies, Google-Dienste und Kontaktformular werden nicht konkret benannt.
3. **AGB und Datenschutz auf derselben Seite**, Seitentitel „Datenschutz“, URL `/agb`, Überschrift „Datenschutzerklärung“, darunter beginnen die AGB.
4. **Cookie-Banner ohne „Ablehnen“:** nur „Zustimmen“ und „Einstellungen“. Nicht DSGVO-konform (Ablehnen muss gleichwertig sein).
5. **Google Fonts (Roboto) wird direkt von fonts.gstatic.com geladen**, ohne Einwilligung.
6. **Gewinnspiel abgelaufen** (Ende 04.03.2026), Seite aber noch online. In den Teilnahmebedingungen steht der Platzhalter „[E-Mail / Telefon / WhatsApp]“.
7. **Kundenfotos mit lesbaren Kennzeichen** (mehrere Bilder in `bilder/kunden/`): Einverständnis klären oder unkenntlich machen.

### Mobil
8. **Telefon-Link falsch:** Auf dem Handy erkennt Wix nur „4151974“ als Nummer, ein Tipp wählt `tel:4151974` **ohne Vorwahl 0160**. Gleiches beim Fax. Anrufe über die Seite laufen ins Leere – für einen Betrieb „nach Vereinbarung“ das wichtigste Verkaufsargument.
9. **Mobilseite fest auf 320px** (Wix-Mobilansicht), wirkt auf modernen Handys klein und grob.
10. Footer-Link „AGB & Daten…“ ist **abgeschnitten**.
11. **Winzige Klickflächen:** Social-Icons 20×20px, E-Mail- und Telefonlinks 17px hoch (empfohlen ≥ 44px).
12. Der Cookie-Banner überdeckt auf dem Handy fast den ganzen ersten Bildschirm.

### Inhalt und Qualität
13. **Widersprüchliche Kontaktdaten:** E-Mail w.bakin@ (Header/Footer) vs. info@ (Kontakt, Datenschutz). Drei Telefonnummern: Mobil 0160 4151974, Fax 05776 9619998 (nur Kontaktseite), Festnetz 05776 3060088 (nur Datenschutz).
14. **Startseite fast leer:** ein Begrüßungstext, darunter eine große weiße Fläche, dann Öffnungszeiten. Keine Leistungen, keine Preise, keine Bewertungen, kein Handlungsaufruf.
15. **Nichtssagende URLs** aus der Wix-Vorlage: `/customer-name`, `/dienstleistungen-1/-2/-3`, `/services` = Felgenservice, `/produkte` = Reifenservice. Schlecht für Google.
16. **Fehlende Meta-Descriptions** auf 7 von 11 Seiten. Wo vorhanden, oft abgeschnitten („… Ihr Reifenhandel“).
17. **Alt-Texte fehlen** bei 71 von 198 Bildern, sonst nur Dateinamen wie „IMG_1158_edited.jpg“.
18. **Favicon ist das Wix-Standardsymbol**, nicht das WIBA-Logo.
19. **Copyright „©2021“**, veraltet.
20. **Tippfehler und Grammatik:** „RDSK - Sensoren“ (statt RDKS), „unsren Herstellersortiment“, „kühlt nicht richtig ? Wir regeln das !“ (Leerzeichen vor Satzzeichen), „WIBA Performance gegründet, um …“ (Satz unvollständig, Über uns), „Kfz - Ersatzteilen“.
21. **Bewertungen:** die russische Bewertung ist doppelt eingefügt, die erste beginnt mitten im Satz („Winterreifen in Auftrag gegeben.“). Kein Link zu Google, keine Sterne.
22. **Video nur in 480p** auf Wix verfügbar.
23. Leistungen aus dem Gewinnspiel (Reifeneinlagerung, Radwäsche) tauchen auf den Leistungsseiten nicht auf.
24. Klimaservice nennt nur Kältemittel **R134a**; neuere Autos nutzen R1234yf. Klären, ob das angeboten wird.
25. **Kein SPF-Eintrag** für die Domain (E-Mails landen leichter im Spam). E-Mail läuft über IONOS, Website und DNS über Wix.

### Bildrechte
- Fast alle Fotos sind eigene iPhone-Aufnahmen (Dateinamen IMG_xxxx, EXIF-Daten) → unkritisch, sofern vom Inhaber.
- Herstellerlogos (BMW, Mercedes, Audi auf Nabenkappen; BH Sens/Intellisens, Mann, Bosch, Febi auf Verpackungen) sind nur abgebildet. Bei Werbenutzung zurückhaltend einsetzen.
- **Personen im Bild** (Mitarbeiter in Hero und Aufbereitungs-Header): Einverständnis klären.
- **Kundenfahrzeuge** mit Kennzeichen: siehe oben.

## Offen für Phase 3
- Impressum: Rechtsform, USt-ID bzw. Steuernummer, ggf. Handwerkskammer beim Kunden erfragen.
- Gründungsjahr (vermutlich 2021, Domain seit 08.04.2021).
- Welche E-Mail und welche Telefonnummern öffentlich? WhatsApp-Kontakt gewünscht (in AGB erwähnt)?
- Preise inkl. MwSt.? Reifenmontage pro Rad?
- Google-Bewertungen: Link und aktueller Schnitt.
- Neuer Hoster nötig (Wix hostet kein eigenes HTML), Domain-Umzug von Wix-DNS.

## Stand der Arbeit

| Phase | Ergebnis |
|---|---|
| 1 Scrapen | abgeschlossen (siehe oben) |
| 2 Entwürfe | `entwurf/index.html`: Runde 1 (A Felgenstern, B Reifenflanke, C Auftragszettel), Runde 2 (D Startknopf, E Galerie, F Lackglanz) |
| 3 Website | `website/`, gebaut mit `website-generator/build.py`. Richtung **E**, mit Auftragszettel aus C, Vorher-Nachher aus F und Zählern aus D |
| 4 Tests | `website-generator/tests/`, Ergebnisse und offene Punkte in `website-generator/README.md` |
| 5 Hosting | Analyse und Vorgehen in `website-generator/README.md` |

## Argumente fürs Verkaufsgespräch

1. **Anrufe kommen wieder an.** Auf der alten Seite wählt der Telefon-Link am Handy nur „4151974“, ohne Vorwahl. Die neue Seite hat Anrufen-Buttons mit der vollständigen Nummer an jeder Stelle.
2. **Rechtssicher statt abmahngefährdet:** Impressum nach § 5 DDG (fehlt heute komplett), Datenschutz passend zur Technik, Cookie-Banner mit „Ablehnen“, keine Google-Schriften und keine Google-Karte ohne Einwilligung.
3. **Preise sofort sichtbar:** Der Auftragszettel zeigt in drei Tipps den Festpreis und schreibt die Anfrage gleich mit. Das ist der direkteste Weg vom Interesse zum Termin.
4. **Startseite verkauft:** statt Begrüßung und leerer Fläche jetzt Leistungen, Preise, Felgen, Vorher-Nachher und Bewertungen.
5. **Hochwertiger Auftritt** passend zu Felgen und Tuning: das Intro durch die Buchstaben, die Galerie, die seitwärts läuft, große Typografie.
6. **Bei Google auffindbar:** sprechende Adressen statt `/dienstleistungen-1`, Beschreibungen und Titel für jede Seite, strukturierte Daten, Sitemap, 301-Weiterleitungen aller alten Adressen.
7. **Schnell und unabhängig:** statische Seite ohne Wix-Abo, eigene Schrift, Bilder in passenden Größen.
8. **Aktuell:** abgelaufenes Gewinnspiel und Platzhaltertexte sind weg, Tippfehler korrigiert, © aktuell.
