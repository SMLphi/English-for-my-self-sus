# -*- coding: utf-8 -*-
"""Gop du lieu chu de + vo app -> dist/index.html (mot tep duy nhat)."""
import io, json, glob, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from pics import PICS, TOPIC_DEFAULT

def load_ex2(tid):
    p = os.path.join(ROOT, 'data', 'ex2', tid + '.json')
    return json.load(io.open(p, encoding='utf-8')) if os.path.exists(p) else {}

def load_topics():
    topics = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 't*.json'))):
        d = json.load(io.open(f, encoding='utf-8'))
        tid = d['id']
        icon = TOPIC_DEFAULT.get(tid, '📘')
        ex2 = load_ex2(tid)
        seen, words = set(), []
        for a in d['words']:
            w = a[0]
            if w in seen:                       # trung trong cung chu de
                continue
            if len(a) > 5 and str(a[5]).startswith('(xem '):   # muc tro rong
                continue
            seen.add(w)
            row = list(a[:8]) + [''] * max(0, 8 - len(a))
            pic = PICS.get(w) or PICS.get(w.lower()) or icon
            hook = a[9] if len(a) > 9 else ''
            second = (ex2.get(w) or ['', '', ''])
            second = list(second) + [''] * (3 - len(second))
            row = row + [pic, hook, second[0], second[1], second[2]]
            # bo truong rong o cuoi de file nho hon
            while row and row[-1] == '':
                row.pop()
            words.append(row)
        topics.append({'id': tid, 'name': d['name'], 'icon': icon, 'words': words})
    return topics

def main():
    topics = load_topics()
    total = sum(len(t['words']) for t in topics)
    grammar = []
    for gf in sorted(glob.glob(os.path.join(ROOT, 'data', 'grammar', 'g*.json'))):
        grammar.append(json.load(io.open(gf, encoding='utf-8')))
    exam = json.load(io.open(os.path.join(ROOT, 'data', 'exam.json'), encoding='utf-8'))
    # nhan trinh do CEFR lay tu danh sach Oxford 3000 goc (PDF cua Oxford University Press)
    oxp = os.path.join(ROOT, 'build', 'oxford3000.json')
    oxraw = json.load(io.open(oxp, encoding='utf-8')) if os.path.exists(oxp) else {}
    nk = lambda s: re.sub(r'\s+', ' ', s.replace(' ', ' ')).strip().lower().replace('’', "'").replace('‘', "'")
    oxlev = {}
    for k, v in oxraw.items():
        for part in [x.strip() for x in k.split(',')]:
            part = re.sub(r'\s*\(.*?\)', '', part).strip()
            part = re.sub(r'\d+$', '', part).strip()
            if part:
                oxlev.setdefault(nk(part), v.get('cefr', ''))
    seen_words = {nk(w[0]) for tp in topics for w in tp['words']}
    ox = {w: oxlev[w] for w in seen_words if w in oxlev}
    pf = os.path.join(ROOT, 'build', 'photos.json')
    photos = json.load(io.open(pf, encoding='utf-8')) if os.path.exists(pf) else {}
    payload = json.dumps({'topics': topics, 'photos': photos, 'grammar': grammar, 'exam': exam, 'ox': ox},
                         ensure_ascii=False, separators=(',', ':'))

    shell = io.open(os.path.join(ROOT, 'app', 'shell.html'), encoding='utf-8').read()
    if '/*__DATA__*/ null' not in shell:
        raise SystemExit('Khong tim thay cho chen du lieu trong shell.html')
    out = shell.replace('/*__DATA__*/ null', payload)

    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    dst = os.path.join(ROOT, 'dist', 'index.html')
    io.open(dst, 'w', encoding='utf-8', newline='').write(out)

    kb = len(out.encode('utf-8')) / 1024
    print(f'{len(topics)} chu de · {total} tu · dist/index.html {kb:.0f} KB')
    n2 = sum(1 for tp in topics for w in tp['words'] if len(w) > 10 and w[10])
    nvi = sum(1 for tp in topics for w in tp['words'] if len(w) > 11 and w[11])
    print(f'cau vi du thu hai: {n2}/{total} tu (co ban dich: {nvi})')
    nph = sum(len(v['cells']) for v in photos.values())
    npt = sum(len(g['points']) for g in grammar)
    nex = sum(len(p['ex']) for g in grammar for p in g['points'])
    print(f'anh that: {nph}/{total} tu · con lai dung bieu tuong')
    print(f'ngu phap: {npt} chuyen de · {nex} bai tap')
    print(f'ky thi: {", ".join(exam[k]["short"] for k in exam)}')
    print(f'Oxford 3000: {len(ox)}/{total} tu co nhan CEFR · phu {len(ox)}/{len(oxlev)} danh sach goc ({len(ox)/len(oxlev)*100:.1f}%)')

if __name__ == '__main__':
    main()
