/* Gemeinsame Funktionen aller WIBA-Entwürfe:
   Cookie-Banner, Scroll-up, Kontakt-Button, Scroll-Reveal, mobiles Menü */
(function () {
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.documentElement.classList.add('js');

  // Cookie-Banner: „Ablehnen“ und „Zustimmen“ gleichwertig
  const cookie = document.getElementById('cookie');
  if (cookie) {
    if (!store.get('wiba-consent')) setTimeout(() => cookie.classList.add('is-open'), 1400);
    cookie.querySelectorAll('[data-consent]').forEach(btn => btn.addEventListener('click', () => {
      store.set('wiba-consent', btn.dataset.consent);
      cookie.classList.remove('is-open');
    }));
  }

  // Scroll-up
  const toTop = document.getElementById('toTop');
  if (toTop) {
    const onScroll = () => toTop.classList.toggle('is-visible', window.scrollY > window.innerHeight * 0.9);
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
    toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }));
  }

  // Kontakt-Button: Anrufen / E-Mail / Route
  const fab = document.getElementById('fab');
  if (fab) {
    const t = fab.querySelector('.fab-toggle');
    const set = open => { fab.classList.toggle('is-open', open); t.setAttribute('aria-expanded', open); };
    t.addEventListener('click', () => set(!fab.classList.contains('is-open')));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && fab.classList.contains('is-open')) { set(false); t.focus(); } });
    document.addEventListener('click', e => { if (!fab.contains(e.target)) set(false); });
  }

  // Scroll-Reveal (einmalig)
  const els = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(en => en.forEach(x => {
      if (x.isIntersecting) { x.target.classList.add('is-in'); io.unobserve(x.target); }
    }), { threshold: 0.15 });
    els.forEach(el => io.observe(el));
  } else els.forEach(el => el.classList.add('is-in'));

  // Mobiles Menü
  const mb = document.querySelector('.menu-btn');
  if (mb) {
    const set = open => { document.body.classList.toggle('menu-open', open); mb.setAttribute('aria-expanded', open); };
    mb.addEventListener('click', () => set(!document.body.classList.contains('menu-open')));
    document.querySelectorAll('.nav a').forEach(a => a.addEventListener('click', () => set(false)));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') set(false); });
  }

  window.WIBA = { reduce };
})();
