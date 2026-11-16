// node small.js -> alle Seiten bei 320px auf Überlauf, dazu Tastatur: Fokus sichtbar
const { chromium, devices } = require('playwright-core');
const BASE = process.env.BASE || 'http://localhost:8090/';
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const c = await b.newContext({ ...devices['iPhone SE'], viewport: { width: 320, height: 640 } });
  const p = await c.newPage(); const out = [];
  for (const s of require('./seiten.js')) {
    await p.goto(BASE + s); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1200);
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - 320);
    const fokus = await p.evaluate(() => { const a = document.querySelector('main a, main button'); if (!a) return true; a.focus(); return getComputedStyle(a).outlineStyle !== 'none'; });
    out.push(`${(s || 'start').padEnd(24)} Überlauf ${ov}px  Fokus sichtbar ${fokus ? 'ja' : 'NEIN'}`);
  }
  console.log(out.join('\n')); await b.close();
})();
