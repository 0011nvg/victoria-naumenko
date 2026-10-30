#!/usr/bin/env python3
"""Собирает index.html (RU) и en/index.html (EN) из content/*.json.

Запуск: python3 tools/build.py  (Python 3.8+, без сторонних пакетов)
Поля title / quote могут содержать <em> и <br>; остальной текст экранируется.
"""
import json
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://0011nvg.github.io/victoria-naumenko/"
TG = "https://t.me/vicky_nmnk"
VK = "https://vk.ru/designingthefuture"
EMAIL = "0011nvg@gmail.com"
VERSION = "20261030"

ARROW = '<span class="arr" aria-hidden="true">↗</span>'


def ext(href, ui):
    """Атрибуты для внешних ссылок."""
    if href.startswith("http"):
        return ' target="_blank" rel="noopener noreferrer"'
    return ""


def sr_new_tab(href, ui):
    return f'<span class="sr-only"> ({e(ui["new_tab"])})</span>' if href.startswith("http") else ""


def head(c, other):
    m, r = c["meta"], c["root"]
    url = SITE + c["path"]
    ld = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "url": url,
        "inLanguage": c["lang"],
        "name": m["title"],
        "mainEntity": {
            "@type": "Person",
            "name": "Виктория Науменко" if c["lang"] == "ru" else "Victoria Naumenko",
            "alternateName": "Victoria Naumenko" if c["lang"] == "ru" else "Виктория Науменко",
            "jobTitle": ["Учитель английского языка", "Преподаватель русского языка как неродного и как иностранного", "Педагог-наставник", "Заместитель директора школы"]
            if c["lang"] == "ru" else ["Teacher of Russian as a foreign language", "Teacher of Russian as an additional language", "English teacher", "Mentor teacher", "Deputy head of school"],
            "image": SITE + "assets/victoria-1000.webp",
            "email": "mailto:" + EMAIL,
            "sameAs": [TG, VK],
            "knowsLanguage": ["ru", "en"],
            "award": "Победитель профессионального конкурса «Флагманы образования»" if c["lang"] == "ru" else "Winner of the “Flagships of Education” professional competition",
        },
    }
    return f"""<!doctype html>
<html lang="{c['lang']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(m['title'])}</title>
  <meta name="description" content="{e(m['description'])}">
  <meta name="theme-color" content="#0c1236">
  <meta name="color-scheme" content="dark light">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="ru" href="{SITE}">
  <link rel="alternate" hreflang="en" href="{SITE}en/">
  <link rel="alternate" hreflang="x-default" href="{SITE}">
  <meta property="og:type" content="profile">
  <meta property="og:locale" content="{c['locale']}">
  <meta property="og:locale:alternate" content="{other['locale']}">
  <meta property="og:site_name" content="{e(m['site_name'])}">
  <meta property="og:title" content="{e(m['og_title'])}">
  <meta property="og:description" content="{e(m['og_description'])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}{m['og_image']}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{e(m['og_alt'])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(m['og_title'])}">
  <meta name="twitter:description" content="{e(m['og_description'])}">
  <meta name="twitter:image" content="{SITE}{m['og_image']}">
  <link rel="icon" href="{r}favicon.ico" sizes="any">
  <link rel="icon" href="{r}assets/icon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{r}assets/icon.png">
  <link rel="preload" href="{r}assets/fonts/manrope-{'cyrillic' if c['lang']=='ru' else 'latin'}-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" as="image" href="{r}assets/victoria-1000.webp" imagesrcset="{r}assets/victoria-600.webp 600w, {r}assets/victoria-1000.webp 1000w" imagesizes="(max-width: 860px) 86vw, 34vw">
  <link rel="stylesheet" href="{r}styles.css?v={VERSION}">
  <script>document.documentElement.classList.add('js')</script>
  <script src="{r}script.js?v={VERSION}" defer></script>
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>"""


def lang_switch(c, extra_cls=""):
    ru_href = "./" if c["lang"] == "ru" else "../"
    en_href = "en/" if c["lang"] == "ru" else "./"
    def item(code, href, label, hreflang):
        cur = c["lang"] == code
        aria = ' aria-current="true"' if cur else ""
        return f'<a class="lang-opt{" is-current" if cur else ""}" href="{href}" hreflang="{hreflang}" lang="{hreflang}" data-lang="{code}"{aria}><span class="sr-only">{label}</span><span aria-hidden="true">{code.upper()}</span></a>'
    return (f'<div class="lang-switch {extra_cls}" role="group" aria-label="{e(c["ui"]["lang_label"])}">'
            + item("ru", ru_href, "Русский", "ru") + item("en", en_href, "English", "en") + "</div>")


