# WIBA Performance – neue Website

Relaunch der Website von **WIBA Performance**, Felgen- und Reifenhandel in Rahden (bisher https://www.wibaperformance.de auf Wix).
Statische Website aus HTML, CSS und Vanilla-JavaScript, erzeugt von einem kleinen Python-Generator. Kein Framework, kein CMS, keine Verbindung zu Drittanbietern beim Laden.

**Stand:** Website fertig gebaut und getestet (16.11.2026), noch nicht veröffentlicht. Offene Punkte für den Kunden stehen in [website-generator/README.md](website-generator/README.md#vor-dem-go-live-mit-dem-kunden-klären).

## Inhalt des Repositorys

| Ordner / Datei | Inhalt |
|---|---|
| [`website/`](website/) | **Die fertige Website**, so wie sie auf den Server kommt (inkl. `.htaccess`, `sitemap.xml`, `robots.txt`) |
| [`website-generator/`](website-generator/) | `build.py` (erzeugt `website/`), Tests, Weiterleitungsliste, Doku zu Funktionen, Tests und Hosting |
| [`daten/`](daten/) | Inhalte als JSON: Unternehmen, Leistungen und Preise, Bewertungen, AGB, alte URLs |
| [`bilder/`](bilder/) | Originalfotos, Logos und Video, sortiert nach Thema (Quelle für den Generator) |
| [`inhalte/seiten/`](inhalte/seiten/) | Texte der alten Seite als Markdown |
| [`design/`](design/) | Farben, Bildwelt-Farben, Schriften der alten Seite |
| [`entwurf/`](entwurf/) | Sechs Designrichtungen (A–F) als klickbare Handy-Entwürfe, Vergleich in `entwurf/index.html` |
| [`screenshots-alte-seite/`](screenshots-alte-seite/) | Aufnahmen der alten Seite, Desktop und Handy |
| [`_raw/`](_raw/) | Scraping-Skripte und deren Ergebnisse (`crawl-render.json`, `extract.json`). Rohe HTML- und Mediendateien sind wegen der Größe nicht im Repository und lassen sich neu laden |
| [`docs/analyse-alte-seite.md`](docs/analyse-alte-seite.md) | Analyse der alten Seite, Auffälligkeiten und Argumente fürs Verkaufsgespräch |
| `BRIEFING-wibaperformance.md` | Arbeitsauftrag für den Relaunch |

## Schnellstart

Voraussetzungen: Python 3.9 oder neuer, für die Tests Node.js 18+ und Google Chrome.

```bash
pip3 install -r requirements.txt
```

```bash
npm install
```

Website neu erzeugen und lokal ansehen:

```bash
npm run build
```

```bash
npm run serve
```

Dann http://localhost:8090 öffnen. Die Entwürfe: `npm run serve:entwurf`, dann http://localhost:8082.

Tests (bei laufendem Server):

```bash
npm test
```

| Befehl | Was passiert |
|---|---|
| `npm run build` | erzeugt alle Seiten, Bildgrößen, Favicon, Sitemap und `.htaccess` neu nach `website/` |
| `npm run serve` | lokaler Server für `website/` auf Port 8090 |
| `npm test` | Klick- und Tastaturtest (37 Prüfungen) und Überlauftest bei 320 px |
| `npm run test:shots` | Aufnahmen aller Seiten bei 390, 320 und 1440 px nach `test-ergebnisse/`, dazu Fehler- und Überlaufprüfung |
| `npm run scrape` | lädt die alte Wix-Seite erneut und erzeugt `daten/`, `bilder/` und `inhalte/` neu |

CSS, JavaScript und Schrift liegen direkt in `website/assets/` und werden vom Generator nicht überschrieben.

## Veröffentlichen

**Vorschau:** https://lukabpunkt.github.io/wibaperformance/ – wird bei jedem Push auf `main`, der `website/` ändert, automatisch über GitHub Pages aktualisiert ([`.github/workflows/pages.yml`](.github/workflows/pages.yml)). Die Vorschau ist für Suchmaschinen gesperrt (`noindex`), damit sie nicht mit der späteren Domain konkurriert.

**Live-Betrieb:** Der Inhalt von `website/` wird 1:1 auf einen Webspace hochgeladen (z. B. per SFTP). Die `.htaccess` setzt einen Apache-Server voraus. Wix kann kein eigenes HTML ausliefern, deshalb ist ein neuer Hoster nötig. Details, DNS-Umzug und E-Mail-Hinweise: [website-generator/README.md](website-generator/README.md#hosting).

## Rechte

Kein Open-Source-Projekt. Texte, Fotos, Logo und Bewertungen gehören WIBA Performance bzw. den jeweiligen Urhebern und dienen ausschließlich dem Angebot an dieses Unternehmen. Das Repository sollte deshalb **privat** bleiben. Schrift: Hanken Grotesk (SIL Open Font License).
