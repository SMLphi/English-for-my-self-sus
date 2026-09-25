# -*- coding: utf-8 -*-
"""Dung chu de con (bai hoc) tu 40 chu de goc.

- Chu de goc: data/topics/tNN.json (du lieu tu, khong sua).
- Cach tach: build/subtopics.json — moi chu de lon -> cac chu de con theo nghia.
  Chu de khong co trong tep do (danh sach xep theo van) -> chia deu, moi phan <= AUTO_MAX tu.
- Kiem tra chat: tu nao chua xep / xep hai lan / sai ten -> bao loi, khong de lot tu.
"""
import io, os, json, glob, math, string

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS_DIR = os.path.join(ROOT, 'data', 'topics')
AUTO_MAX = 25
THEME_LAST = 18          # t01..t18: chu de doi song; t19..: tu loai & cap do


def master_topics():
    out = []
    for f in sorted(glob.glob(os.path.join(TOPICS_DIR, 't*.json'))):
        d = json.load(io.open(f, encoding='utf-8'))
        seen, rows = set(), []
        for a in d['words']:
            if a[0] in seen: continue                      # trung trong cung chu de
            if len(a) > 5 and str(a[5]).startswith('(xem '): continue   # muc tro rong
            seen.add(a[0]); rows.append(a)
        d['rows'] = rows
        out.append(d)
    return out


def load_lessons(strict=True):
    """Tra ve (groups, lessons). lesson = {id, group, name, rows}."""
    split = json.load(io.open(os.path.join(ROOT, 'build', 'subtopics.json'), encoding='utf-8'))
    groups, lessons, problems = [], [], []
    for d in master_topics():
        tid, rows = d['id'], d['rows']
        by_word = {a[0]: a for a in rows}
        parts = []
        if tid in split:
            used = {}
            for name, spec in split[tid]:
                ws = [w.strip() for w in spec.split('|') if w.strip()]
                pr = []
                for w in ws:
                    if w not in by_word: problems.append('%s: "%s" khong co trong chu de' % (tid, w)); continue
                    if w in used: problems.append('%s: "%s" xep hai lan (%s, %s)' % (tid, w, used[w], name)); continue
                    used[w] = name; pr.append(by_word[w])
                parts.append((name, pr))
            missing = [a[0] for a in rows if a[0] not in used]
            if missing: problems.append('%s: chua xep %d tu: %s' % (tid, len(missing), ', '.join(missing)))
        else:
            k = math.ceil(len(rows) / AUTO_MAX)
            size = math.ceil(len(rows) / k)
            for j in range(k):
                pr = rows[j * size:(j + 1) * size]
                if pr: parts.append(('Phần %d/%d · %s – %s' % (j + 1, k, pr[0][0], pr[-1][0]), pr))
        ids = []
        for j, (name, pr) in enumerate(parts):
            if not pr: continue
            lid = tid + string.ascii_lowercase[j]
            lessons.append({'id': lid, 'group': tid, 'name': name, 'rows': pr})
            ids.append(lid)
        groups.append({'id': tid, 'kind': 'theme' if int(tid[1:]) <= THEME_LAST else 'level',
                       'name': d['name'], 'lessons': ids, 'count': len(rows)})
    if problems and strict:
        raise SystemExit('Loi tach chu de con:\n  ' + '\n  '.join(problems))
    return groups, lessons


if __name__ == '__main__':
    g, l = load_lessons()
    for x in g:
        ls = [y for y in l if y['group'] == x['id']]
        print('%s %-34s %3d tu -> %d bai: %s' % (x['id'], x['name'][:34], x['count'], len(ls),
                                                 ', '.join('%s(%d)' % (y['name'][:22], len(y['rows'])) for y in ls)))
    print('%d chu de lon, %d chu de con, lon nhat %d tu' % (len(g), len(l), max(len(y['rows']) for y in l)))
