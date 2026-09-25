# -*- coding: utf-8 -*-
"""Lay hoi thoai tu kho DailyDialog cho tung chu de.

Nguon: DailyDialog (Li et al., IJCNLP 2017) - CC BY-NC-SA 4.0.
Kho goc tai tu Hugging Face ve build/corpus/dd/*.parquet (xem get_dialogs()).

Cach dung:
  python build/dialogues.py t01                  -> theo danh sach chot cua pick_dialogs.py
  python build/dialogues.py t01 4876 2606 ...   -> chon tay theo so thu tu trong kho
Cau tieng Anh chi duoc chuan hoa khoang trang va dau nhay, khong sua noi dung.
Ban dich tieng Viet (truong "vi") duoc giu lai neu tep da co.
"""
import io, os, re, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DD = os.path.join(ROOT, 'build', 'corpus', 'dd')
HF = 'https://huggingface.co/datasets/li2017dailydialog/daily_dialog/resolve/refs%2Fconvert%2Fparquet/default/{}/0000.parquet'
SPLITS = ('train', 'validation', 'test')


def get_dialogs():
    import urllib.request, pandas as pd
    os.makedirs(DD, exist_ok=True)
    frames = []
    for s in SPLITS:
        p = os.path.join(DD, s + '.parquet')
        if not os.path.exists(p):
            print('tai', s, '...')
            urllib.request.urlretrieve(HF.format(s), p)
        frames.append(pd.read_parquet(p))
    return [[u.strip() for u in d] for d in pd.concat(frames)['dialog']]


# Loi go phim hien nhien trong kho goc (sua dung tung chuoi, khong doi noi dung)
TYPOS = [
    (r"\blt's\b", "It's"),          # chu l thay cho chu I
    (r"^It it true\b", "It is true"),
    (r"\bM y name\b", "My name"),
]


def clean(s):
    """Chi chuan hoa cach viet cua kho (tach dau cau bang khoang trang), khong doi chu."""
    s = s.replace('’', "'").replace('‘', "'")
    s = re.sub(r"\s*'\s*(s|t|re|ve|ll|d|m|S|T|RE|VE|Ve|LL|D|M)\b", r"'\1", s)
    s = re.sub(r"(\w)'Ve\b", r"\1've", s)
    s = re.sub(r'\s+([,.!?;:])', r'\1', s)
    s = re.sub(r'([.!?])([A-Z])', r'\1 \2', s)      # "baby.It" -> "baby. It"
    s = re.sub(r'\s*\.\.\.\s*', '... ', s).strip()
    s = re.sub(r'\s{2,}', ' ', s)
    for bad, good in TYPOS:
        s = re.sub(bad, good, s)
    return s


def main():
    tid = sys.argv[1]
    words = {}
    if len(sys.argv) > 2:
        ids = [int(x) for x in sys.argv[2:]]
    else:
        # lay danh sach da chot tu pick_dialogs.py (kem cac tu dung dung nghia trong tung doan)
        pick = json.load(io.open(os.path.join(ROOT, 'build', 'dlg_review', tid + '.pick.json'), encoding='utf-8'))
        ids = [int(p['id'][2:]) for p in pick]
        words = {p['id']: p['words'] for p in pick}
    out = os.path.join(ROOT, 'data', 'dialogues', tid + '.json')
    # dung lai ban dich da co o bat ky tep hoi thoai nao (ke ca bo chu de cu), uu tien tep dang ghi
    old = {}
    import glob as _g
    for f in sorted(_g.glob(os.path.join(ROOT, 'data', 'dialogues', '*.json')), key=lambda f: f == out):
        for d in json.load(io.open(f, encoding='utf-8'))['items']:
            if d.get('vi') and all(d['vi']): old[d['id']] = d
    dias = get_dialogs()
    items = []
    for i in ids:
        key = 'dd%d' % i
        en = [clean(u) for u in dias[i]]
        prev = old.get(key, {})
        vi = prev.get('vi') if prev.get('vi') and len(prev['vi']) == len(en) else [''] * len(en)
        items.append({'id': key, 'title': prev.get('title', ''), 'words': words.get(key, []),
                      'en': en, 'vi': vi})
    if words:
        # de truoc kho sau: doan ngan, cau ngan len dau
        items.sort(key=lambda d: len(' '.join(d['en'])))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = {'source': 'DailyDialog', 'license': 'CC BY-NC-SA 4.0', 'items': items}
    with io.open(out, 'w', encoding='utf-8') as f:
        f.write('{"source":"DailyDialog","license":"CC BY-NC-SA 4.0","items":[\n')
        f.write(',\n'.join(json.dumps(d, ensure_ascii=False) for d in items))
        f.write('\n]}\n')
    print(out, len(items), 'hoi thoai')


if __name__ == '__main__':
    main()
