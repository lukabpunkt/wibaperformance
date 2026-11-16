// node interact.js -> Klick- und Tastaturtest (mobil 390, Desktop 1440)
const { chromium, devices } = require('playwright-core');
const BASE = process.env.BASE || 'http://localhost:8090/';
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const r = []; const ok = (n, v) => r.push((v ? 'OK     ' : 'FEHLER ') + n);
  // Mobil
  let c = await b.newContext({ ...devices['iPhone 13'] }); let p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(BASE); await p.waitForTimeout(800);
  await p.keyboard.press('Tab'); ok('Erster Tab fokussiert Sprunglink', await p.evaluate(() => document.activeElement.classList.contains('skip')));
  await p.waitForTimeout(2400);
  ok('Cookie-Banner erscheint', await p.locator('#cookie.is-open').count() === 1);
  await p.click('#cookie [data-consent="notwendig"]'); await p.waitForTimeout(700);
  ok('Ablehnen schließt und speichert', await p.evaluate(() => !document.getElementById('cookie').classList.contains('is-open') && localStorage.getItem('wiba-consent-v1') === 'notwendig'));
  await p.reload(); await p.waitForTimeout(3000); ok('Banner nach Reload nicht mehr da', await p.locator('#cookie.is-open').count() === 0);
  await p.click('.menu-btn'); await p.waitForTimeout(900);
  ok('Menü öffnet (Vorhang sichtbar)', await p.evaluate(() => { const a = document.querySelector('.vorhang nav a'); const rr = a.getBoundingClientRect(); const el = document.elementFromPoint(rr.left + 5, rr.top + rr.height / 2); return document.body.classList.contains('menu-open') && !!el && !!el.closest('.vorhang'); }));
  await p.keyboard.press('Tab'); await p.keyboard.press('Tab'); await p.keyboard.press('Tab');
  ok('Tab bleibt im offenen Menü', await p.evaluate(() => !!document.activeElement.closest('.vorhang, .site-header')));
  await p.keyboard.press('Escape'); await p.waitForTimeout(900); ok('Menü schließt mit Escape', await p.evaluate(() => !document.body.classList.contains('menu-open')));
  const zoomEnde = await p.evaluate(() => { const z = document.querySelector('.zoom'); return z.offsetTop + z.offsetHeight; });
  await p.evaluate(y => scrollTo(0, y), zoomEnde); await p.waitForTimeout(700);
  ok('Kontaktleiste nach dem Intro sichtbar', await p.locator('.kontaktleiste.is-visible').count() === 1);
  ok('Kontaktleiste: vollständige Telefonnummer', await p.evaluate(() => document.querySelector('.kontaktleiste .anrufen').href === 'tel:+491604151974'));
  ok('Scroll-up in der Kontaktleiste sichtbar', await p.locator('.kontaktleiste.is-visible .leiste-hoch').count() === 1);
  await p.click('.leiste-hoch'); await p.waitForTimeout(2200); ok('Scroll-up bringt nach oben', await p.evaluate(() => scrollY < 5));
  // Auftragszettel
  await p.evaluate(() => document.querySelector('#auftrag .drucker').scrollIntoView({ block: 'center' })); await p.waitForTimeout(2200);
  ok('Zettel gedruckt', await p.evaluate(() => document.querySelector('.drucker').classList.contains('los')));
  await p.click('#auftrag input[value="Klimaservice"]'); await p.waitForTimeout(100);
  await p.click('#auftrag .z-option input >> nth=1'); await p.waitForTimeout(1400);
  ok('Zettel: Klima + Desinfektion = 150,00 €', (await p.textContent('#auftrag output')).trim() === '150,00 €');
  ok('Zettel: E-Mail enthält Leistung', decodeURIComponent(await p.getAttribute('#auftrag .z-mail', 'href')).includes('Klimaservice (Befüllen + Desinfektion), 150,00 €'));
  await p.click('#auftrag input[value="Aufbereitung"]'); await p.waitForTimeout(300);
  ok('Zettel: Aufbereitung = Auf Anfrage', (await p.textContent('#auftrag output')).trim() === 'Auf Anfrage');
  // Vorher/Nachher
  await p.evaluate(() => document.querySelector('.vn').scrollIntoView({ block: 'center' })); await p.waitForTimeout(3600);
  await p.focus('.vn input'); await p.keyboard.press('End'); await p.waitForTimeout(100);
  ok('Regler per Tastatur (End = 100 %)', await p.evaluate(() => document.querySelector('.vn').style.getPropertyValue('--x') === '100%'));
  await p.click('.reiter button >> nth=2'); ok('Reiter wechselt Bild', (await p.getAttribute('.vn .nach', 'src')).includes('vn-04-nachher'));
  // Horizontale Galerie
  ok('Galerie läuft seitwärts', await p.evaluate(async () => { const q = document.querySelector('.quer'); scrollTo(0, q.offsetTop + (q.offsetHeight - innerHeight) * .7); await new Promise(r => setTimeout(r, 400)); return /translate3d\(-\d/.test(document.querySelector('.spur').style.transform); }));
  // Lightbox
  await p.goto(BASE + 'kunden/'); await p.waitForTimeout(1200);
  await p.click('.galerie button >> nth=0'); await p.waitForTimeout(500);
  ok('Lightbox öffnet', await p.evaluate(() => document.getElementById('lightbox').open));
  const s1 = await p.getAttribute('#lightbox .lb-bild img', 'src');
  await p.click('.lb-weiter'); await p.waitForTimeout(300);
  ok('Lightbox: weiter', (await p.getAttribute('#lightbox .lb-bild img', 'src')) !== s1);
  await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(300);
  ok('Lightbox: Pfeiltaste zurück', (await p.getAttribute('#lightbox .lb-bild img', 'src')) === s1);
  await p.keyboard.press('Escape'); await p.waitForTimeout(300); ok('Lightbox: Escape schließt', await p.evaluate(() => !document.getElementById('lightbox').open));
  // Formular und Karte
  await p.goto(BASE + 'kontakt/?thema=Klimaservice'); await p.waitForTimeout(1000);
  await p.goto(BASE + 'felgenservice/'); await p.waitForTimeout(800);
  await p.evaluate(() => document.querySelector('.video').scrollIntoView({ block: 'center' })); await p.waitForTimeout(1200);
  await p.click('.video-play'); await p.waitForTimeout(400);
  ok('Video: Play-Knopf startet und zeigt Steuerung', await p.evaluate(() => { const v = document.querySelector('.video video'); return v.controls && document.querySelector('.video').classList.contains('laeuft'); }));
  await p.goto(BASE + 'kontakt/?thema=Klimaservice'); await p.waitForTimeout(1000);
  ok('Formular: Thema aus URL vorbelegt', (await p.inputValue('#f-thema')) === 'Klimaservice');
  await p.click('#anfrage-form button[type=submit]'); await p.waitForTimeout(200);
  ok('Formular: Pflichtfelder geprüft', (await p.textContent('.form-status')).trim() === '');
  await p.fill('#f-name', 'Test'); await p.fill('#f-text', 'Testnachricht');
  await p.click('#anfrage-form button[type=submit]'); await p.waitForTimeout(400);
  ok('Formular: Hinweis nach Absenden', (await p.textContent('.form-status')).includes('E-Mail-Programm'));
  ok('Karte erst nach Klick (vorher kein iframe)', await p.locator('.karte iframe').count() === 0);
  await p.click('[data-karte-laden]'); await p.waitForTimeout(500);
  ok('Karte lädt nach Klick', await p.locator('.karte iframe').count() === 1);
  ok('Keine JS-Fehler (mobil)', errs.length === 0);
  await c.close();
  // Desktop
  c = await b.newContext({ viewport: { width: 1440, height: 900 } }); p = await c.newPage(); const errs2 = []; p.on('pageerror', e => errs2.push(e.message));
  await c.addInitScript(() => { try { localStorage.setItem('wiba-consent-v1', 'notwendig'); } catch (e) {} });
  await p.goto(BASE + 'reifenservice/'); await p.waitForTimeout(1200);
  ok('Desktop: Navigation und Menü-Knopf sichtbar', await p.evaluate(() => getComputedStyle(document.querySelector('.nav-desk')).display === 'flex' && getComputedStyle(document.querySelector('.menu-btn')).display !== 'none'));
  ok('Desktop: aktuelle Seite markiert', (await p.getAttribute('.nav-desk a[aria-current=page]', 'href')) === '../reifenservice/');
  await p.click('.fab-toggle'); await p.waitForTimeout(500);
  ok('Desktop: Kontakt-Button klappt auf', await p.locator('#fab.is-open').count() === 1);
  await p.keyboard.press('Escape'); ok('Desktop: Escape schließt Kontakt-Button', await p.locator('#fab.is-open').count() === 0);
  await p.evaluate(() => document.getElementById('preise').scrollIntoView()); await p.waitForTimeout(1800);
  ok('Desktop: Preise zählen hoch (12,50 €)', (await p.textContent('#preise .p-zeile b')).trim() === '12,50 €');
  ok('Keine JS-Fehler (Desktop)', errs2.length === 0);
  await c.close();
  // Bewegung reduziert
  c = await b.newContext({ ...devices['iPhone 13'], reducedMotion: 'reduce' }); p = await c.newPage();
  await p.goto(BASE); await p.waitForTimeout(800);
  ok('Reduziert: Claim sofort sichtbar', await p.evaluate(() => getComputedStyle(document.querySelector('.zoom-claim')).opacity === '1'));
  ok('Reduziert: Maske ausgeblendet', await p.evaluate(() => getComputedStyle(document.querySelector('.zoom-maske')).display === 'none'));
  await c.close();
  console.log(r.join('\n')); await b.close();
})();
