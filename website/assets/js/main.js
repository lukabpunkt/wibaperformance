/* WIBA Performance – Interaktionen
   Menü, Kopf, Cookie-Banner, Schnellkontakt, Scroll-up, Einblenden, Wort-Reveal, Zähler,
   Zoom-Intro, Fülltext, horizontale Galerie, Parallaxe, Bewertungen, Auftragszettel,
   Vorher-Nachher-Regler, Lightbox, Karte nach Einwilligung, Anfrageformular, Cursor */
(function () {
  'use strict';
  const root = document.documentElement;
  root.classList.remove('no-js'); root.classList.add('js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => [...(c || document).querySelectorAll(s)];
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  const CONSENT = 'wiba-consent-v1';
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const map = (v, a, b) => clamp((v - a) / (b - a));
  const progress = el => { const r = el.getBoundingClientRect(), t = r.height - innerHeight; return t <= 0 ? (r.top < 0 ? 1 : 0) : clamp(-r.top / t); };
  const euro = (v, d = 2) => v.toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d }) + ' €';

  /* rAF-gedrosselte Scroll-Callbacks */
  const onScrollFns = [];
  let tick = false;
  const runScroll = () => { onScrollFns.forEach(f => f()); tick = false; };
  addEventListener('scroll', () => { if (!tick) { tick = true; requestAnimationFrame(runScroll); } }, { passive: true });
  const onScroll = fn => { onScrollFns.push(fn); fn(); };

  /* ---------- Menü ---------- */
  const menuBtn = $('.menu-btn');
  if (menuBtn) {
    const label = menuBtn.querySelector('span');
    const rest = [...document.body.children].filter(el => !el.matches('.site-header, .vorhang, script, .skip'));
    const setMenu = open => {
      document.body.classList.toggle('menu-open', open);
      rest.forEach(el => { if (open) el.setAttribute('inert', ''); else el.removeAttribute('inert'); });
      if (open) { const a = $('.vorhang nav a'); if (a) setTimeout(() => a.focus({ preventScroll: true }), 80); }
      menuBtn.setAttribute('aria-expanded', String(open));
      if (label) label.textContent = open ? 'Schließen' : 'Menü';
    };
    menuBtn.addEventListener('click', () => setMenu(!document.body.classList.contains('menu-open')));
    $$('.vorhang a').forEach(a => a.addEventListener('click', () => setMenu(false)));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && document.body.classList.contains('menu-open')) { setMenu(false); menuBtn.focus(); } });
  }

  /* ---------- Kopf, Scroll-up, Kontaktleiste ---------- */
  const kopf = $('.site-header'), toTop = $('#toTop'), leiste = $('.kontaktleiste');
  const startSeite = !!$('.zoom');
  let lastY = scrollY;
  onScroll(() => {
    const y = scrollY;
    if (kopf) {
      kopf.classList.toggle('is-solid', y > 40);
      if (!document.body.classList.contains('menu-open')) kopf.classList.toggle('is-weg', y > lastY + 2 && y > 500);
      if (y < lastY - 2) kopf.classList.remove('is-weg');
    }
    lastY = y;
    const zz = startSeite ? $('.zoom') : null;
    const nachIntro = zz ? zz.offsetTop + zz.offsetHeight - innerHeight * .4 : 0;
    if (toTop) toTop.classList.toggle('is-visible', y > Math.max(innerHeight * 1.2, nachIntro));
    if (leiste) leiste.classList.toggle('is-visible', y > (startSeite ? nachIntro : 160));
  });
  [toTop, ...$$('[data-nach-oben]')].filter(Boolean).forEach(btn => btn.addEventListener('click', () => {
    scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
    const skip = $('.skip'); if (skip) skip.focus({ preventScroll: true });
  }));

  /* ---------- Kontakt-Button (Desktop) ---------- */
  const fab = $('#fab');
  if (fab) {
    const t = $('.fab-toggle', fab);
    const set = open => { fab.classList.toggle('is-open', open); t.setAttribute('aria-expanded', String(open)); };
    t.addEventListener('click', e => { e.stopPropagation(); set(!fab.classList.contains('is-open')); });
    document.addEventListener('click', e => { if (!fab.contains(e.target)) set(false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && fab.classList.contains('is-open')) { set(false); t.focus(); } });
  }

  /* ---------- Cookie-Banner ---------- */
  const cookie = $('#cookie');
  const consentFns = [];
  const consent = () => store.get(CONSENT);
  if (cookie) {
    const open = () => { cookie.classList.add('is-open'); const b = $('button', cookie); if (b) setTimeout(() => b.focus({ preventScroll: true }), 60); };
    if (!consent()) setTimeout(() => cookie.classList.add('is-open'), startSeite ? 2600 : 1200);
    $$('[data-consent]', cookie).forEach(b => b.addEventListener('click', () => {
      store.set(CONSENT, b.dataset.consent); cookie.classList.remove('is-open');
      consentFns.forEach(fn => fn(b.dataset.consent));
    }));
    $$('[data-cookie-settings]').forEach(b => b.addEventListener('click', open));
  }

  /* ---------- Wort-Reveal und Einblenden ---------- */
  $$('[data-split]').forEach(el => {
    const text = el.textContent.trim();
    el.setAttribute('aria-label', text);
    el.innerHTML = text.split(/\s+/).map((w, i) => `<span class="w" aria-hidden="true"><span class="wi" style="--i:${i}">${w}</span></span>`).join(' ');
  });
  const reveal = $$('[data-reveal], [data-split]:not([data-split="manual"])');
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(en => en.forEach(x => { if (x.isIntersecting) { x.target.classList.add('is-in'); io.unobserve(x.target); } }), { threshold: .14, rootMargin: '0px 0px -30px 0px' });
    reveal.forEach(el => io.observe(el));
  } else reveal.forEach(el => el.classList.add('is-in'));

  /* ---------- Zähler ---------- */
  const zaehle = (el, from, to, d, prefix) => {
    if (reduce) { el.textContent = prefix + euro(to, d); return; }
    const t0 = performance.now(), dur = 1100;
    const step = t => { const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 4); el.textContent = prefix + euro(from + (to - from) * e, d); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  };
  const counters = $$('[data-count]');
  if ('IntersectionObserver' in window && counters.length && !reduce) {
    const io = new IntersectionObserver(en => en.forEach(x => { if (x.isIntersecting) { const el = x.target; zaehle(el, 0, parseFloat(el.dataset.count), 2, el.dataset.prefix || ''); io.unobserve(el); } }), { threshold: .7 });
    counters.forEach(c => io.observe(c));
  }

  /* ---------- Startseite: Zoom durch „WIBA“ ---------- */
  const zoom = $('.zoom');
  if (zoom) {
    const buehne = $('.zoom-buehne', zoom), svg = $('.zoom-maske', zoom), txt = $('.maske-text', zoom);
    const rects = $$('rect', svg), rahmen = $('.zoom-rahmen', zoom), img = $('.zoom-bild', zoom);
    const schleier = $('.zoom-schleier', zoom), claim = $('.zoom-claim', zoom), vorn = $('.zoom-vorn', zoom);
    let sMax = 30, W = 0, H = 0;
    const layout = () => {
      W = buehne.clientWidth; H = buehne.clientHeight;
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
      rects.forEach(r => { r.setAttribute('width', W); r.setAttribute('height', H); });
      txt.setAttribute('font-size', 100); txt.setAttribute('x', W / 2); txt.setAttribute('y', H / 2);
      const len = txt.getComputedTextLength() || 260;
      const fs = Math.min(100 * (W * .9) / len, H * .46, 560);
      txt.setAttribute('font-size', fs.toFixed(1));
      txt.setAttribute('y', (H * .47 + fs * .36).toFixed(1));
      let ex; try { ex = txt.getExtentOfChar(1); } catch (e) { ex = null; }
      if (ex && ex.width) {
        svg.style.transformOrigin = `${ex.x + ex.width / 2}px ${ex.y + ex.height * .55}px`;
        sMax = Math.hypot(W, H) / (ex.width * .38);
      }
    };
    const update = () => {
      const p = progress(zoom);
      const z = map(p, 0, .6);
      svg.style.transform = `scale(${1 + (sMax - 1) * z * z * z})`;
      svg.style.opacity = 1 - map(p, .5, .6);
      rahmen.style.transform = `scale(${1.08 - .08 * map(p, 0, .9)})`;
      vorn.style.opacity = 1 - map(p, 0, .1);
      schleier.style.opacity = map(p, .55, .8);
      const c = map(p, .66, .86);
      claim.style.opacity = c; claim.style.transform = `translateY(${(1 - c) * 40}px)`;
      claim.style.pointerEvents = c > .6 ? 'auto' : 'none';
    };
    if (reduce) { zoom.classList.add('bereit'); }
    else {
      let gestartet = false;
      const start = () => { if (gestartet) return; gestartet = true; layout(); update(); requestAnimationFrame(() => zoom.classList.add('bereit')); onScroll(update); };
      const bild = img.decode ? img.decode().catch(() => {}) : Promise.resolve();
      const schrift = document.fonts && document.fonts.load ? document.fonts.load('900 100px "Hanken Grotesk"').catch(() => {}) : Promise.resolve();
      Promise.all([bild, schrift]).then(start);
      setTimeout(start, 3500);
      let lastW = innerWidth, lastH = innerHeight;
      addEventListener('resize', () => {
        if (Math.abs(innerWidth - lastW) < 2 && Math.abs(innerHeight - lastH) < 140) return;
        lastW = innerWidth; lastH = innerHeight; layout(); update();
      });
    }
  }

  /* ---------- Text füllt sich Wort für Wort ---------- */
  $$('.fuell').forEach(f => {
    f.innerHTML = f.textContent.trim().split(/\s+/).map(w => `<span class="fw">${w}</span>`).join(' ');
    const fw = $$('.fw', f);
    if (reduce) { fw.forEach(w => w.classList.add('an')); return; }
    onScroll(() => {
      const r = f.getBoundingClientRect();
      const p = map(innerHeight * .85 - r.top, 0, r.height + innerHeight * .35);
      const n = Math.round(p * fw.length);
      fw.forEach((w, i) => w.classList.toggle('an', i < n));
    });
  });

  /* ---------- Horizontale Galerie ---------- */
  $$('.quer').forEach(quer => {
    if (reduce) return;
    const spur = $('.spur', quer), balken = $('.balken i', quer), zaehler = $('.zaehler', quer), figs = spur.children;
    const hoehe = () => { quer.style.height = (innerHeight + Math.max(0, spur.scrollWidth - innerWidth)) + 'px'; };
    hoehe(); addEventListener('load', hoehe); addEventListener('resize', hoehe);
    onScroll(() => {
      const r = quer.getBoundingClientRect();
      if (r.bottom < -100 || r.top > innerHeight + 100) return;
      const p = progress(quer), extra = Math.max(0, spur.scrollWidth - innerWidth);
      spur.style.transform = `translate3d(${-p * extra}px,0,0)`;
      if (balken) balken.style.width = p * 100 + '%';
      if (zaehler) zaehler.textContent = `${Math.min(figs.length, Math.floor(p * (figs.length - 1) + 1.0001))} / ${figs.length}`;
      for (const f of figs) { const b = f.getBoundingClientRect(); f.querySelector('img').style.transform = `scale(1.12) translate3d(${(b.left + b.width / 2 - innerWidth / 2) / innerWidth * -28}px,0,0)`; }
    });
  });

  /* ---------- Parallaxe in Spalten ---------- */
  const spalten = $$('.mosaik .sp');
  if (spalten.length && !reduce) onScroll(() => spalten.forEach(s => {
    const r = s.parentElement.getBoundingClientRect();
    if (r.bottom < 0 || r.top > innerHeight) return;
    s.style.transform = `translate3d(0,${(r.top - innerHeight / 2) * +s.dataset.speed}px,0)`;
  }));

  /* ---------- Bewertungen wischen ---------- */
  $$('.wisch').forEach(w => {
    const liste = w.previousElementSibling;
    $$('button', w).forEach(b => b.addEventListener('click', () => liste.scrollBy({ left: +b.dataset.dir * (liste.firstElementChild.offsetWidth + 14), behavior: reduce ? 'auto' : 'smooth' })));
  });

  /* ---------- Auftragszettel ---------- */
  const daten = $('#preisdaten');
  $$('.drucker').forEach(dr => {
    if (!daten) return;
    const L = JSON.parse(daten.textContent);
    const form = $('form', dr), lg = $('.z-leistung', dr), og = $('.z-option', dr), legend = $('.z-option-titel', dr);
    const titel = $('.z-titel', dr), info = $('.z-info', dr), out = $('output', dr), mail = $('.z-mail', dr);
    const uid = 'z' + Math.random().toString(36).slice(2, 7);
    const chip = (name, val, checked) => `<label><input type="radio" name="${uid}-${name}" value="${val}"${checked ? ' checked' : ''}><span>${val}</span></label>`;
    const start = dr.dataset.start && L.find(l => l.name === dr.dataset.start) ? dr.dataset.start : L[0].name;
    lg.innerHTML = L.map(l => chip('l', l.name, l.name === start)).join('');
    let letzter = null;
    const render = (anim) => {
      const l = L.find(x => x.name === $(`[name="${uid}-l"]:checked`, form).value);
      const sel = $(`[name="${uid}-o"]:checked`, form);
      const cur = sel && l.optionen.find(o => o[0] === sel.value) ? sel.value : l.optionen[0][0];
      legend.textContent = l.frage;
      og.innerHTML = l.optionen.map(o => chip('o', o[0], o[0] === cur)).join('');
      const o = l.optionen.find(x => x[0] === cur), wert = o[1], ab = o[2] ? 'ab ' : '';
      titel.textContent = l.name + ' · ' + o[0]; info.textContent = l.info;
      if (typeof wert === 'number') {
        if (anim && letzter !== null) zaehle(out, letzter, wert, 2, ab); else out.textContent = ab + euro(wert);
        letzter = wert;
      } else { out.textContent = wert; letzter = null; }
      out.classList.toggle('text', typeof wert !== 'number');
      const hw = $('.z-hinweis', dr);
      if (hw) hw.textContent = typeof wert === 'number' ? 'Festpreis laut Preisliste, inklusive MwSt. Termine nach Vereinbarung.' : 'Der Preis richtet sich nach Fahrzeug und Aufwand. Wir melden uns mit einem Angebot.';
      const preis = typeof wert === 'number' ? ab + euro(wert) : 'Preis auf Anfrage';
      const body = `Hallo WIBA Performance,\n\nich interessiere mich für: ${l.name} (${o[0]}), ${preis}.\n\nFahrzeug (Marke, Modell):\nReifen-/Felgengröße:\nWunschtermin:\nRückrufnummer:\n\nViele Grüße`;
      mail.href = 'mailto:' + dr.dataset.mail + '?subject=' + encodeURIComponent('Anfrage: ' + l.name + ' (' + o[0] + ')') + '&body=' + encodeURIComponent(body);
    };
    form.addEventListener('change', () => { render(true); const z = $('.zettel', dr); z.classList.remove('neu'); void z.offsetWidth; z.classList.add('neu'); });
    form.addEventListener('submit', e => e.preventDefault());
    $('.zettel', dr).addEventListener('animationend', e => { if (e.animationName === 'druck') e.target.classList.add('fertig'); });
    render(false);
    if (reduce || !('IntersectionObserver' in window)) { dr.classList.add('los'); $('.zettel', dr).classList.add('fertig'); }
    else new IntersectionObserver((en, o) => { if (en[0].isIntersecting) { dr.classList.add('los'); o.disconnect(); } }, { threshold: .3 }).observe(dr);
  });

  /* ---------- Vorher / Nachher ---------- */
  $$('.vn-modul').forEach(m => {
    const vn = $('.vn', m), r = $('input', vn), vor = $('.vor', vn), nach = $('.nach', vn);
    const setX = v => vn.style.setProperty('--x', v + '%');
    r.addEventListener('input', () => setX(r.value));
    const demo = () => {
      if (reduce) return;
      const k = [50, 14, 86, 50], t0 = performance.now(), dur = 2600;
      const step = t => {
        const p = Math.min(1, (t - t0) / dur), s = p * 3, i = Math.min(2, Math.floor(s)), f = s - i;
        const e = f < .5 ? 2 * f * f : 1 - Math.pow(-2 * f + 2, 2) / 2, v = k[i] + (k[i + 1] - k[i]) * e;
        setX(v); r.value = Math.round(v); if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    $$('.reiter button', m).forEach(b => b.addEventListener('click', () => {
      $$('.reiter button', m).forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      vor.src = b.dataset.vor; nach.src = b.dataset.nach; vor.alt = 'Vorher: ' + b.textContent; nach.alt = 'Nachher: ' + b.textContent;
      if (vor.srcset) { vor.removeAttribute('srcset'); nach.removeAttribute('srcset'); }
      demo();
    }));
    if ('IntersectionObserver' in window) new IntersectionObserver((en, o) => { if (en[0].isIntersecting) { setTimeout(demo, 500); o.disconnect(); } }, { threshold: .5 }).observe(vn);
  });

  /* ---------- Lightbox ---------- */
  const lb = $('#lightbox');
  if (lb && typeof lb.showModal === 'function') {
    const img = $('.lb-bild img', lb), count = $('.lb-zahl', lb);
    let btns = [], i = 0, opener = null;
    const show = n => {
      i = (n + btns.length) % btns.length;
      const b = btns[i], t = $('img', b);
      img.src = b.dataset.full; img.alt = t.alt;
      count.textContent = (i + 1) + ' von ' + btns.length;
      img.style.animation = 'none'; void img.offsetWidth; img.style.animation = '';
    };
    $$('.galerie button').forEach(b => b.addEventListener('click', () => {
      btns = $$('button', b.closest('.galerie')); opener = b; show(btns.indexOf(b)); lb.showModal();
    }));
    $('.lb-zu', lb).addEventListener('click', () => lb.close());
    $('.lb-zurueck', lb).addEventListener('click', () => show(i - 1));
    $('.lb-weiter', lb).addEventListener('click', () => show(i + 1));
    lb.addEventListener('click', e => { if (e.target === lb || e.target.classList.contains('lb-bild')) lb.close(); });
    lb.addEventListener('keydown', e => { if (e.key === 'ArrowLeft') show(i - 1); if (e.key === 'ArrowRight') show(i + 1); });
    lb.addEventListener('close', () => { img.removeAttribute('src'); if (opener) opener.focus(); });
    let x0 = null;
    lb.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', e => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1)); x0 = null; });
  }

  /* ---------- Karte erst nach Einwilligung ---------- */
  const karte = $('.karte');
  if (karte) {
    const laden = () => {
      if (karte.classList.contains('is-loaded')) return;
      karte.innerHTML = `<iframe title="Karte: Hackelbarg 7, 32369 Rahden" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="${karte.dataset.src}"></iframe>`;
      karte.classList.add('is-loaded');
    };
    if (consent() === 'alle') laden();
    consentFns.push(v => { if (v === 'alle') laden(); });
    const b = $('[data-karte-laden]', karte);
    if (b) b.addEventListener('click', () => { store.set(CONSENT, 'alle'); if (cookie) cookie.classList.remove('is-open'); laden(); });
  }

  /* ---------- Anfrageformular: öffnet das E-Mail-Programm ---------- */
  const anfrage = $('#anfrage-form');
  if (anfrage) {
    const params = new URLSearchParams(location.search);
    const thema = params.get('thema'); const sel = $('select[name=thema]', anfrage);
    if (thema && sel && [...sel.options].some(o => o.value === thema)) sel.value = thema;
    anfrage.addEventListener('submit', e => {
      e.preventDefault();
      const st = $('.form-status', anfrage);
      if (!anfrage.checkValidity()) { anfrage.reportValidity(); return; }
      const d = new FormData(anfrage);
      const body = ['Name: ' + d.get('name'), 'Telefon: ' + (d.get('telefon') || '-'), 'E-Mail: ' + (d.get('email') || '-'),
        'Fahrzeug: ' + (d.get('fahrzeug') || '-'), 'Anliegen: ' + d.get('thema'), '', d.get('nachricht')].join('\n');
      location.href = 'mailto:' + anfrage.dataset.to + '?subject=' + encodeURIComponent('Anfrage über die Website: ' + d.get('thema')) + '&body=' + encodeURIComponent(body);
      st.textContent = 'Ihr E-Mail-Programm öffnet sich mit der fertigen Anfrage. Bitte dort auf Senden tippen.';
    });
  }

  /* ---------- Cursor auf Bildern (nur Maus) ---------- */
  const cur = $('.cursor');
  if (cur && fine && !reduce) {
    let x = -200, y = -200, cx = x, cy = y, laeuft = false;
    const loop = () => { cx += (x - cx) * .22; cy += (y - cy) * .22; cur.style.transform = `translate(${cx}px,${cy}px)`; if (Math.abs(x - cx) + Math.abs(y - cy) > .5) requestAnimationFrame(loop); else laeuft = false; };
    addEventListener('pointermove', e => { x = e.clientX; y = e.clientY; if (!laeuft) { laeuft = true; requestAnimationFrame(loop); } }, { passive: true });
    $$('[data-cursor]').forEach(el => {
      el.addEventListener('pointerenter', () => { cur.textContent = el.dataset.cursor; cur.classList.add('an'); });
      el.addEventListener('pointerleave', () => cur.classList.remove('an'));
    });
  } else if (cur) cur.remove();
})();

/* Video mit eigenem Play-Knopf */
(function () {
  document.querySelectorAll('.video').forEach(box => {
    const v = box.querySelector('video'), b = box.querySelector('.video-play');
    if (!v || !b) return;
    b.addEventListener('click', () => { v.controls = true; box.classList.add('laeuft'); const p = v.play(); if (p && p.catch) p.catch(() => {}); v.focus(); });
  });
})();
