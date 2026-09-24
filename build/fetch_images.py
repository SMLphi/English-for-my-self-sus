# -*- coding: utf-8 -*-
"""Tai anh dai dien bai Wikipedia cho danh tu. Tra ten theo lo 50, tai anh song song."""
import json, os, io, glob, time, urllib.parse, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'build', 'imgcache')
META  = os.path.join(ROOT, 'build', 'imgmeta.json')
os.makedirs(CACHE, exist_ok=True)
UA  = {'User-Agent': 'BaNghinTu/1.0 (personal vocabulary study app)'}
API = 'https://en.wikipedia.org/w/api.php'
CELL = 200

HINT = {'t01':'human appearance','t02':'family','t03':'emotion','t04':'anatomy medicine',
        't05':'house furniture','t06':'food','t07':'clothing','t08':'money commerce',
        't09':'occupation','t10':'business office','t11':'school education',
        't12':'language communication','t13':'time','t14':'weather','t15':'nature',
        't16':'animal','t17':'plant','t18':'transport','t19':'travel','t20':'city',
        't21':'computer','t22':'media','t23':'hobby','t24':'sport','t25':'art',
        't26':'book','t27':'science','t28':'society','t29':'law','t30':'word'}

meta = json.load(io.open(META, encoding='utf-8')) if os.path.exists(META) else {}

def api(params):
    u = API + '?' + urllib.parse.urlencode(params)
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503): time.sleep(1.5 + k * 2); continue
            return {}
        except Exception:
            time.sleep(1 + k); continue
    return {}

def batch_titles(words):
    """Tra toi 50 tu mot lan -> {tu: (url, title)}"""
    titles = [w[0].upper() + w[1:] for w in words]
    d = api({'action':'query','format':'json','formatversion':'2','redirects':'1',
             'titles':'|'.join(titles),'prop':'pageimages|pageprops',
             'piprop':'thumbnail','pithumbsize':'500','pilimit':'50'})
    q = d.get('query', {})
    alias = {t: w for t, w in zip(titles, words)}
    for m in q.get('normalized', []) + q.get('redirects', []):
        if m.get('from') in alias: alias[m['to']] = alias[m['from']]
    out = {}
    for p in q.get('pages', []):
        w = alias.get(p.get('title'))
        if not w: continue
        if 'disambiguation' in (p.get('pageprops') or {}): continue
        if p.get('thumbnail'): out[w] = (p['thumbnail']['source'], p.get('title'))
    return out

def search_one(word, hint):
    d = api({'action':'query','format':'json','formatversion':'2','generator':'search',
             'gsrsearch':(word + ' ' + hint).strip(),'gsrlimit':'3','gsrnamespace':'0',
             'prop':'pageimages|pageprops','piprop':'thumbnail','pithumbsize':'500'})
    for p in sorted(d.get('query', {}).get('pages', []), key=lambda x: x.get('index', 9)):
        if 'disambiguation' in (p.get('pageprops') or {}): continue
        if p.get('thumbnail'): return word, (p['thumbnail']['source'], p.get('title'))
    return word, None

def square(raw):
    im = Image.open(io.BytesIO(raw))
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, 'white'); im = im.convert('RGBA')
        bg.paste(im, mask=im.split()[-1]); im = bg
    else: im = im.convert('RGB')
    w, h = im.size; s = min(w, h)
    im = im.crop(((w - s)//2, (h - s)//2, (w - s)//2 + s, (h - s)//2 + s))
    return im.resize((CELL, CELL), Image.LANCZOS)

def download(job):
    word, url, title = job
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
            raw = r.read()
        square(raw).save(os.path.join(CACHE, word.replace('/', '_') + '.jpg'),
                         'JPEG', quality=80, optimize=True)
        return word, {'title': title, 'url': url, 'ok': True}
    except Exception as e:
        return word, {'title': title, 'url': url, 'ok': False, 'err': str(e)[:70]}

def wants_photo(word, pos):
    return 'phr' not in pos and 'n' in [x.strip() for x in pos.split('/')]

def flush_now(found):
    """Tai song song roi ghi meta ngay, de chay lai khong mat cong."""
    dl = [(w, u, t) for w, (u, t) in found.items()]
    if not dl: return
    print('  tai %d anh...' % len(dl), flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for w, rec in ex.map(download, dl):
            meta[w] = rec; done += 1
            if done % 40 == 0:
                json.dump(meta, io.open(META, 'w', encoding='utf-8'), ensure_ascii=False)
                print('    da tai %d/%d' % (done, len(dl)), flush=True)
    json.dump(meta, io.open(META, 'w', encoding='utf-8'), ensure_ascii=False)
    print('    xong lo: %d anh' % done, flush=True)

def main():
    jobs, seen_all = [], set()
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 't*.json'))):
        d = json.load(io.open(f, encoding='utf-8')); seen = set()
        for a in d['words']:
            if a[0] in seen: continue
            seen.add(a[0])
            if wants_photo(a[0], a[1]) and a[0] not in seen_all:
                seen_all.add(a[0]); jobs.append((d['id'], a[0]))
    todo = [j for j in jobs if j[1] not in meta]
    print('danh tu: %d | da xong: %d | can tai: %d' % (len(jobs), len(jobs)-len(todo), len(todo)), flush=True)
    if not todo: return

    # --- buoc 1: tra ten theo lo 50 ---
    found, misses = {}, []
    words = [w for _, w in todo]
    for i in range(0, len(words), 50):
        chunk = words[i:i+50]
        got = batch_titles(chunk)
        found.update(got)
        misses += [w for w in chunk if w not in got]
        print('  tra ten %d/%d -> khop %d' % (min(i+50, len(words)), len(words), len(found)), flush=True)
        time.sleep(.3)

    # --- buoc 2: tai ngay nhung tu da khop ten ---
    flush_now(found)

    # --- buoc 3: tu nao khong khop thi tim kiem, cham va it luong ---
    hint = {w: HINT.get(t, '') for t, w in todo}
    if misses and not os.environ.get('NO_SEARCH'):
        print('  tim kiem them cho %d tu (cham hon)...' % len(misses), flush=True)
        extra = {}
        with ThreadPoolExecutor(max_workers=2) as ex:
            for w, res in ex.map(lambda x: search_one(x, hint.get(x, '')), misses):
                if res: extra[w] = res
        flush_now(extra)

    for _, w in todo:
        meta.setdefault(w, {'ok': False})
    json.dump(meta, io.open(META, 'w', encoding='utf-8'), ensure_ascii=False)
    got = sum(1 for _, w in jobs if meta.get(w, {}).get('ok'))
    print('XONG: %d/%d danh tu co anh' % (got, len(jobs)), flush=True)

if __name__ == '__main__':
    main()
