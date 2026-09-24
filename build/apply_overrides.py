# -*- coding: utf-8 -*-
"""Ap lop chi dinh thu cong: tai lai anh cho tu bi trung nghia, bo anh cho tu trong danh sach loai."""
import json, io, os, sys, time, urllib.parse, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overrides import OVERRIDE, BLOCK
import importlib.util
spec = importlib.util.spec_from_file_location('fi', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fetch_images.py'))
fi = importlib.util.module_from_spec(spec); spec.loader.exec_module(fi)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'build', 'imgcache')
META = os.path.join(ROOT, 'build', 'imgmeta.json')
meta = json.load(io.open(META, encoding='utf-8'))

# --- 1. bo anh cho tu trong danh sach loai ---
removed = 0
for w in BLOCK:
    p = os.path.join(CACHE, w.replace('/', '_') + '.jpg')
    if os.path.exists(p):
        os.remove(p); removed += 1
    meta[w] = {'ok': False, 'blocked': True}
print('da bo anh cho %d tu trong danh sach loai' % removed)

# --- 2. tra ten chi dinh theo lo ---
words = [w for w in OVERRIDE if w not in BLOCK]
title_of = {OVERRIDE[w]: w for w in words}
found = {}
titles = list(title_of.keys())
for i in range(0, len(titles), 50):
    chunk = titles[i:i+50]
    d = fi.api({'action':'query','format':'json','formatversion':'2','redirects':'1',
                'titles':'|'.join(chunk),'prop':'pageimages|pageprops',
                'piprop':'thumbnail','pithumbsize':'500','pilimit':'50'})
    q = d.get('query', {})
    alias = dict(title_of)
    for m in q.get('normalized', []) + q.get('redirects', []):
        if m.get('from') in alias: alias[m['to']] = alias[m['from']]
    for p in q.get('pages', []):
        w = alias.get(p.get('title'))
        if w and p.get('thumbnail'):
            found[w] = (p['thumbnail']['source'], p.get('title'))
    time.sleep(.3)
print('chi dinh: %d/%d tu tra duoc anh' % (len(found), len(words)))

# --- 3. tai ve, ghi de anh cu ---
jobs = [(w, u, t) for w, (u, t) in found.items()]
done = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    for w, rec in ex.map(fi.download, jobs):
        rec['forced'] = True
        meta[w] = rec; done += 1
print('da tai lai %d anh' % done)
json.dump(meta, io.open(META, 'w', encoding='utf-8'), ensure_ascii=False)
miss = [w for w in words if w not in found]
if miss: print('khong tra duoc (giu bieu tuong):', ', '.join(miss[:25]))
