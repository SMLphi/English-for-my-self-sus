# -*- coding: utf-8 -*-
"""Doi chieu tu cua app voi Topic Lists cua Cambridge (build/cambridge_topics.json).

In ra: moi tu thuoc nhung chu de Cambridge nao, bao nhieu tu Oxford/mo rong khop.
Ket qua: build/cambridge_map.json {tu: [chu_de...]}
"""
import io, os, re, json, glob, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POS = r'\((?:n|v|adj|adv|prep|pl|phr v|n & v|v & n|v & adj|adj & v|n & adj|adj & n|n & adv|adj & adv|n, v|excl)\)'


# so nhieu cua nguon co nghia rieng -> khong duoc doi ve so it (glasses = kinh, khong phai cai coc)
SING_BLOCK = {'glass', 'short', 'good', 'cloth', 'jean', 'trouser', 'pant', 'sport', 'content', 'custom', 'arm'}


def variants(item, singular=True):
    s = item.lower().replace('’', "'")
    s = re.sub(POS, '', s)
    out = set()
    for p in re.split(r'\s*/\s*', s):
        p = p.strip()
        if '(' in p:
            out.add(re.sub(r'\s*\([^)]*\)', '', p).strip())          # bo phan tuy chon
            out.add(re.sub(r'[()\[\]]', '', p).strip())              # giu phan tuy chon
        else:
            out.add(p)
    more = set()
    for x in out:
        x = re.sub(r'\s+', ' ', x).strip()
        if not x: continue
        more.add(x)
        if singular and len(x) > 3 and x.endswith('s') and ' ' not in x:   # shoes -> shoe, socks -> sock
            for y in (x[:-1], x[:-2] if x.endswith('es') else ''):
                if y and y not in SING_BLOCK: more.add(y)
    return more


def load():
    cam = json.load(io.open(os.path.join(ROOT, 'build', 'cambridge_topics.json'), encoding='utf-8'))
    topic_vars = {}
    for t, lv in cam.items():
        v = {}
        for tag in ('a2', 'b1'):
            for it in lv[tag]:
                for x in variants(it):
                    v.setdefault(x, tag)                               # nho cap do dau tien gap
        topic_vars[t] = v
    words = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 't*.json'))):
        tp = json.load(io.open(f, encoding='utf-8'))
        for w in tp['words']:
            words.append((tp['id'], w))
    return cam, topic_vars, words


def main():
    cam, TV, words = load()
    ox = json.load(io.open(os.path.join(ROOT, 'build', 'oxford3000.json'), encoding='utf-8'))
    nk = lambda s: re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip().lower().replace('’', "'")
    oxset = set()
    for k in ox:
        for part in k.split(','):
            part = re.sub(r'\s*\(.*?\)', '', part).strip(); part = re.sub(r'\d+$', '', part).strip()
            if part: oxset.add(nk(part))
    res = {}
    for tid, w in words:
        k = nk(w[0])
        hits = [t for t in TV if k in TV[t]]
        res[w[0]] = hits
    n_ox = sum(1 for tid, w in words if nk(w[0]) in oxset)
    m_ox = sum(1 for tid, w in words if nk(w[0]) in oxset and res[w[0]])
    n_ex = len(words) - n_ox
    m_ex = sum(1 for tid, w in words if nk(w[0]) not in oxset and res[w[0]])
    print('tu Oxford 3000 : %d, khop chu de Cambridge: %d (%.0f%%)' % (n_ox, m_ox, 100 * m_ox / n_ox))
    print('tu mo rong     : %d, khop chu de Cambridge: %d' % (n_ex, m_ex))
    multi = collections.Counter(len(v) for v in res.values())
    print('so chu de moi tu khop:', dict(sorted(multi.items())))
    cnt = collections.Counter(t for v in res.values() for t in v)
    for t in sorted(cnt, key=lambda x: -cnt[x]): print('  %-46s %4d tu' % (t, cnt[t]))
    json.dump({'ox': sorted(oxset), 'map': res}, io.open(os.path.join(ROOT, 'build', 'cambridge_map.json'), 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
