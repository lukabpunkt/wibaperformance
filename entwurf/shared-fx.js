/* Effekte für die Premium-Entwürfe D–F. Alles respektiert „Bewegung reduzieren“.
   - [data-split]      Wörter maskiert einblenden (Stagger), Start per .is-in oder sofort mit data-split="load"
   - [data-count]      Zahl zählt hoch, wenn sichtbar (deutsches Format, data-dec Nachkommastellen)
   - [data-magnetic]   Button folgt leicht dem Mauszeiger (nur feine Zeiger)
   - [data-tilt]       3D-Neigung mit Glanzlicht (nur feine Zeiger)
   - FX.onScroll(fn)   rAF-gedrosselter Scroll-Callback
   - FX.progress(el)   0..1 Fortschritt eines (hohen) Abschnitts beim Durchscrollen */
(function () {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;
  const fns = [];
  let ticking = false;
  const run = () => { fns.forEach(f => f()); ticking = false; };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(run); } }, { passive: true });
  addEventListener('resize', () => requestAnimationFrame(run));

  const FX = {
    reduce, fine,
    onScroll(fn) { fns.push(fn); fn(); },
    progress(el) {
      const r = el.getBoundingClientRect();
      const total = r.height - innerHeight;
      return total <= 0 ? (r.top < 0 ? 1 : 0) : Math.min(1, Math.max(0, -r.top / total));
    },
    clamp: (v, a = 0, b = 1) => Math.min(b, Math.max(a, v)),
    map: (v, a, b) => FX.clamp((v - a) / (b - a)),
  };

  // Wörter splitten
  document.querySelectorAll('[data-split]').forEach(el => {
    const words = el.textContent.trim().split(/\s+/);
    el.setAttribute('aria-label', el.textContent.trim());
    el.innerHTML = words.map((w, i) => `<span class="w" aria-hidden="true"><span class="wi" style="--i:${i}">${w}</span></span>`).join(' ');
    if (reduce || el.dataset.split === 'load') el.classList.add('is-in');
    else if (el.dataset.split !== 'manual' && 'IntersectionObserver' in window) {
      const io = new IntersectionObserver(en => { if (en[0].isIntersecting) { el.classList.add('is-in'); io.disconnect(); } }, { threshold: .3 });
      io.observe(el);
    } else if (el.dataset.split !== 'manual') el.classList.add('is-in');
  });

  // Hochzählen
  const fmt = (v, d) => v.toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d });
  const counters = document.querySelectorAll('[data-count]');
  const count = el => {
    const to = parseFloat(el.dataset.count), d = +(el.dataset.dec || 0);
    if (reduce) { el.textContent = fmt(to, d); return; }
    const t0 = performance.now(), dur = 1300;
    const step = t => { const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 4); el.textContent = fmt(to * e, d); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(en => en.forEach(x => { if (x.isIntersecting) { count(x.target); io.unobserve(x.target); } }), { threshold: .6 });
    counters.forEach(c => { c.textContent = fmt(0, +(c.dataset.dec || 0)); io.observe(c); });
  }

  // Magnetische Buttons
  if (fine && !reduce) document.querySelectorAll('[data-magnetic]').forEach(b => {
    b.addEventListener('pointermove', e => {
      const r = b.getBoundingClientRect();
      b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .25}px, ${(e.clientY - r.top - r.height / 2) * .35}px)`;
    });
    b.addEventListener('pointerleave', () => { b.style.transform = ''; });
  });

  // Neigung mit Glanz
  if (fine && !reduce) document.querySelectorAll('[data-tilt]').forEach(c => {
    c.addEventListener('pointermove', e => {
      const r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      c.style.transform = `perspective(900px) rotateY(${(x - .5) * 10}deg) rotateX(${(.5 - y) * 8}deg)`;
      c.style.setProperty('--gx', x * 100 + '%'); c.style.setProperty('--gy', y * 100 + '%');
    });
    c.addEventListener('pointerleave', () => { c.style.transform = ''; });
  });

  window.FX = FX;
})();