def header(c):
    ui = c["ui"]
    links = "".join(f'<a href="{n["href"]}">{e(n["text"])}</a>' for n in c["nav"])
    return f"""
<body>
  <a class="skip-link" href="#main">{e(ui['skip'])}</a>
  <header class="site-header" data-header>
    <div class="wrap header-inner">
      <a class="logo" href="#top" aria-label="{e(ui['home_label'])}"><span class="logo-mark" aria-hidden="true">V<i>N</i></span></a>
      <nav id="main-nav" class="main-nav" aria-label="{e(ui['nav_label'])}">{links}<a class="nav-cta-mobile" href="{TG}" target="_blank" rel="noopener noreferrer">{e(c['nav_cta'])} ↗<span class="sr-only"> ({e(ui['new_tab'])})</span></a></nav>
      <div class="header-tools">
        {lang_switch(c)}
        <a class="nav-cta" href="{TG}" target="_blank" rel="noopener noreferrer">{e(c['nav_cta'])}<span class="sr-only"> ({e(ui['new_tab'])})</span> {ARROW}</a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav" data-open="{e(ui['menu'])}" data-close="{e(ui['menu_close'])}" hidden><span class="menu-text">{e(ui['menu'])}</span><span class="burger" aria-hidden="true"><i></i><i></i></span></button>
      </div>
    </div>
  </header>"""


def hero(c):
    h, r, ui = c["hero"], c["root"], c["ui"]
    rot = "".join(f'<span class="rot-item{" is-active" if i == 0 else ""}">{e(t)}</span>' for i, t in enumerate(h["rotate"]))
    chips = "".join(f'<li class="chip chip-{i+1}"><span class="chip-dot" aria-hidden="true"></span>{e(t)}</li>' for i, t in enumerate(h["chips"]))
    pillars = "".join(
        f'<li><a class="pillar" href="{p["href"]}"><span class="pillar-n">{p["n"]}</span><span class="pillar-t">{e(p["title"])}</span><span class="pillar-s">{e(p["text"])}</span><span class="pillar-arr" aria-hidden="true">↓</span></a></li>'
        for p in h["pillars"])
    return f"""
  <main id="main">
    <section class="hero" id="top" aria-labelledby="hero-title">
      <div class="hero-aura" aria-hidden="true"><span class="aura a1"></span><span class="aura a2"></span><span class="aura a3"></span></div>
      <div class="hero-glyphs" aria-hidden="true"><span class="glyph g-a">A</span><span class="glyph g-ya">Я</span></div>
      <div class="wrap hero-grid">
        <div class="hero-copy">
          <p class="eyebrow"><span class="pulse" aria-hidden="true"></span>{e(h['eyebrow'])}</p>
          <h1 id="hero-title" class="hero-name"><span class="line">{e(h['first'])}</span> <span class="line line-2">{e(h['last'])}</span></h1>
          <p class="hero-rotator"><span class="sr-only">{e(h['sr_line'])}</span><span aria-hidden="true" class="rot-wrap"><span class="rot-prefix">{e(h['prefix'])}</span> <span class="rot" data-rotator>{rot}</span></span></p>
          <p class="hero-lead">{e(h['lead'])}</p>
          <div class="hero-actions">
            <a class="btn btn-signal" href="{TG}" target="_blank" rel="noopener noreferrer">{e(h['cta_primary'])}<span class="sr-only"> ({e(ui['new_tab'])})</span> {ARROW}</a>
            <a class="btn btn-ghost" href="#projects">{e(h['cta_secondary'])} <span class="arr" aria-hidden="true">↓</span></a>
          </div>
        </div>
        <div class="hero-visual">
          <div class="portrait" data-tilt>
            <div class="portrait-ring" aria-hidden="true"></div>
            <div class="portrait-frame">
              <img src="{r}assets/victoria-1000.webp" srcset="{r}assets/victoria-600.webp 600w, {r}assets/victoria-1000.webp 1000w" sizes="(max-width: 860px) 86vw, 34vw" width="1000" height="1334" alt="{e(h['portrait_alt'])}" fetchpriority="high">
            </div>
            <a class="badge" href="#achievements"><span class="badge-star" aria-hidden="true">✦</span><span class="badge-copy"><span class="badge-label">{e(h['badge_label'])}</span><strong>{e(h['badge_title'])}</strong></span></a>
            <ul class="chips" aria-hidden="true">{chips}</ul>
          </div>
        </div>
      </div>
      <div class="wrap"><ul class="pillars" aria-label="{e(h['pillars_label'])}">{pillars}</ul></div>
    </section>
"""


def ticker(c):
    words = "".join(f'<span>{e(w)}</span><i aria-hidden="true">✦</i>' for w in c["ticker"])
    return f"""
    <div class="ticker" aria-hidden="true"><div class="ticker-track">{words}{words}</div></div>
"""


