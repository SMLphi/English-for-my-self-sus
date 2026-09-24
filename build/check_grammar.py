# -*- coding: utf-8 -*-
"""Kiem tra bo ngu phap: dap an hop le, manh ghep ghep lai dung cau."""
import json, io, glob, collections, sys

def can_build(tiles, answer):
    """Cac manh ghep (co the nhieu chu) co xep lai thanh dung cau khong?"""
    want = answer.lower().split()
    def rec(remaining, pos):
        if pos == len(want): return not remaining
        for i, t in enumerate(remaining):
            tw = t.lower().split()
            if want[pos:pos+len(tw)] == tw:
                if rec(remaining[:i] + remaining[i+1:], pos + len(tw)): return True
        return False
    return rec(list(tiles), 0)

tot = ex = 0
ids = []
types = collections.Counter()
prob = []
for f in sorted(glob.glob('data/grammar/g*.json')):
    d = json.load(io.open(f, encoding='utf-8'))
    for p in d['points']:
        tot += 1; ids.append(p['id']); ex += len(p['ex'])
        for k in ('level','name','en','intro','forms','notes','traps','ex'):
            if not p.get(k): prob.append(f"{p['id']}: thieu {k}")
        for n, e in enumerate(p['ex'], 1):
            types[e['t']] += 1
            tag = f"{p['id']} bai {n} ({e['t']})"
            if not e.get('w'): prob.append(f"{tag}: thieu giai thich")
            if e['t'] == 'mc':
                if not isinstance(e.get('a'), int) or not (0 <= e['a'] < len(e.get('o', []))):
                    prob.append(f"{tag}: chi so dap an sai")
                elif len(set(e['o'])) != len(e['o']):
                    prob.append(f"{tag}: co lua chon trung nhau")
            elif e['t'] == 'order':
                if not isinstance(e.get('q'), list): prob.append(f"{tag}: q phai la mang")
                elif not can_build(e['q'], e['a']):
                    prob.append(f"{tag}: manh ghep {e['q']} khong xep thanh '{e['a']}'")
            else:
                if not e.get('a'): prob.append(f"{tag}: thieu dap an")
                elif not isinstance(e['a'], list): prob.append(f"{tag}: dap an phai la mang")
    print(f"{d['group']:34s} {len(d['points']):2d} chuyen de")

print(f"\nTONG: {tot} chuyen de - {ex} bai tap - {dict(types)}")
dup = [i for i, c in collections.Counter(ids).items() if c > 1]
if dup: prob.append('trung ma chuyen de: ' + str(dup))
print('LOI:', len(prob))
for x in prob: print('  -', x)
sys.exit(1 if prob else 0)
