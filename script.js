/* Виктория Науменко — интерактивность сайта.
   Без библиотек. Весь контент доступен и без JavaScript. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var KEY = 'vn-lang';

  function store(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* хранилище недоступно */ } }
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  /* ---------- Язык: запоминаем выбор и сохраняем текущий раздел ---------- */
  var lang = doc.getAttribute('lang') === 'en' ? 'en' : 'ru';
  var saved = read();
  // Если посетитель раньше выбрал английский и пришёл на русскую главную не по ссылке переключателя — ведём в EN.
  if (lang === 'ru' && saved === 'en' && !/[?&]lang=ru/.test(location.search)) {
    var ref = document.referrer || '';
    var internal = ref.indexOf(location.origin + location.pathname.replace(/[^/]*$/, '')) === 0;
    if (!internal) { location.replace('en/' + location.hash); return; }
  }

  document.querySelectorAll('[data-lang]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      var target = a.getAttribute('data-lang');
      store(target);
      if (target === lang) { ev.preventDefault(); return; }
      var hash = location.hash;
      if (hash && document.querySelector(hash)) {
        ev.preventDefault();
        location.href = a.getAttribute('href') + hash;
      }
    });
  });

  /* ---------- Шапка ---------- */
  var header = document.querySelector('[data-header]');
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.getElementById('main-nav');
  function onScroll() { if (header) header.classList.toggle('is-scrolled', window.scrollY > 24); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  if (toggle && nav) {
    toggle.hidden = false;
    var text = toggle.querySelector('.menu-text');
    var setMenu = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('menu-open', open);
      if (text) text.textContent = toggle.getAttribute(open ? 'data-close' : 'data-open');
      toggle.setAttribute('aria-label', toggle.getAttribute(open ? 'data-close' : 'data-open'));
      if (open) { setTimeout(function () { var first = nav.querySelector('a'); if (first) first.focus(); }, 80); }
    };
    toggle.addEventListener('click', function () { setMenu(toggle.getAttribute('aria-expanded') !== 'true'); });
    nav.addEventListener('click', function (ev) { if (ev.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { setMenu(false); toggle.focus(); }
    });
    window.addEventListener('resize', function () { if (window.innerWidth > 1000) setMenu(false); });
  }

  /* ---------- Сменяющиеся направления ---------- */
  var rot = document.querySelector('[data-rotator]');
  if (rot && !reduce) {
    var items = rot.querySelectorAll('.rot-item');
    var i = 0;
    if (items.length > 1) {
      setInterval(function () {
        if (document.hidden) return;
        var cur = items[i];
        i = (i + 1) % items.length;
        cur.classList.remove('is-active');
        cur.classList.add('is-leaving');
        items[i].classList.add('is-active');
        setTimeout(function () { cur.classList.remove('is-leaving'); }, 600);
      }, 2600);
    }
  }

  /* ---------- Появление при прокрутке ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- Мягкий наклон портрета и параллакс букв (только мышь) ---------- */
  var fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var portrait = document.querySelector('[data-tilt]');
  var hero = document.querySelector('.hero');
  var glyphs = document.querySelectorAll('.glyph');
  if (fine && !reduce && hero) {
    var raf = 0;
    hero.addEventListener('pointermove', function (ev) {
      if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0;
        var r = hero.getBoundingClientRect();
        var x = (ev.clientX - r.left) / r.width - 0.5;
        var y = (ev.clientY - r.top) / r.height - 0.5;
        if (portrait) { portrait.style.setProperty('--ry', (x * 8).toFixed(2) + 'deg'); portrait.style.setProperty('--rx', (-y * 6).toFixed(2) + 'deg'); }
        glyphs.forEach(function (g, k) {
          var f = k ? -18 : 28;
          g.style.setProperty('--gx', (x * f).toFixed(1) + 'px');
          g.style.setProperty('--gy', (y * f).toFixed(1) + 'px');
        });
      });
    });
    hero.addEventListener('pointerleave', function () {
      if (portrait) { portrait.style.setProperty('--ry', '0deg'); portrait.style.setProperty('--rx', '0deg'); }
    });
  }

  /* ---------- Кнопка записи на телефоне ---------- */
  var sticky = document.querySelector('[data-sticky-cta]');
  var contact = document.getElementById('contact');
  if (sticky && hero && 'IntersectionObserver' in window) {
    var heroVisible = true, contactVisible = false;
    var update = function () { sticky.classList.toggle('is-visible', !heroVisible && !contactVisible); };
    new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; update(); }, { threshold: 0.05 }).observe(hero);
    if (contact) new IntersectionObserver(function (e) { contactVisible = e[0].isIntersecting; update(); }, { threshold: 0 }).observe(contact);
  }
})();
