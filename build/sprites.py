# -*- coding: utf-8 -*-
"""Ghep anh da tai thanh mot tam sprite cho moi chu de + ban do o luoi."""
import json, os, io, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'build', 'imgcache')
META = os.path.join(ROOT, 'build', 'imgmeta.json')
OUT = os.path.join(ROOT, 'dist', 'img')
CELL, COLS = 200, 10

def main():
    meta = json.load(io.open(META, encoding='utf-8')) if os.path.exists(META) else {}
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, '*.jpg')):   # xoa sprite cua bo chu de cu
        os.remove(old)
    book = {}
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from lessons import load_lessons
    for L in load_lessons()[1]:                          # moi chu de con mot tam sprite
        tid = L['id']
        have = []
        for a in L['rows']:
            w = a[0]
            p = os.path.join(CACHE, w.replace('/', '_') + '.jpg')
            if meta.get(w, {}).get('ok') and os.path.exists(p):
                have.append((w, p))
        if not have:
            continue
        rows = (len(have) + COLS - 1) // COLS
        sheet = Image.new('RGB', (COLS * CELL, rows * CELL), (238, 240, 236))
        cells, titles = {}, {}
        for i, (w, p) in enumerate(have):
            try:
                im = Image.open(p).convert('RGB')
                if im.size != (CELL, CELL): im = im.resize((CELL, CELL), Image.LANCZOS)
                sheet.paste(im, ((i % COLS) * CELL, (i // COLS) * CELL))
                cells[w] = i
                t = (meta.get(w) or {}).get('title')
                if t and t.lower() != w.lower(): titles[w] = t
            except Exception as e:
                print('  bo qua', w, str(e)[:50])
        dst = os.path.join(OUT, tid + '.jpg')
        sheet.save(dst, 'JPEG', quality=76, optimize=True, progressive=True)
        kb = os.path.getsize(dst) / 1024
        book[tid] = {'rows': rows, 'cols': COLS, 'cells': cells, 'titles': titles}
        print('%s  %3d anh  %d x %d  %5.0f KB' % (tid, len(cells), COLS, rows, kb))
    json.dump(book, io.open(os.path.join(ROOT, 'build', 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    tot = sum(len(v['cells']) for v in book.values())
    mb = sum(os.path.getsize(os.path.join(OUT, k + '.jpg')) for k in book) / 1048576
    print('TONG: %d anh trong %d tam, %.1f MB' % (tot, len(book), mb))

if __name__ == '__main__':
    main()
