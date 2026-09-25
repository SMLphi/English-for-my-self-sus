# -*- coding: utf-8 -*-
"""Chia lai chu de theo chuan.

- Tu co trong Topic Lists cua Cambridge (A2 Key + B1 Preliminary) -> 27 chu de Cambridge.
  Tu nam o nhieu chu de -> chon chu de cu the nhat theo PRIORITY.
- Tu con lai co trong Oxford 3000 hoac danh sach tu chinh A2/B1 cua Cambridge
  -> nhom theo cap do (Oxford; khong co thi lay cap Cambridge) va tu loai.
- Tu khong co trong nguon chuan nao -> bo.
- Moi bai toi da MAX tu, sap tu de den kho.
Ghi: data/groups.json, data/t###.json, data/ex2/t###.json; in bang doi chieu.
Chay lai an toan: doc du lieu tu tat ca data/t*.json hien co (ca dinh dang cu lan moi).
"""
import io, os, re, json, glob, math, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
MAX = 30
LV = ['A1', 'A2', 'B1', 'B2']

# (khoa Cambridge, ma nhom, ten Viet, bieu tuong) — thu tu = thu tu hien thi
CAM = [
    ('Family and Friends', 'Gia đình & bạn bè', '👨‍👩‍👧'),
    ('Colours', 'Màu sắc', '🎨'),
    ('Clothes and Accessories', 'Quần áo & phụ kiện', '👕'),
    ('Food and Drink', 'Đồ ăn & đồ uống', '🍜'),
    ('House and Home', 'Nhà cửa', '🏠'),
    ('Appliances', 'Thiết bị điện', '🔌'),
    ('Time', 'Thời gian', '⏰'),
    ('Weather', 'Thời tiết', '🌦️'),
    ('Measurements', 'Đo lường', '📏'),
    ('Health, Medicine and Exercise', 'Sức khoẻ, y tế & tập luyện', '🩺'),
    ('Education', 'Giáo dục', '🎓'),
    ('Language', 'Ngôn ngữ', '🗣️'),
    ('Work and Jobs', 'Công việc & nghề nghiệp', '💼'),
    ('Shopping', 'Mua sắm', '🛒'),
    ('Services', 'Dịch vụ', '🛎️'),
    ('Places: Buildings', 'Địa điểm: toà nhà', '🏢'),
    ('Places: Town and City', 'Địa điểm: thành phố', '🏙️'),
    ('Places: Countryside', 'Địa điểm: nông thôn', '🌄'),
    ('The Natural World', 'Thế giới tự nhiên', '🌍'),
    ('Environment', 'Môi trường', '🌱'),
    ('Travel and Transport', 'Du lịch & giao thông', '✈️'),
    ('Sport', 'Thể thao', '⚽'),
    ('Hobbies and Leisure', 'Sở thích & thời gian rảnh', '🎲'),
    ('Entertainment and Media', 'Giải trí & truyền thông', '🎬'),
    ('Communication and Technology', 'Giao tiếp & công nghệ', '💻'),
    ('Documents and Texts', 'Giấy tờ & văn bản', '📄'),
    ('Personal Feelings, Opinions and Experiences', 'Cảm xúc, ý kiến & trải nghiệm', '💭'),
]
# tu nam o nhieu chu de -> chon chu de dung truoc trong danh sach nay (cu the truoc, chung sau)
PRIORITY = ['Family and Friends', 'Colours', 'Clothes and Accessories', 'Food and Drink', 'Measurements',
            'Weather', 'Time', 'Health, Medicine and Exercise', 'Appliances', 'House and Home',
            'Documents and Texts', 'Education', 'Language', 'Work and Jobs', 'Services', 'Shopping',
            'Places: Countryside', 'The Natural World', 'Environment', 'Places: Buildings', 'Places: Town and City',
            'Travel and Transport', 'Hobbies and Leisure', 'Sport', 'Entertainment and Media',
            'Communication and Technology', 'Personal Feelings, Opinions and Experiences']
