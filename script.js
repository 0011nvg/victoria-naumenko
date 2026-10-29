/* Progressive enhancement: navigation and content work without JavaScript. */
(() => {
  const root = document.documentElement;
  const button = document.querySelector('.menu-toggle');
  const nav = document.getElementById('main-nav');
  if (button && nav) {
    root.classList.add('js');
    button.hidden = false;
    const closeMenu = (restoreFocus = false) => {
      button.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
      button.querySelector('span').textContent = '+';
      if (restoreFocus) button.focus();
    };
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
      button.querySelector('span').textContent = open ? '−' : '+';
    });
    nav.addEventListener('click', (event) => {
      const link = event.target.closest('a');
      if (!link || !nav.contains(link)) return;
      if (button.getAttribute('aria-expanded') === 'true') {
        closeMenu();
        const destination = document.querySelector(link.hash);
        if (destination) {
          destination.setAttribute('tabindex', '-1');
          destination.focus({ preventScroll: true });
          destination.addEventListener('blur', () => destination.removeAttribute('tabindex'), { once: true });
        }
      }
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') closeMenu(true);
    });
    document.addEventListener('click', (event) => {
      if (!event.target.closest('.header-inner')) closeMenu();
    });
    window.matchMedia('(max-width: 760px)').addEventListener('change', () => closeMenu());
  }
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if ('IntersectionObserver' in window && !motion.matches) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        if (!motion.matches) entry.target.classList.add('is-revealing');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach((element) => observer.observe(element));
  }
})();
