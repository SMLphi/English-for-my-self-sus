# -*- coding: utf-8 -*-
"""Chon hoi thoai DailyDialog cho mot chu de sao cho it lap tu nhat.

Tham lam: moi buoc chon doan co nhieu tu MOI nhat (chua doan nao day),
tru diem cho tu da day roi (tu hiem tru nang, tu rat pho bien tru nhe).
Tep build/dlg_review/<tid>.json ghi ket qua doc tay:
  reject: [id, ...]              doan bo (noi dung khong hop, loi chinh ta...)
  skip:   {id: [tu, ...]}        tu co mat nhung KHONG dung nghia chu de -> khong tinh
  pick:   [id, ...]              doan da duyet, giu co dinh o dau
  sense:  {tu: regex}            tu nhieu nghia chi tinh khi khop mau (dung nghia chu de)
Cach dung: python build/pick_dialogs.py t01 [so_doan]
"""
import io, os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dialogues import get_dialogs, clean
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tid = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 60
rv_path = os.path.join(ROOT, 'build', 'dlg_review', tid + '.json')
RV = json.load(io.open(rv_path, encoding='utf-8')) if os.path.exists(rv_path) else {}
reject = set(RV.get('reject', [])); skip = RV.get('skip', {}); fixed = RV.get('pick', [])

t = json.load(io.open(os.path.join(ROOT, 'data', tid + '.json'), encoding='utf-8'))
forms = {}
for w in t['words']:
    b = w[0].lower(); forms[b] = b
    for f in re.split(r'[·,/;]', w[4]):
        f = re.sub(r'\(.*?\)', '', f).strip().lower()
        if re.fullmatch(r"[a-z'-]+", f) and f not in ('more', 'most', 'less', 'least'): forms.setdefault(f, b)
    d2 = b + b[-1]
    for x in [b+'s', b+'es', b+'ed', b+'d', b+'ing', b+'er', b+'r', b+'est', d2+'er', d2+'est', d2+'ed', d2+'ing',
              re.sub('e$', 'ing', b), re.sub('y$', 'ies', b)]:
        forms.setdefault(x, b)
    if b.endswith('e') and len(b) >= 6: forms.setdefault(b[:-1], b)

def hits(text):
    out = set()
    for tok in re.findall(r"[a-z]+(?:[-'][a-z]+)*", text.lower()):
        tok = re.sub(r"'s$", '', tok)
        if tok in forms: out.add(forms[tok])
        elif '-' in tok:
            out |= {forms[p] for p in tok.split('-') if p in forms}
    return out

dias = get_dialogs()
seen = set(); pool = []
for i, d in enumerate(dias):
    k = re.sub(r'\W+', '', ' '.join(d).lower())[:160]
    if k in seen: continue
    seen.add(k)
    if not (4 <= len(d) <= 12 and len(' '.join(d)) < 1100) or 'dd%d' % i in reject: continue
    # kho co doan bi cat cut (cau dai khong co dau ket thuc) hoac viet thuong ca doan -> bo
    if any(len(u) > 110 and not re.search(r"""[.!?"')]\s*$""", u) for u in d): continue
    if sum(1 for u in d if u[:1].islower()) > len(d) // 2: continue
    pool.append(i)
sense = {w: re.compile(r'(?<![a-z])(?:' + rx + ')', re.I) for w, rx in RV.get('sense', {}).items()}   # moi nhanh deu phai bat dau o dau tu
def hits_ok(i):
    # tu nhieu nghia: chi tinh khi dung dung nghia chu de (mau trong tep duyet)
    text = clean(' '.join(dias[i]))
    return {w for w in hits(text) if w not in sense or sense[w].search(text)} - set(skip.get('dd%d' % i, []))
H = {i: hits_ok(i) for i in pool}
df = {}
for i in pool:
    for w in H[i]: df[w] = df.get(w, 0) + 1
weight = lambda w: 0.25 if df.get(w, 0) > 300 else 1.0   # tu qua pho bien: lap lai khong tranh duoc

def score(i, taught):
    new = H[i] - taught; rep = H[i] & taught
    L = len(' '.join(dias[i]))
    return len(new) * 3 - sum(weight(w) for w in rep) - L / 400, new, rep

taught = set(); order = []
for key in fixed:
    i = int(key[2:]); order.append(i); taught |= H.get(i, set())
while len(order) < N:
    cand = [score(i, taught) + (i,) for i in pool if i not in order and H[i] - taught]
    if not cand: break
    s, new, rep, i = max(cand, key=lambda x: x[0])
    order.append(i); taught |= new
allw = [w[0].lower() for w in t['words']]
print('phu %d/%d tu sau %d doan' % (len(taught), len(allw), len(order)))
print('chua phu:', ', '.join(w for w in allw if w not in taught))
out = []
taught = set()
for i in order:
    new = sorted(H[i] - taught); rep = sorted(H[i] & taught); taught |= H[i]
    out.append('=== dd%d%s  MOI: %s | lap: %s' % (i, ' (da duyet)' if 'dd%d' % i in fixed else '', ', '.join(new), ', '.join(rep)))
    out += ['    ' + clean(u) for u in dias[i]]
io.open(os.path.join(ROOT, 'build', 'dlg_review', tid + '.txt'), 'w', encoding='utf-8').write('\n'.join(out))
# ket qua chot: doan nao + tu nao dung dung nghia trong doan do (app chi to mau cac tu nay)
json.dump([{'id': 'dd%d' % i, 'words': sorted(H[i])} for i in order],
          io.open(os.path.join(ROOT, 'build', 'dlg_review', tid + '.pick.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)