POSCLS = [('n', 'Danh từ'), ('v', 'Động từ'), ('adj', 'Tính từ'), ('adv', 'Trạng từ'), ('other', 'Từ chức năng & từ khác')]
OXICON = {'A1': '🔤', 'A2': '📗', 'B1': '📘', 'B2': '📙'}


def poscls(pos):
    p = pos.split('/')[0].strip()
    if p in ('n',): return 'n'
    if p in ('v', 'phr v'): return 'v'
    if p == 'adj': return 'adj'
    if p == 'adv': return 'adv'
    return 'other'


def main():
    import sys
    sys.path.insert(0, os.path.join(ROOT, 'build'))
    from map_cambridge import load, variants  # noqa
    cam, TV, _ = load()
    nk = lambda s: re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip().lower().replace('’', "'")
    # cap do CEFR Oxford (giong build.py)
    oxraw = json.load(io.open(os.path.join(ROOT, 'build', 'oxford3000.json'), encoding='utf-8'))
    oxlev = {}
    for k, v in oxraw.items():
        for part in k.split(','):
            part = re.sub(r'\s*\(.*?\)', '', part).strip(); part = re.sub(r'\d+$', '', part).strip()
            if part: oxlev.setdefault(nk(part), v.get('cefr', ''))

    # doc toan bo tu hien co + cau vi du thu hai (moi tu la duy nhat trong app)
    old_files = sorted(glob.glob(os.path.join(DATA, 't*.json')))
    rows, ex2, oldtopic = [], {}, {}
    for f in old_files:
        d = json.load(io.open(f, encoding='utf-8'))
        e = os.path.join(DATA, 'ex2', d['id'] + '.json')
        if os.path.exists(e): ex2.update(json.load(io.open(e, encoding='utf-8')))
        for a in d['words']:
            if len(a) > 5 and str(a[5]).startswith('(xem '): continue
            if a[0] in oldtopic: continue
            oldtopic[a[0]] = d.get('name', d['id'])
            rows.append(a)

    # danh sach tu chinh cua Cambridge: tu nao co mat thi cung la tu chuan
    heads = json.load(io.open(os.path.join(ROOT, 'build', 'cambridge_words.json'), encoding='utf-8'))
    camlev = {}
    for tag, lv in (('a2', 'A2'), ('b1', 'B1')):
        for h in heads[tag]:
            for x in variants(h):
                camlev.setdefault(x, lv)
    groups = collections.OrderedDict()
    for key, vi, icon in CAM:
        groups[key] = {'kind': 'cambridge', 'en': key, 'name': vi, 'icon': icon, 'words': []}
    for lv in LV:
        groups['ox' + lv] = {'kind': 'oxford', 'en': 'Oxford 3000 / Cambridge ' + lv, 'name': 'Từ thông dụng ' + lv,
                             'icon': OXICON[lv], 'words': []}
    # khop chinh xac (khong doi so it) de xet tu khong phai danh tu
    TVX = {t: {x for it in cam[t]['a2'] + cam[t]['b1'] for x in variants(it, False)} for t in TV}
    have = {nk(a[0]) for a in rows}
    dropped, dup = [], []
    for a in rows:
        k = nk(a[0])
        if k.endswith('s') and k[:-1] in have and a[1].split('/')[0].strip() == 'n' and k not in oxlev:   # arms/goods/news la tu rieng
            dup.append(a[0]); continue                   # boots trung boot -> giu mot muc
        if len(k) > 3 and k.endswith('s') and ' ' not in k and not any(k in TV[t] for t in TV)                 and k not in oxlev and k not in camlev:
            k = k[:-1]                                   # app ghi so nhieu (boots), nguon ghi so it (boot)
        isn = a[1].split('/')[0].strip() == 'n'
        hits = [t for t in PRIORITY if k in TVX[t] or (isn and k in TV[t])]
        lev = oxlev.get(k, '') or camlev.get(k, '')
        if hits:
            t = hits[0]
            if not lev: lev = 'A2' if TV[t][k] == 'a2' else 'B1'
            groups[t]['words'].append((lev, a))
        elif lev:
            groups['ox' + lev]['words'].append((lev, a))
        else:
            dropped.append(a[0])

    # xoa du lieu cu, ghi du lieu moi
    for f in old_files: os.remove(f)
    for f in glob.glob(os.path.join(DATA, 'ex2', 't*.json')): os.remove(f)
    gl, lessons, n = [], [], 0
    for gi, (key, g) in enumerate(groups.items()):
        gid = 'g%02d' % (gi + 1)
        if g['kind'] == 'cambridge':
            ws = sorted(g['words'], key=lambda x: LV.index(x[0]) if x[0] in LV else 9)
            packs = [('', ws)]
        else:  # cap do Oxford: tach theo tu loai
            packs = [(lbl, [x for x in g['words'] if poscls(x[1][1]) == c]) for c, lbl in POSCLS]
        ids = []
        if g['kind'] == 'oxford':                        # nhom tu loai qua nho -> nhap vao nhom truoc
            merged = []
            for lbl, ws in packs:
                if merged and 0 < len(ws) < 8:
                    merged[-1] = (merged[-1][0] + ', ' + lbl.lower(), merged[-1][1] + ws)
                elif ws:
                    merged.append((lbl, ws))
            packs = merged
        for lbl, ws in packs:
            if not ws: continue
            k = math.ceil(len(ws) / MAX)
            if k > 1 and len(ws) - (k - 1) * MAX < 8 and len(ws) <= k * MAX - 8:
                pass
            size = math.ceil(len(ws) / k)
            for j in range(k):
                part = ws[j * size:(j + 1) * size]
                if not part: continue
                n += 1
                tid = 't%03d' % n
                lvs = [x[0] for x in part if x[0] in LV]
                rng = lvs[0] if lvs[0] == lvs[-1] else lvs[0] + '–' + lvs[-1]
                base = lbl if g['kind'] == 'oxford' else g['name']
                name = base + (' %d/%d' % (j + 1, k) if k > 1 else '')
                doc = {'id': tid, 'group': gid, 'name': name, 'level': rng, 'icon': g['icon'],
                       'words': [x[1] for x in part]}
                with io.open(os.path.join(DATA, tid + '.json'), 'w', encoding='utf-8') as f:
                    f.write('{"id":"%s","group":"%s","name":%s,"level":"%s","icon":"%s","words":[\n' % (
                        tid, gid, json.dumps(name, ensure_ascii=False), rng, g['icon']))
                    f.write(',\n'.join(json.dumps(w, ensure_ascii=False) for w in doc['words']))
                    f.write('\n]}\n')
                e2 = {w[0]: ex2[w[0]] for w in doc['words'] if w[0] in ex2}
                json.dump(e2, io.open(os.path.join(DATA, 'ex2', tid + '.json'), 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=0)
                ids.append(tid)
                lessons.append((g['name'], name, rng, len(part)))
        gl.append({'id': gid, 'kind': g['kind'], 'name': g['name'], 'en': g['en'], 'icon': g['icon'],
                   'lessons': ids, 'count': len(g['words'])})
    json.dump(gl, io.open(os.path.join(DATA, 'groups.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # bao cao
    rep = ['# Doi chieu chu de moi', '', '| Nhom | Chuan | So tu | So bai |', '|---|---|---|---|']
    for g in gl:
        rep.append('| %s %s | %s | %d | %d |' % (g['icon'], g['name'], g['en'], g['count'], len(g['lessons'])))
    rep += ['', 'Tu bi bo (khong co trong Oxford 3000 va danh sach Cambridge A2/B1): %d' % len(dropped), '',
            ', '.join(sorted(dropped))]
    io.open(os.path.join(ROOT, 'build', 'regroup_report.md'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    tot = sum(g['count'] for g in gl)
    cam_n = sum(g['count'] for g in gl if g['kind'] == 'cambridge')
    print('giu %d tu (%d theo chu de Cambridge, %d theo cap do Oxford), bo %d tu mo rong, gop %d muc trung so nhieu' % (
        tot, cam_n, tot - cam_n, len(dropped), len(dup)))
    print('%d nhom, %d bai; bai lon nhat %d tu' % (len(gl), n, max(x[3] for x in lessons)))


if __name__ == '__main__':
    main()
