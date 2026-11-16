// Rendert alle Seiten von wibaperformance.de (Wix) mit Playwright und dem System-Chrome.
// Aufruf (im Projektordner, nach npm install): node _raw/scripts/render-crawl.js .
// Ergebnis: _raw/html/ (rohes SSR-HTML), _raw/html-rendered/ (gerendertes DOM),
//           _raw/crawl-render.json (Seiten, Bilder, Links, Schriften, Mobil-Befunde),
//           screenshots-alte-seite/ (Desktop 1440 + Mobil 390)
const { chromium, devices } = require('playwright-core');
const fs = require('fs'), path = require('path');
const OUT = process.argv[2];
const HOST = 'www.wibaperformance.de';
const START = [
  '/', '/services', '/dienstleistungen-1', '/dienstleistungen-2', '/dienstleistungen-3', '/produkte',
  '/customer-name', '/über-uns', '/kontakt', '/agb', '/gewinnspiel-jetzt-mitmachen',
].map(p => 'https://' + HOST + encodeURI(p));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const slug = u => { const p = decodeURIComponent(new URL(u).pathname).replace(/^\/|\/$/g, ''); return (p || 'index').replace(/[\/]/g, '__'); };

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const desk = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'de-DE' });
  const mob = await browser.newContext({ ...devices['iPhone 13'], deviceScaleFactor: 1, locale: 'de-DE' });
  for (const d of ['html', 'html-rendered']) fs.mkdirSync(path.join(OUT, '_raw', d), { recursive: true });
  fs.mkdirSync(path.join(OUT, 'screenshots-alte-seite'), { recursive: true });
  const queue = [...START], seen = new Set(), pages = [], images = new Map(), external = new Set(), fonts = new Set(), css = new Set();
  const addImg = (u, page, how, alt) => {
    if (!u || u.startsWith('data:')) return;
    const i = images.get(u) || { url: u, found_on: [], how: [], alts: [] };
    if (!i.found_on.includes(page)) i.found_on.push(page);
    if (!i.how.includes(how)) i.how.push(how);
    if (alt && !i.alts.includes(alt)) i.alts.push(alt);
    images.set(u, i);
  };
  const scrollAll = async page => page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 150)); }
    window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 500));
  });

  while (queue.length) {
    const url = queue.shift();
    const key = decodeURI(url).replace(/\/$/, '');
    if (seen.has(key)) continue; seen.add(key);
    const page = await desk.newPage();
    page.on('response', r => {
      const u = r.url(), t = r.headers()['content-type'] || '';
      if (/static\.wixstatic\.com\/media\//.test(u) || t.startsWith('image/')) addImg(u, key, 'network');
      if (/\.(woff2?|ttf|otf)(\?|$)/.test(u) || t.includes('font')) fonts.add(u);
      if (t.includes('text/css')) css.add(u);
    });
    let resp;
    try { resp = await page.goto(url, { waitUntil: 'load', timeout: 60000 }); } catch (e) { console.log('ERR', url, e.message); await page.close(); continue; }
    const status = resp ? resp.status() : 0;
    const final = page.url();
    const name = slug(final);
    if (resp) { try { fs.writeFileSync(path.join(OUT, '_raw/html', name + '.html'), await resp.text()); } catch (e) {} }
    await scrollAll(page); await page.waitForTimeout(1500);
    fs.writeFileSync(path.join(OUT, '_raw/html-rendered', name + '.html'), await page.content());
    const info = await page.evaluate(() => {
      const r = { imgs: [], bgs: [], links: [], meta: {}, title: document.title, h: [], fontsUsed: {} };
      document.querySelectorAll('img').forEach(i => r.imgs.push({ src: i.currentSrc || i.src, srcset: i.getAttribute('srcset'), alt: i.alt, w: i.naturalWidth, h: i.naturalHeight }));
      document.querySelectorAll('*').forEach(e => {
        const b = getComputedStyle(e).backgroundImage; if (b && b.includes('url(')) (b.match(/url\(["']?([^"')]+)/g) || []).forEach(m => r.bgs.push(m.replace(/url\(["']?/, '')));
      });
      document.querySelectorAll('a[href]').forEach(a => r.links.push({ href: a.href, text: a.innerText.trim().slice(0, 80) }));
      document.querySelectorAll('meta').forEach(m => { const k = m.getAttribute('name') || m.getAttribute('property'); if (k) r.meta[k] = m.content; });
      document.querySelectorAll('link[rel*=icon]').forEach(l => r.imgs.push({ src: l.href, alt: 'icon' }));
      document.querySelectorAll('h1,h2,h3,h4,h5,h6').forEach(h => r.h.push(h.tagName + ': ' + h.innerText.trim().slice(0, 100)));
      document.querySelectorAll('h1,h2,h3,p,span,a,li').forEach(e => { if (!e.innerText || !e.innerText.trim()) return; const s = getComputedStyle(e); const k = s.fontFamily.split(',')[0] + ' | ' + s.fontWeight; r.fontsUsed[k] = (r.fontsUsed[k] || 0) + 1; });
      return r;
    });
    info.imgs.forEach(i => { addImg(i.src, key, 'img', i.alt); if (i.srcset) i.srcset.split(',').forEach(s => addImg(s.trim().split(' ')[0], key, 'srcset', i.alt)); });
    info.bgs.forEach(b => addImg(b, key, 'background'));
    if (info.meta['og:image']) addImg(info.meta['og:image'], key, 'og:image');
    const missingAlt = info.imgs.filter(i => i.alt !== 'icon' && !i.alt).length;
    for (const l of info.links) {
      let u; try { u = new URL(l.href); } catch (e) { continue; }
      if (!/^https?:$/.test(u.protocol)) continue;
      if (u.hostname.replace(/^www\./, '') === 'wibaperformance.de') {
        u.hash = ''; u.search = '';
        const k = decodeURI(u.href).replace(/\/$/, '');
        if (!seen.has(k) && !/\.(jpg|png|pdf)$/i.test(u.pathname)) queue.push(u.href);
      } else external.add(l.href + ' | ' + l.text);
    }
    await page.screenshot({ path: path.join(OUT, 'screenshots-alte-seite', 'desktop-' + name + '.png'), fullPage: true });
    await page.close();

    // Mobil
    const mp = await mob.newPage();
    await mp.goto(final, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
    await scrollAll(mp); await mp.waitForTimeout(1500);
    const mobileFindings = await mp.evaluate(() => {
      const f = { overflow: document.documentElement.scrollWidth - window.innerWidth, smallTargets: [], clipped: [] };
      document.querySelectorAll('a,button,[role=button]').forEach(e => {
        const r = e.getBoundingClientRect(); if (r.width === 0 || r.height === 0) return;
        if (r.height < 32 || r.width < 32) f.smallTargets.push(`${Math.round(r.width)}x${Math.round(r.height)} ${(e.innerText || e.getAttribute('aria-label') || '').trim().slice(0, 40)}`);
      });
      document.querySelectorAll('p,span,h1,h2,h3,h4').forEach(e => {
        if (e.children.length) return; const r = e.getBoundingClientRect();
        if (r.width && (r.right > window.innerWidth + 2 || r.left < -2)) f.clipped.push(e.innerText.trim().slice(0, 60));
        if (e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).overflow !== 'visible') f.clipped.push('[abgeschnitten] ' + e.innerText.trim().slice(0, 60));
      });
      return f;
    });
    await mp.screenshot({ path: path.join(OUT, 'screenshots-alte-seite', 'mobil-' + name + '.png'), fullPage: true });
    await mp.close();
    pages.push({ url: url, final, status, name, title: info.title, meta: info.meta, headings: info.h, missingAlt, imgCount: info.imgs.length, fontsUsed: info.fontsUsed, mobile: mobileFindings });
    console.log('PAGE', status, decodeURI(final), 'imgs', info.imgs.length);
    await sleep(300);
  }
  fs.writeFileSync(path.join(OUT, '_raw/crawl-render.json'), JSON.stringify({ pages, images: [...images.values()], external_links: [...external].sort(), fonts: [...fonts], css: [...css] }, null, 2));
  console.log(pages.length, 'Seiten', images.size, 'Bild-URLs', fonts.size, 'Schriften');
  await browser.close();
})();