def services(c):
    s, ui = c["services"], c["ui"]
    items = []
    for i, it in enumerate(s["items"]):
        pts = "".join(f"<li>{e(p)}</li>" for p in it["points"])
        approach = f'<p class="svc-approach">{e(it["approach"])}</p>' if it.get("approach") else ""
        items.append(f"""
          <details class="svc" name="services" id="svc-{it['id']}"{' open' if i == 0 else ''}>
            <summary>
              <span class="svc-n">0{i+1}</span>
              <span class="svc-head"><span class="svc-kicker">{e(it['kicker'])}</span><span class="svc-title">{e(it['title'])}</span></span>
              <span class="svc-toggle" aria-hidden="true"></span>
            </summary>
            <div class="svc-body">
              <div class="svc-main">
                <p class="svc-lead">{e(it['lead'])}</p>
                {approach}
                <a class="btn btn-ink" href="{TG}" target="_blank" rel="noopener noreferrer">{e(it['cta'])}<span class="sr-only"> ({e(ui['new_tab'])})</span> {ARROW}</a>
              </div>
              <div class="svc-focus">
                <p class="mini-label">{e(s['focus_label'])}</p>
                <ul class="focus-list">{pts}</ul>
              </div>
            </div>
          </details>""")
    return f"""
    <section class="section services" id="services" aria-labelledby="services-title">
      <div class="wrap services-grid">
        <div class="section-intro">
          <p class="eyebrow">{e(s['eyebrow'])}</p>
          <h2 id="services-title">{s['title']}</h2>
          <p class="intro">{e(s['intro'])}</p>
          <p class="services-note">{e(s['note'])}</p>
        </div>
        <div class="svc-list">{''.join(items)}
        </div>
      </div>
    </section>
"""


def about(c):
    a = c["about"]
    paras = "".join(f"<p>{e(p)}</p>" for p in a["paragraphs"])
    roles = "".join(
        f'<li class="role reveal"><span class="role-n">0{i+1}</span><h3 class="role-verb">{e(r["verb"])}</h3><p>{e(r["text"])}</p></li>'
        for i, r in enumerate(a["roles"]))
    return f"""
    <section class="section about" id="about" aria-labelledby="about-title">
      <div class="wrap">
        <div class="about-top">
          <div>
            <p class="eyebrow">{e(a['eyebrow'])}</p>
            <h2 id="about-title">{a['title']}</h2>
          </div>
          <div class="about-copy reveal">
            <p class="lead">{e(a['lead'])}</p>
            {paras}
          </div>
        </div>
        <h3 class="sr-only">{e(a['roles_label'])}</h3>
        <ul class="roles">{roles}</ul>
        <figure class="quote reveal">
          <blockquote><p>{a['quote']}</p></blockquote>
          <figcaption>{e(a['quote_text'])}</figcaption>
        </figure>
      </div>
    </section>
"""


def achievements(c):
    a = c["achievements"]
    f = a["feature"]
    cells = []
    for it in a["items"]:
        inner = f'<p class="ach-label">{e(it["label"])}</p><h3>{e(it["title"])}</h3><p class="ach-text">{e(it["text"])}</p>'
        if it.get("href"):
            cells.append(f'<li class="ach reveal"><a class="ach-link" href="{it["href"]}">{inner}<span class="arr" aria-hidden="true">↓</span></a></li>')
        else:
            cells.append(f'<li class="ach reveal">{inner}</li>')
    return f"""
    <section class="section achievements" id="achievements" aria-labelledby="ach-title">
      <div class="wrap">
        <p class="eyebrow">{e(a['eyebrow'])}</p>
        <h2 id="ach-title" class="ach-title">{a['title']}</h2>
        <div class="ach-grid">
          <div class="ach-feature reveal">
            <span class="feature-star" aria-hidden="true">✦</span>
            <p class="ach-label">{e(f['label'])}</p>
            <h3>{e(f['title'])}</h3>
            <p class="ach-text">{e(f['text'])}</p>
          </div>
          <ul class="ach-list">{''.join(cells)}</ul>
        </div>
      </div>
    </section>
"""


