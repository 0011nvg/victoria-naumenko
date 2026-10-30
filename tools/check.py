#!/usr/bin/env python3
"""Статическая проверка собранных страниц: python3 tools/check.py
Проверяет: сборка актуальна, языки и метаданные, якоря, ссылки, изображения, контакты."""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = {"ru": ROOT / "index.html", "en": ROOT / "en/index.html"}
ALLOWED_EXTERNAL = {
    "https://t.me/vicky_nmnk", "https://vk.ru/designingthefuture",
    "https://0011nvg.github.io/pedagog/", "https://0011nvg.github.io/lexigo/",
    "https://0011nvg.github.io/-rkn-ai-praktikum/",
}
errors = []


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def fail(msg):
    errors.append(msg)


# 1. Сборка воспроизводима
before = {k: v.read_bytes() for k, v in PAGES.items()}
subprocess.run([sys.executable, str(ROOT / "tools/build.py")], check=True, stdout=subprocess.DEVNULL)
for k, v in PAGES.items():
    if v.read_bytes() != before[k]:
        fail(f"{k}: index.html устарел — запустите tools/build.py и закоммитьте результат")

for lang, path in PAGES.items():
    html = path.read_text(encoding="utf-8")
    p = P()
    p.feed(html)
    base = path.parent
    ids = {a.get("id") for _, a in p.tags if a.get("id")}
    if f'<html lang="{lang}">' not in html:
        fail(f"{lang}: неверный атрибут lang")
    for needle in ['rel="canonical"', 'hreflang="ru"', 'hreflang="en"', 'hreflang="x-default"', 'og:title', 'og:image', 'application/ld+json', 'name="description"']:
        if needle not in html:
            fail(f"{lang}: нет {needle}")
    if len(re.findall(r"<h1[ >]", html)) != 1:
        fail(f"{lang}: должен быть ровно один h1")
    for tag, a in p.tags:
        if tag == "a":
            href = a.get("href", "")
            if not href:
                fail(f"{lang}: пустая ссылка")
            elif href.startswith("#"):
                if href[1:] not in ids:
                    fail(f"{lang}: якорь {href} не найден")
            elif href.startswith("http"):
                if href not in ALLOWED_EXTERNAL:
                    fail(f"{lang}: неожиданная внешняя ссылка {href}")
                if a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
                    fail(f"{lang}: нет rel=noopener у {href}")
            elif href.startswith("mailto:"):
                if not href.startswith("mailto:0011nvg@gmail.com"):
                    fail(f"{lang}: неверный адрес почты {href}")
            else:
                target = (base / href).resolve()
                if not (target.exists() or (target / "index.html").exists()):
                    fail(f"{lang}: локальная ссылка не найдена {href}")
        if tag == "img":
            if "alt" not in a:
                fail(f"{lang}: изображение без alt {a.get('src')}")
            if not (a.get("width") and a.get("height")):
                fail(f"{lang}: изображение без размеров {a.get('src')}")
            if not (base / a["src"]).exists():
                fail(f"{lang}: нет файла {a['src']}")
        if tag in ("link", "script") and (a.get("href") or a.get("src")):
            ref = (a.get("href") or a.get("src")).split("?")[0]
            if not ref.startswith("http") and not (base / ref).exists():
                fail(f"{lang}: нет файла {ref}")
    for must in ["https://t.me/vicky_nmnk", "mailto:0011nvg@gmail.com", "https://vk.ru/designingthefuture"]:
        if must not in html:
            fail(f"{lang}: нет контакта {must}")
    if "github.com" in html:
        fail(f"{lang}: GitHub не должен быть ссылкой на странице")

# 2. Смешение языков в видимом тексте английской версии (допускаются названия в кавычках)
en = PAGES["en"].read_text(encoding="utf-8")
visible = re.sub(r"<script.*?</script>|<[^>]+>", " ", en, flags=re.S)
cyr = [w for w in re.findall(r"[А-Яа-яЁё][А-Яа-яЁё\-]+", visible)]
allowed = {"Флагманы", "образования", "говорить", "понимать", "объяснять", "создавать", "Русский", "Виктория", "Науменко"}
extra = sorted(set(cyr) - allowed)
if extra:
    fail(f"en: кириллица в тексте: {extra}")

# 3. CSS-шрифты на месте
css = (ROOT / "styles.css").read_text(encoding="utf-8")
for f in re.findall(r'url\("([^"]+)"\)', css):
    if not (ROOT / f).exists():
        fail(f"styles.css: нет файла {f}")

if errors:
    print("ОШИБКИ:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK: обе версии прошли проверку")
