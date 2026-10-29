"""Dependency-free release checks: generated page, assets, links, metadata."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
before = (ROOT/'index.html').read_bytes()
subprocess.run([sys.executable, str(ROOT/'tools/build.py')], check=True)
assert before == (ROOT/'index.html').read_bytes(), 'Generated index.html was out of date'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]; self.links=[]; self.assets=[]; self.meta={}; self.h1=0; self.images=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='a':
            self.links.append(a)
            if a.get('target')=='_blank':assert 'noopener' in a.get('rel',''), 'Missing noopener'
        if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
        if tag in ('img','script') and 'src' in a:self.assets.append(a['src'])
        if tag=='link' and a.get('rel') in ('stylesheet','icon','apple-touch-icon'):self.assets.append(a['href'])
        if tag=='img':
            self.images.append(a)
            assert a.get('alt'), 'Missing descriptive image alt'
            assert a.get('width') and a.get('height'), 'Missing intrinsic image dimensions'

p=Page(); html=(ROOT/'index.html').read_text();p.feed(html)
assert p.h1==1
assert len(p.ids)==len(set(p.ids)), 'Duplicate IDs'
for link in p.links:
    target=link.get('href','')
    assert target and target!='#', 'Empty link'
    if target.startswith('#'):assert target[1:] in p.ids, f'Broken anchor: {target}'
    else:assert urlsplit(target).scheme=='https', f'Non-HTTPS link: {target}'
for asset in p.assets:assert (ROOT/asset).is_file(), f'Missing asset: {asset}'
for key in ('description','og:title','og:description','og:url','og:image','twitter:card'):
    assert p.meta.get(key), f'Missing metadata: {key}'
assert (ROOT/'assets/social.jpg').is_file()
assert '<html lang="ru">' in html
assert 'prefers-reduced-motion:reduce' in (ROOT/'styles.css').read_text()
assert '{{' not in html
assert 'mailto:' not in html and 'tel:' not in html
data=json.loads((ROOT/'content.json').read_text())
expected={'https://0011nvg.github.io/lexigo/','https://0011nvg.github.io/pedagog/','https://0011nvg.github.io/-rkn-ai-praktikum/','https://vk.ru/designingthefuture'}
assert {x['href'] for x in p.links if x['href'].startswith('https://')}==expected
assert {x['id'] for x in data['projects'] if x['status']=='В разработке'}=={'lexigo','rkn'}
total=sum(f.stat().st_size for f in (ROOT/'assets').iterdir())
assert total<1_000_000, f'Assets exceed 1 MB: {total}'
print(f'PASS: static HTML, metadata, {len(p.links)} links, {len(p.images)} images, assets {total:,} bytes')
