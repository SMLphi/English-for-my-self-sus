# -*- coding: utf-8 -*-
"""Ghep cau vi du tu kho Tatoeba vao data/ex2/. Giu ban dich tay da co neu tot hon."""
import io, json, glob, os, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUNK = re.compile(r'^\s*(tiếng việt|tieng viet|\?+|-+)\s*$', re.I)

stats = collections.Counter()
manual = {}          # ban dich tay toi da viet truoc do
for f in glob.glob(os.path.join(ROOT, 'data', 'ex2', 't*.json')):
    tid = os.path.basename(f)[:-5]
    manual[tid] = json.load(io.open(f, encoding='utf-8'))

for f in sorted(glob.glob(os.path.join(ROOT, 'build', 'ex2gen', 't*.json'))):
    tid = os.path.basename(f)[:-5]
    gen = json.load(io.open(f, encoding='utf-8'))
    old = manual.get(tid, {})
    outm = {}
    for w, v in gen.items():
        en, vi, src = v[0], v[1], v[2]
        if vi and JUNK.match(vi):
            vi, src = '', 'E'
        if src == 'T':
            outm[w] = [en, vi, 'T']; stats['tatoeba_ca_hai'] += 1
        else:
            outm[w] = [en, '', 'E']; stats['can_dich'] += 1
    # tu nao kho cau khong co -> giu lai cau tay cu neu truoc day da viet
    for w, v in old.items():
        if w not in outm and isinstance(v, list) and len(v) >= 2 and v[0]:
            outm[w] = [v[0], v[1], 'M']; stats['giu_cau_tay'] += 1
    json.dump(outm, io.open(os.path.join(ROOT,'data','ex2',tid+'.json'),'w',encoding='utf-8'),
              ensure_ascii=False, indent=0)

for k, v in sorted(stats.items()): print('%-18s %d' % (k, v))