def projects(c):
    p, ui, r = c["projects"], c["ui"], c["root"]
    items = []
    for i, it in enumerate(p["items"]):
        facts = "".join(f'<li><strong>{e(v)}</strong><span>{e(t)}</span></li>' for v, t in it["facts"])
        status = f'<span class="status"><span class="status-dot" aria-hidden="true"></span>{e(it["status"])}</span>' if it["status"] else ""
        note = f'<p class="proj-note">{e(it["note"])}</p>' if it["note"] else ""
        host = it["url"].replace("https://", "")
        items.append(f"""
        <article class="proj proj--{it['id']} reveal" aria-labelledby="proj-{it['id']}">
          <div class="proj-copy">
            <div class="proj-meta"><span class="proj-n">0{i+1}</span><span class="proj-kicker">{e(it['kicker'])}</span></div>
            <h3 id="proj-{it['id']}" class="proj-title">{e(it['title'])}</h3>
            {status}
            <p class="proj-desc">{e(it['description'])}</p>
            <ul class="facts">{facts}</ul>
            <p class="proj-aud">{e(it['audience'])}</p>
            {note}
            <a class="btn btn-signal proj-btn" href="{it['url']}" target="_blank" rel="noopener noreferrer">{e(ui['open_project'])}<span class="sr-only"> «{e(it['title'])}» ({e(ui['new_tab'])})</span> {ARROW}</a>
          </div>
          <a class="proj-visual" href="{it['url']}" target="_blank" rel="noopener noreferrer" tabindex="-1" aria-hidden="true">
            <span class="browser"><span class="browser-bar"><i></i><i></i><i></i><span class="browser-url">{e(host)}</span></span>
              <img src="{r}{it['image']}" width="1200" height="825" loading="lazy" decoding="async" alt="">
            </span>
            <span class="phone"><img src="{r}{it['image_m']}" width="390" height="780" loading="lazy" decoding="async" alt=""></span>
          </a>
          <p class="sr-only">{e(it['alt'])}</p>
        </article>""")
    return f"""
    <section class="section projects" id="projects" aria-labelledby="projects-title">
      <div class="wrap">
        <div class="section-head">
          <div><p class="eyebrow">{e(p['eyebrow'])}</p><h2 id="projects-title">{p['title']}</h2></div>
          <p class="intro">{e(p['intro'])}</p>
        </div>
        <div class="proj-list">{''.join(items)}
        </div>
      </div>
    </section>
"""


def contact(c):
    k, ui = c["contact"], c["ui"]
    acts = []
    for a in k["actions"]:
        acts.append(f"""
            <a class="action action--{a['kind']}" href="{e(a['href'])}"{ext(a['href'], ui)}>
              <span class="action-label">{e(a['label'])}</span>
              <span class="action-title">{e(a['title'])}</span>
              <span class="action-detail">{e(a['detail'])}</span>{sr_new_tab(a['href'], ui)}
              <span class="action-arr" aria-hidden="true">↗</span>
            </a>""")
    return f"""
    <section class="section contact" id="contact" aria-labelledby="contact-title">
      <div class="contact-aura" aria-hidden="true"></div>
      <div class="wrap">
        <p class="eyebrow">{e(k['eyebrow'])}</p>
        <h2 id="contact-title" class="contact-title">{k['title']}</h2>
        <p class="intro contact-intro">{e(k['intro'])}</p>
        <div class="actions">{''.join(acts)}
        </div>
        <div class="contact-foot">
          <a class="vk" href="{VK}" target="_blank" rel="noopener noreferrer"><span class="vk-mark" aria-hidden="true">VK</span><span>{e(k['vk_text'])}</span><span class="sr-only"> ({e(ui['new_tab'])})</span> {ARROW}</a>
          <p class="contact-note">{e(k['note'])}</p>
        </div>
      </div>
    </section>
  </main>
"""


def footer(c):
    ui = c["ui"]
    return f"""
  <footer class="footer">
    <div class="wrap footer-inner">
      <a class="logo" href="#top" aria-label="{e(ui['home_label'])}"><span class="logo-mark" aria-hidden="true">V<i>N</i></span></a>
      <p>{e(ui['copyright'])}<span class="footer-note">{e(ui['footer_note'])}</span></p>
      {lang_switch(c, 'lang-switch--footer')}
      <a class="back-top" href="#top">{e(ui['top'])} <span aria-hidden="true">↑</span></a>
    </div>
  </footer>
  <a class="sticky-cta" href="{TG}" target="_blank" rel="noopener noreferrer" data-sticky-cta>{e(c['sticky_cta'])}<span class="sr-only"> ({e(ui['new_tab'])})</span> {ARROW}</a>
</body>
</html>
"""


def render(c, other):
    return "".join([head(c, other), header(c), hero(c), ticker(c), services(c), about(c), achievements(c), projects(c), contact(c), footer(c)])


def main():
    ru = json.loads((ROOT / "content/ru.json").read_text(encoding="utf-8"))
    en = json.loads((ROOT / "content/en.json").read_text(encoding="utf-8"))
    (ROOT / "index.html").write_text(render(ru, en), encoding="utf-8")
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "en/index.html").write_text(render(en, ru), encoding="utf-8")
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url><loc>{SITE}</loc><xhtml:link rel="alternate" hreflang="ru" href="{SITE}"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}en/"/></url>
  <url><loc>{SITE}en/</loc><xhtml:link rel="alternate" hreflang="ru" href="{SITE}"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}en/"/></url>
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print("built: index.html, en/index.html, sitemap.xml")


if __name__ == "__main__":
    main()
