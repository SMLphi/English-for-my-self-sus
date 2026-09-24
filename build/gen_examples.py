# -*- coding: utf-8 -*-
"""Sinh cau vi du thu hai tu kho Tatoeba (CC BY 2.0 FR) cho tung tu."""
import io, json, glob, re, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'build', 'corpus')
def norm(s): return re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip().lower()

vocab, rows = set(), []
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 't*.json'))):
    d = json.load(io.open(f, encoding='utf-8'))
    seen = set()
    for a in d['words']:
        if a[0] in seen: continue
        seen.add(a[0]); vocab.add(norm(a[0]))
        rows.append((d['id'], a[0], a[5]))

def forms(w):
    out = {w}
    if re.match(r'^[a-z]+$', w):
        out |= {w+'s', w+'es', w+'ed', w+'d', w+'ing', w+'er', w+'est', w+"'s"}
        if w.endswith('e'): out |= {w[:-1]+'ing', w[:-1]+'ed'}
        if w.endswith('y'): out |= {w[:-1]+'ies', w[:-1]+'ied', w[:-1]+'ier', w[:-1]+'iest'}
        if len(w) > 2 and w[-1] not in 'aeiou' and w[-2] in 'aeiou' and w[-3:-2] not in 'aeiou':
            out |= {w+w[-1]+'ing', w+w[-1]+'ed'}
    return out

EXTRA = set("""a an the i me my you your he him his she her it its we us our they them their
is am are was were be been being have has had do does did will would can could shall should may
might must not no yes to of in on at by for with from as and or but if so than that this these
those there here what when where who whom whose which how why all any some each every both very
too much many more most less least own same other another such just only also then now well
went gone got said made took came saw knew thought found gave told became left felt put brought
began kept held wrote stood heard ran sat spoke bought ate drove chose fell paid met sent built
grew lost drank slept flew broke spent read forgot sold taught caught bit hid rose tom mary john
mr mrs ms dr o'clock don't doesn't didn't isn't aren't wasn't weren't can't won't couldn't
shouldn't wouldn't haven't hasn't hadn't i'm i'll i've i'd you're you'll he's she's it's we're
they're that's there's let's""".split())
allowed = set(EXTRA)
for w in vocab:
    if ' ' in w: allowed |= set(w.split())
    else: allowed |= forms(w)

eng, vie, link = {}, {}, {}
for line in io.open(os.path.join(C,'eng_sentences.tsv'), encoding='utf-8'):
    p=line.rstrip('\n').split('\t');  eng[p[0]]=p[2] if len(p)>=3 else None
for line in io.open(os.path.join(C,'vie_sentences.tsv'), encoding='utf-8'):
    p=line.rstrip('\n').split('\t')
    if len(p)>=3: vie[p[0]]=p[2]
for line in io.open(os.path.join(C,'eng-vie_links.tsv'), encoding='utf-8'):
    p=line.rstrip('\n').split('\t')
    if len(p)>=2 and p[1] in vie: link.setdefault(p[0], p[1])

tok = re.compile(r"[A-Za-z']+")
index = collections.defaultdict(list)
for sid, text in eng.items():
    if not text or not (text[0].isupper() and text[-1] in '.!?'): continue
    ws = tok.findall(text)
    if not (5 <= len(ws) <= 14): continue
    low = [w.lower() for w in ws]
    if any(w not in allowed for w in low): continue
    for w in set(low): index[w].append(sid)

used = set()
out = collections.defaultdict(dict)
need_vi = []
stats = collections.Counter()
for tid, word, ex1 in rows:
    key = norm(word)
    cands = list(index.get(key, []))
    if ' ' in key:                       # cum tu: cau phai chua ca cum
        cands = [s for s in index.get(key.split()[0], []) if key in norm(eng[s])]
    cands = [s for s in cands if s not in used and norm(eng[s]) != norm(ex1)]
    if not cands:
        stats['khong_co'] += 1; continue
    def score(s):
        t = eng[s]; n = len(tok.findall(t))
        return (0 if s in link else 1,            # uu tien co san ban dich
                0 if 6 <= n <= 11 else 1,          # do dai de doc
                0 if re.search(r'\b'+re.escape(key)+r'\b', t.lower()) else 1,  # dung dang goc
                1 if t.startswith(('Tom','Mary')) else 0,
                n)
    cands.sort(key=score)
    s = cands[0]; used.add(s)
    if s in link:
        out[tid][word] = [eng[s], vie[link[s]], 'T']; stats['co_ban_dich'] += 1
    else:
        out[tid][word] = [eng[s], '', 'E']; stats['can_dich'] += 1
        need_vi.append((tid, word, eng[s]))

os.makedirs(os.path.join(ROOT,'build','ex2gen'), exist_ok=True)
for tid, m in out.items():
    json.dump(m, io.open(os.path.join(ROOT,'build','ex2gen',tid+'.json'),'w',encoding='utf-8'),
              ensure_ascii=False, indent=0)
json.dump(need_vi, io.open(os.path.join(ROOT,'build','need_vi.json'),'w',encoding='utf-8'), ensure_ascii=False)
print('co san ban dich Viet : %d' % stats['co_ban_dich'])
print('can toi dich         : %d' % stats['can_dich'])
print('khong tim duoc cau   : %d' % stats['khong_co'])
