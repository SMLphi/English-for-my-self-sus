# -*- coding: utf-8 -*-
"""Dung ban PWA doc lap: tep HTML day du + manifest + service worker."""
import io, os, json, shutil, hashlib, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
PWA  = os.path.join(ROOT, 'pwa')
os.makedirs(PWA, exist_ok=True)

body = io.open(os.path.join(DIST, 'index.html'), encoding='utf-8').read()

# tach <title> ra khoi than trang de dat dung cho trong <head>
title = 'Ba Nghìn Từ'
if body.startswith('<title>'):
    end = body.index('</title>')
    title = body[7:end]
    body = body[end + 8:].lstrip('\n')

# Ban tu host: khong goi ra Google Fonts nua. Go cac the <link> do khoi than trang,
# thay bang mot stylesheet noi bo dat trong <head>.
import re as _re
GF = _re.compile(r'<link[^>]*(?:fonts\.googleapis\.com|fonts\.gstatic\.com)[^>]*>\s*', _re.I)
n_removed = len(GF.findall(body))
body = GF.sub('', body)

HEAD = '''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%s</title>
<meta name="description" content="Học 3000 từ vựng tiếng Anh Oxford theo chủ đề: nghe, nói, đọc, viết, ngữ pháp và lộ trình luyện thi.">
<meta name="theme-color" content="#1F6F5C">
%%FONTCSS%%<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Ba Nghìn Từ">
<style>
  html,body{height:100%%}
  :root{color-scheme:light dark;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
  body{margin:0;font:14px system-ui,sans-serif;background:#EDEFEC}
  img{max-width:100%%}
  [hidden]{display:none!important}
</style>
</head>
<body>
''' % title

FOOT = '''
<script>
// dang ky service worker de chay offline (im lang neu moi truong khong cho phep)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('sw.js').catch(function () {});
  });
}
</script>
</body>
</html>
'''
has_fonts = os.path.exists(os.path.join(ROOT, 'build', 'fonts', 'fonts.css'))
HEAD = HEAD.replace('%FONTCSS%',
                    '<link rel="stylesheet" href="fonts.css">\n' if has_fonts else '')
if not has_fonts:
    print('CANH BAO: chua co phong tu host -> chay: python build/get_fonts.py')
io.open(os.path.join(PWA, 'index.html'), 'w', encoding='utf-8', newline='').write(HEAD + body + FOOT)

manifest = {
  "name": "Ba Nghìn Từ — học từ vựng tiếng Anh",
  "short_name": "Ba Nghìn Từ",
  "description": "3000 từ Oxford theo chủ đề, luyện nghe nói đọc viết, ngữ pháp và lộ trình luyện thi.",
  "start_url": "./index.html",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#EDEFEC",
  "theme_color": "#1F6F5C",
  "lang": "vi",
  "categories": ["education"],
  "icons": [
    {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "icons/maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
    {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
json.dump(manifest, io.open(os.path.join(PWA, 'manifest.webmanifest'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)

fsrc = os.path.join(ROOT, 'build', 'fonts')
if os.path.isdir(fsrc):
    fdst = os.path.join(PWA, 'fonts')
    if os.path.isdir(fdst): shutil.rmtree(fdst)
    os.makedirs(fdst)
    for f in os.listdir(fsrc):
        if f.endswith('.woff2'): shutil.copy2(os.path.join(fsrc, f), os.path.join(fdst, f))
    shutil.copy2(os.path.join(fsrc, 'fonts.css'), os.path.join(PWA, 'fonts.css'))

for sub in ('img', 'icons'):
    src, dst = os.path.join(DIST, sub), os.path.join(PWA, sub)
    if os.path.isdir(src):
        if os.path.isdir(dst): shutil.rmtree(dst)
        shutil.copytree(src, dst)

assets = ['./', 'index.html', 'manifest.webmanifest']
assets += sorted('icons/' + os.path.basename(p) for p in glob.glob(os.path.join(PWA, 'icons', '*.png')))
assets += sorted('img/' + os.path.basename(p) for p in glob.glob(os.path.join(PWA, 'img', '*.jpg')))
if os.path.exists(os.path.join(PWA, 'fonts.css')):
    assets.append('fonts.css')
    assets += sorted('fonts/' + os.path.basename(p) for p in glob.glob(os.path.join(PWA, 'fonts', '*.woff2')))
ver = hashlib.md5(io.open(os.path.join(PWA,'index.html'),encoding='utf-8').read().encode()).hexdigest()[:10]

SW = '''// Ba Nghin Tu - service worker: luu toan bo app de chay offline
const VERSION = 'bnt-%s';
const ASSETS = %s;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      if (res && res.status === 200 && res.type === 'basic') {
        const copy = res.clone();
        caches.open(VERSION).then(c => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match('index.html')))
  );
});
''' % (ver, json.dumps(assets, indent=0))
io.open(os.path.join(PWA, 'sw.js'), 'w', encoding='utf-8', newline='').write(SW)

BAT = '''@echo off
title Ba Nghin Tu
cd /d "%~dp0"
echo.
echo   Dang khoi dong... giu cua so nay mo trong luc hoc.
echo.
start "" http://localhost:8777/
python -m http.server 8777 --bind 127.0.0.1 >nul 2>&1
if errorlevel 1 echo   Khong tim thay Python. Hay cai Python roi chay lai.
pause
'''
io.open(os.path.join(PWA, 'start.bat'), 'w', encoding='utf-8', newline='').write(BAT)

total = sum(os.path.getsize(os.path.join(dp, f))
            for dp, dn, fn in os.walk(PWA) for f in fn)
print('ban PWA: %d tep dc luu offline, tong %.1f MB' % (len(assets), total / 1048576))
print('phien ban cache:', ver)
print('da go %d the <link> tro toi Google Fonts' % n_removed)
