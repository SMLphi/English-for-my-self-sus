# -*- coding: utf-8 -*-
"""In ra cac cau thay the cho nhung tu bi chon sai nghia."""
import io, json, glob, re, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'build', 'corpus')
def norm(s): return re.sub(r'\s+',' ',s.replace('\xa0',' ')).strip().lower()

vocab = set(); meaning = {}
for f in sorted(glob.glob(os.path.join(ROOT,'data','t*.json'))):
    d = json.load(io.open(f, encoding='utf-8'))
    for a in d['words']:
        vocab.add(norm(a[0])); meaning[(d['id'], a[0])] = (a[3], a[5])
def forms(w):
    out={w}
    if re.match(r'^[a-z]+$',w):
        out|={w+'s',w+'es',w+'ed',w+'d',w+'ing',w+'er',w+'est',w+"'s"}
        if w.endswith('e'): out|={w[:-1]+'ing',w[:-1]+'ed'}
        if w.endswith('y'): out|={w[:-1]+'ies',w[:-1]+'ied'}
    return out
EXTRA=set("""a an the i me my you your he him his she her it its we us our they them their is am are
was were be been being have has had do does did will would can could shall should may might must
not no yes to of in on at by for with from as and or but if so than that this these those there
here what when where who whom whose which how why all any some each every both very too much many
more most less own same other another such just only also then now well went gone got said made
took came saw knew thought found gave told became left felt put brought began kept held wrote
stood heard ran sat spoke bought ate drove chose fell paid met sent built grew lost drank slept
flew broke spent read forgot sold taught caught bit hid rose tom mary john mr mrs ms dr o'clock
don't doesn't didn't isn't aren't wasn't weren't can't won't couldn't shouldn't wouldn't haven't
hasn't hadn't i'm i'll i've i'd you're you'll he's she's it's we're they're that's there's let's""".split())
allowed=set(EXTRA)
for w in vocab:
    if ' ' in w: allowed |= set(w.split())
    else: allowed |= forms(w)

eng={}
for line in io.open(os.path.join(C,'eng_sentences.tsv'),encoding='utf-8'):
    p=line.rstrip('\n').split('\t')
    if len(p)>=3: eng[p[0]]=p[2]
vie={}
for line in io.open(os.path.join(C,'vie_sentences.tsv'),encoding='utf-8'):
    p=line.rstrip('\n').split('\t')
    if len(p)>=3: vie[p[0]]=p[2]
link={}
for line in io.open(os.path.join(C,'eng-vie_links.tsv'),encoding='utf-8'):
    p=line.rstrip('\n').split('\t')
    if len(p)>=2 and p[1] in vie: link.setdefault(p[0],p[1])

tok=re.compile(r"[A-Za-z']+")
index=collections.defaultdict(list)
for sid,text in eng.items():
    if not (text[0].isupper() and text[-1] in '.!?'): continue
    ws=tok.findall(text)
    if not (5<=len(ws)<=14): continue
    low=[w.lower() for w in ws]
    if any(w not in allowed for w in low): continue
    for w in set(low): index[w].append(sid)

# cau dang dung, de khong lap lai
inuse=set()
for f in glob.glob(os.path.join(ROOT,'data','ex2','t*.json')):
    for w,v in json.load(io.open(f,encoding='utf-8')).items():
        if v[0]: inuse.add(norm(v[0]))

for arg in sys.argv[1:]:
    tid,word = arg.split('|',1)
    key=norm(word)
    cands=[s for s in index.get(key,[]) if norm(eng[s]) not in inuse]
    if ' ' in key:
        cands=[s for s in index.get(key.split()[0],[]) if key in norm(eng[s]) and norm(eng[s]) not in inuse]
    vi_mean, ex1 = meaning.get((tid,word), ('',''))
    cands=[s for s in cands if norm(eng[s])!=norm(ex1)]
    cands.sort(key=lambda s:(0 if s in link else 1, abs(len(tok.findall(eng[s]))-8)))
    print('\n== %s|%s   (nghia: %s)' % (tid,word,vi_mean))
    print('   cau 1 dang co: %s' % ex1)
    for i,s in enumerate(cands[:6]):
        vt = vie[link[s]] if s in link else ''
        print('   [%d] %s%s' % (i, eng[s], ('   |VI| '+vt) if vt else ''))
    if not cands: print('   (khong con cau nao khac)')
