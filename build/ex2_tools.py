# -*- coding: utf-8 -*-
"""Cong cu cho bo cau vi du thu hai."""
import io, json, glob, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR  = os.path.join(ROOT, 'data', 'ex2')

INVIS = re.compile('[­​‌‍﻿]')
def clean_vi(s):
    s = INVIS.sub('', s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\s+([,.!?;:])', r'\1', s)
    if s and s[0].islower(): s = s[0].upper() + s[1:]
    if s and s[-1] not in '.!?…"\'': s += '.'
    return s

def load():
    out = {}
    for f in sorted(glob.glob(os.path.join(DIR, 't*.json'))):
        out[os.path.basename(f)[:-5]] = json.load(io.open(f, encoding='utf-8'))
    return out

def save(data):
    for tid, m in data.items():
        json.dump(m, io.open(os.path.join(DIR, tid + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=0)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'stats'
    data = load()

    if cmd == 'clean':
        n = 0
        for tid, m in data.items():
            for w, v in m.items():
                if len(v) >= 2 and v[1]:
                    c = clean_vi(v[1])
                    if c != v[1]: v[1] = c; n += 1
        save(data); print('da lam sach %d ban dich' % n)

    elif cmd == 'todo':
        # in ra cac cau can dich, theo lo
        start = int(sys.argv[2]); size = int(sys.argv[3])
        items = []
        for tid in sorted(data):
            for w, v in data[tid].items():
                if not v[1]: items.append((tid, w, v[0]))
        print('# tong can dich: %d | lo nay: %d..%d' % (len(items), start, min(start+size, len(items))))
        for tid, w, en in items[start:start+size]:
            print('%s|%s|%s' % (tid, w, en))

    elif cmd == 'review':
        # in ra cac ban dich Tatoeba CHUA soat, de doi chieu bang mat
        start = int(sys.argv[2]); size = int(sys.argv[3])
        items = [(tid, w, v[0], v[1]) for tid in sorted(data)
                 for w, v in data[tid].items() if len(v) > 2 and v[2] == 'T']
        print('# con %d ban dich chua soat | lo nay %d..%d'
              % (len(items), start, min(start+size, len(items))))
        for tid, w, en, vi in items[start:start+size]:
            print('%s|%s :: %s :: %s' % (tid, w, en, vi))

    elif cmd == 'verify':
        # nhung tu trong tep nay: giu nguyen ban dich, danh dau da doi chieu
        keys = json.load(io.open(sys.argv[2], encoding='utf-8'))
        n = 0
        for k in keys:
            tid, w = k.split('|', 1)
            if tid in data and w in data[tid] and data[tid][w][2] == 'T':
                data[tid][w][2] = 'V'; n += 1
        save(data); print('da danh dau %d ban dich la DA DOI CHIEU' % n)

    elif cmd == 'verifyrest':
        # danh dau toan bo phan con lai cua lo la da doi chieu (dung sau khi da sua het loi)
        start = int(sys.argv[2]); size = int(sys.argv[3])
        items = [(tid, w) for tid in sorted(data)
                 for w, v in data[tid].items() if len(v) > 2 and v[2] == 'T']
        n = 0
        for tid, w in items[start:start+size]:
            data[tid][w][2] = 'V'; n += 1
        save(data); print('da danh dau %d ban dich la DA DOI CHIEU' % n)

    elif cmd == 'seten':
        patch = json.load(io.open(sys.argv[2], encoding='utf-8'))
        n = 0
        for k, en in patch.items():
            tid, w = k.split('|', 1)
            if tid in data and w in data[tid]:
                data[tid][w] = [en, '', 'E']; n += 1
        save(data); print('da doi %d cau tieng Anh' % n)

    elif cmd == 'apply':
        # nap ban dich tu tep JSON {"tid|word": "ban dich"}
        patch = json.load(io.open(sys.argv[2], encoding='utf-8'))
        n = 0
        for k, vi in patch.items():
            tid, w = k.split('|', 1)
            if tid in data and w in data[tid]:
                data[tid][w][1] = clean_vi(vi)
                data[tid][w][2] = 'C'          # C = cau tu kho, ban dich do toi dich
                n += 1
        save(data); print('da ap %d ban dich' % n)

    else:
        c = collections.Counter()
        for tid, m in data.items():
            for w, v in m.items():
                c[v[2] if len(v) > 2 else '?'] += 1
                if not v[1]: c['trong'] += 1
        print('T = ban dich Tatoeba CHUA soat   : %d' % c['T'])
        print('V = ban dich Tatoeba DA doi chieu : %d' % c['V'])
        print('C = cau Tatoeba, app dich lai     : %d' % c['C'])
        print('E = chua co ban dich              : %d' % c['E'])
        print('M = cau tay cu giu lai            : %d' % c['M'])
        print('con trong                          : %d' % c['trong'])
