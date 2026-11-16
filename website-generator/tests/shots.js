// node website-generator/tests/shots.js [ausgabeordner] [seite ...]  -> Abschnitts-Screenshots mobil (390) und Desktop (1440), Fehler, Überlauf (390/320/1440)
// Server: python3 -m http.server 8090 --directory website
const { chromium, devices } = require('playwright-core');
const BASE = process.env.BASE || 'http://localhost:8090/';
const out = process.argv[2] || 'test-ergebnisse';
require('fs').mkdirSync(out, { recursive: true });
const seiten = process.argv.length > 3 ? process.argv.slice(3).map(s => s === 'start' ? '' : s) : require('./seiten.js');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const profile = {
    m: { ...devices['iPhone 13'], deviceScaleFactor: 1 },
    s: { ...devices['iPhone SE'], viewport: { width: 320, height: 640 }, deviceScaleFactor: 1 },
    d: { viewport: { width: 1440, height: 900 } },
  };
  const fehler = [];
  for (const s of seiten) {
    for (const [name, prof] of Object.entries(profile)) {
      const ctx = await browser.newContext(prof);
      await ctx.addInitScript(() => { try { localStorage.setItem('wiba-consent-v1', 'notwendig'); } catch (e) {} });
      const p = await ctx.newPage();
      p.on('console', m => { if (m.type() === 'error') fehler.push(`${s || 'start'} [${name}] Konsole: ${m.text()}`); });
      p.on('pageerror', e => fehler.push(`${s || 'start'} [${name}] JS: ${e.message}`));
      p.on('response', r => { if (r.status() >= 400 && !(s === '404.html' && r.url().endsWith('404.html'))) fehler.push(`${s || 'start'} [${name}] ${r.status()} ${r.url()}`); });
      await p.goto(BASE + s, { waitUntil: 'load' });
      await p.waitForTimeout(1500);
      const H = await p.evaluate(() => document.documentElement.scrollHeight);
      const vh = prof.viewport.height;
      let i = 0;
      for (let y = 0; y < H; y += vh) {
        await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(name === 's' ? 250 : 900);
        if (name !== 's') await p.screenshot({ path: `${out}/${name}-${(s || 'start').replace(/[\/.]/g, '_')}-${String(i++).padStart(2, '0')}.png` });
      }
      const ov = await p.evaluate(w => document.documentElement.scrollWidth - w, prof.viewport.width);
      if (ov > 0) {
        const wer = await p.evaluate(w => [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.right > w + 1 && getComputedStyle(e).position !== 'fixed' && !e.closest('.spur,.zoom,.stimmen'); }).slice(0, 4).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().right)), prof.viewport.width);
        fehler.push(`${s || 'start'} [${name}] horizontaler Überlauf ${ov}px: ${wer.join(', ')}`);
      }
      await ctx.close();
    }
  }
  console.log(fehler.length ? fehler.join('\n') : 'keine Fehler');
  await browser.close();
})();
