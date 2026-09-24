# -*- coding: utf-8 -*-
"""Chon cau vi du that tu kho Tatoeba cho tung tu.

Tieu chi: cau chua tu dich, dai 5-14 tu, va MOI tu trong cau deu nam trong
von tu cua app (Oxford 3000 + ten rieng + so) -> nguoi hoc doc la hieu ngay.
"""
import io, json, glob, re, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'build', 'corpus')

def norm(s): return re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip().lower()

# ---------- 1. von tu cua app ----------
vocab, rows = set(), []
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 't*.json'))):
    d = json.load(io.open(f, encoding='utf-8'))
    for a in d['words']:
        vocab.add(norm(a[0]))
        rows.append((d['id'], a[0], a[1], a[5]))

# dang bien the don gian de mo rong von tu "duoc phep" trong cau
def forms(w):
    out = {w}
    if re.match(r'^[a-z]+$', w):
        out |= {w+'s', w+'es', w+'ed', w+'d', w+'ing', w+'er', w+'est', w+"'s"}
        if w.endswith('e'): out |= {w[:-1]+'ing', w[:-1]+'ed'}
        if w.endswith('y'): out |= {w[:-1]+'ies', w[:-1]+'ied', w[:-1]+'ier', w[:-1]+'iest'}
        if len(w) > 2 and w[-1] not in 'aeiou' and w[-2] in 'aeiou' and w[-3:-2] not in 'aeiou':
            out |= {w+w[-1]+'ing', w+w[-1]+'ed'}
    return out

allowed = set()
for w in vocab:
    if ' ' in w: allowed |= set(w.split())
    else: allowed |= forms(w)
# tu chuc nang + bat quy tac + ten rieng hay gap trong kho Tatoeba
allowed |= set("""a an the i me my you your he him his she her it its we us our they them their
is am are was were be been being have has had do does did will would can could shall should may
might must not no yes to of in on at by for with from as and or but if so than that this these
those there here what when where who whom whose which how why all any some each every both very
too much many more most less least own same other another such just only also then now very well
went gone got said made took came saw knew thought found gave told became left felt put brought
began kept held wrote stood heard let began ran sat spoke bought ate drove chose fell paid met
sent built grew lost drank slept flew broke spent read forgot sold taught caught bit hid rose
tom mary john mr mrs ms dr o'clock don't doesn't didn't isn't aren't wasn't weren't can't won't
couldn't shouldn't wouldn't haven't hasn't hadn't i'm i'll i've i'd you're you'll he's she's it's
we're they're that's there's let's""".split())

# ---------- 2. nap kho cau ----------
print('nap kho cau...', flush=True)
eng = {}
for line in io.open(os.path.join(C, 'eng_sentences.tsv'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 3: eng[p[0]] = p[2]
vie = {}
for line in io.open(os.path.join(C, 'vie_sentences.tsv'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 3: vie[p[0]] = p[2]
link = {}
for line in io.open(os.path.join(C, 'eng-vie_links.tsv'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 2 and p[1] in vie: link.setdefault(p[0], p[1])
print('  %d cau EN, %d cau VI, %d cap co ban dich' % (len(eng), len(vie), len(link)), flush=True)

# ---------- 3. loc cau "de hieu" va lap chi muc ----------
tok = re.compile(r"[A-Za-z']+")
index = collections.defaultdict(list)
kept = 0
for sid, text in eng.items():
    if not (text[0].isupper() and text[-1] in '.!?'): continue
    words = tok.findall(text)
    n = len(words)
    if n < 5 or n > 14: continue
    low = [w.lower() for w in words]
    if any(w not in allowed for w in low): continue
    kept += 1
    for w in set(low): index[w].append(sid)
print('  giu lai %d cau hoan toan nam trong von tu app' % kept, flush=True)

# ---------- 4. do phu ----------
hit = have_vi = 0
per_topic = collections.Counter()
for tid, w, pos, ex1 in rows:
    key = norm(w)
    cands = index.get(key) or (index.get(key.split()[0]) if ' ' in key else None) or []
    cands = [s for s in cands if norm(eng[s]) != norm(ex1)]
    if cands:
        hit += 1; per_topic[tid] += 1
        if any(s in link for s in cands): have_vi += 1
print('\nDO PHU: %d/%d tu tim duoc cau (%.1f%%)' % (hit, len(rows), hit/len(rows)*100))
print('         %d tu co san ban dich tieng Viet (%.1f%%)' % (have_vi, have_vi/len(rows)*100))
json.dump({'kept': kept}, io.open(os.path.join(ROOT,'build','corpus','stats.json'),'w',encoding='utf-8'))

print('\nVi du mau:')
import random; random.seed(3)
for tid, w, pos, ex1 in random.sample(rows, 12):
    key = norm(w)
    cands = [s for s in (index.get(key) or []) if norm(eng[s]) != norm(ex1)]
    cands.sort(key=lambda s: (s not in link, len(eng[s])))
    if cands:
        s = cands[0]
        print('  %-14s %s' % (w, eng[s]))
        if s in link: print('  %-14s   [co ban dich] %s' % ('', vie[link[s]]))
    else:
        print('  %-14s (khong co cau phu hop)' % w)
