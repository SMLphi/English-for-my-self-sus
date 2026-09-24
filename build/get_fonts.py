# -*- coding: utf-8 -*-
"""Tai phong chu Google ve may de ban tu host khong phu thuoc Google.

Lay CSS cua Google Fonts (kem dai chu Viet), tai toan bo tep .woff2 duoc nhac toi,
roi viet lai duong dan thanh duong dan noi bo -> build/fonts/.
Phong Google Fonts phat hanh theo giay phep SIL Open Font License, tu host duoc.
"""
import urllib.request, urllib.parse, io, os, re, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build', 'fonts')
os.makedirs(OUT, exist_ok=True)

# User-Agent cua trinh duyet moi -> Google tra ve woff2 (nhe nhat)
UA = {'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                     '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')}

CSS_URL = ('https://fonts.googleapis.com/css2'
           '?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800'
           '&family=IBM+Plex+Mono:wght@400;500'
           '&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400'
           '&display=swap')

def get(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

print('lay CSS tu Google Fonts...')
css = get(CSS_URL).decode('utf-8')

# App chi dung tieng Viet va tieng Anh -> bo cac bo chu khong dung cho nhe
KEEP = ('latin', 'latin-ext', 'vietnamese')
kept_blocks = []
for m in re.finditer(r'(/\*\s*([a-z-]+)\s*\*/\s*@font-face\s*\{.*?\})', css, re.S):
    if m.group(2) in KEEP:
        kept_blocks.append(m.group(1))
dropped = css.count('@font-face') - len(kept_blocks)
css = '\n'.join(kept_blocks) + '\n'
print('bo %d khai bao thuoc bo chu khong dung (cyrillic, greek...)' % dropped)

urls = sorted(set(re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', css)))
print('con lai %d tep phong can tai' % len(urls))

mapping, total = {}, 0
for u in urls:
    base = os.path.basename(urlparse_path := urllib.parse.urlparse(u).path)
    # ten tep goc cua Google khong duy nhat -> them van tat bam de tranh trung
    stem, ext = os.path.splitext(base)
    name = '%s-%s%s' % (stem, hashlib.md5(u.encode()).hexdigest()[:6], ext or '.woff2')
    dst = os.path.join(OUT, name)
    if not os.path.exists(dst):
        data = get(u)
        open(dst, 'wb').write(data)
    total += os.path.getsize(dst)
    mapping[u] = 'fonts/' + name

for u, local in mapping.items():
    css = css.replace(u, local)

header = ('/* Phong chu tu host - tai tu Google Fonts, giay phep SIL Open Font License.\n'
          '   Sinh boi build/get_fonts.py, dung sua tay. */\n')
io.open(os.path.join(OUT, 'fonts.css'), 'w', encoding='utf-8', newline='').write(header + css)

faces = css.count('@font-face')
print('da tai %d tep phong, tong %.0f KB' % (len(urls), total / 1024))
print('sinh fonts.css voi %d khai bao @font-face' % faces)
