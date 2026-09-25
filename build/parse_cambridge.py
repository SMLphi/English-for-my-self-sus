# -*- coding: utf-8 -*-
"""Tach Topic Lists (Appendix 2) trong danh sach tu vung chinh thuc cua Cambridge English.

Nguon (tai cong khai tren cambridgeenglish.org, robots.txt cho phep):
  - A2 Key and Key for Schools Vocabulary List (UCLES 2025)
  - B1 Preliminary and Preliminary for Schools Vocabulary List (CUPA 2025)
Ket qua: build/cambridge_topics.json  {chu_de: {"a2": [muc...], "b1": [muc...]}}
Moi muc giu nguyen chu viet cua Cambridge, vd "DVD (player)", "try on (v)".
"""
import io, os, re, json
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'build', 'cambridge_raw')
FILES = {
    'a2': ('506886-a2-key-2020-vocabulary-list.pdf',
           'https://www.cambridgeenglish.org/images/506886-a2-key-2020-vocabulary-list.pdf'),
    'b1': ('506887-b1-preliminary-vocabulary-list.pdf',
           'https://www.cambridgeenglish.org/Images/506887-b1-preliminary-vocabulary-list.pdf'),
}
# ten chu de chuan hoa (A2 viet "Communication", B1 viet "Communications")
SAME = {'Communications and Technology': 'Communication and Technology',
        'Personal Feelings, Opinions and Experiences (Adjectives)': 'Personal Feelings, Opinions and Experiences',
        'Personal Feelings, Opinions and Experiences (adjectives)': 'Personal Feelings, Opinions and Experiences'}
NOISE = re.compile(r'Page \d+ of \d+|\bUCLES\b|\bCUPA\b|Vocabulary List|^\s*Schools\s*$|^\s*List\s*$|Preliminary|Key and Key|Appendix|Topic Lists')  # phan biet hoa thuong: CUPA khong duoc khop occupation


def fetch():
    import urllib.request
    os.makedirs(RAW, exist_ok=True)
    for name, url in FILES.values():
        p = os.path.join(RAW, name)
        if not os.path.exists(p):
            print('tai', url)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            io.open(p, 'wb').write(urllib.request.urlopen(req, timeout=120).read())


HEADINGS = {
    'Appliances', 'Clothes and Accessories', 'Colours', 'Communication and Technology',
    'Communications and Technology', 'Documents and Texts', 'Education', 'Entertainment and Media',
    'Environment', 'Family and Friends', 'Food and Drink', 'Health, Medicine and Exercise',
    'Hobbies and Leisure', 'House and Home', 'Language', 'Measurements',
    'Personal Feelings, Opinions and Experiences (adjectives)',
    'Personal Feelings, Opinions and Experiences (Adjectives)',
    'Places: Buildings', 'Places: Countryside', 'Places: Town and City', 'Services', 'Shopping',
    'Sport', 'The Natural World', 'Time', 'Travel and Transport', 'Weather', 'Work and Jobs'}


def appendix_lines(name, layout):
    r = PdfReader(os.path.join(RAW, name))
    pages = [p.extract_text(extraction_mode='layout') if layout else p.extract_text() for p in r.pages]
    start = max(i for i, t in enumerate(pages) if 'Appendix 2' in t and 'Topic Lists' in t)
    out = []
    for t in pages[start:]:
        out += t.split(chr(10))
    return out


def parse(tag):
    # A2 xep 4 cot -> trich theo bo cuc, tach cot bang >=2 khoang trang
    # B1 moi dong mot muc -> trich thuong, noi cac dong bi xuong dong giua muc
    layout = tag == 'a2'
    topics, cur, pending = {}, None, ''
    for raw in appendix_lines(FILES[tag][0], layout):
        head = re.sub(r'\s+', ' ', raw.strip())
        if head in HEADINGS:
            cur = SAME.get(head, head)
            topics.setdefault(cur, []); pending = ''
            continue
        if NOISE.search(raw) or not raw.strip() or cur is None:
            continue
        cells = [c.strip() for c in re.split(r'\s{2,}', raw.strip()) if c.strip()] if layout else [raw.strip()]
        for c in cells:
            # "jewellery /" + "jewelry", "go" + "(with/together)" + "(phr v)", "old-fashioned" + "(adj)"
            if pending and (c.startswith('(') or pending.endswith('/')):
                topics[cur][-1] = pending = pending + ' ' + c
                continue
            topics[cur].append(c)
            pending = c
    return topics


HEAD = re.compile(r"^([A-Za-z][A-Za-z '’./-]*?)\s*\((?:[a-z &,]+)\)\s*$")


def headwords(tag):
    """Danh sach tu chinh (truoc Appendix): moi muc dang 'tu (tu loai)'."""
    r = PdfReader(os.path.join(RAW, FILES[tag][0]))
    pages = [p.extract_text() for p in r.pages]
    end = min(i for i, t in enumerate(pages) if 'Appendix' in t and i > 3)
    out = []
    for t in pages[3:end]:
        for l in t.split(chr(10)):
            m = HEAD.match(l.strip())
            if m: out.append(m.group(1).strip())
    return out


def main():
    fetch()
    res = {}
    for tag in FILES:
        for t, items in parse(tag).items():
            res.setdefault(t, {'a2': [], 'b1': []})[tag] = items
    heads = {tag: headwords(tag) for tag in FILES}
    json.dump(heads, io.open(os.path.join(ROOT, 'build', 'cambridge_words.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('danh sach tu chinh: A2 %d muc, B1 %d muc' % (len(heads['a2']), len(heads['b1'])))
    out = os.path.join(ROOT, 'build', 'cambridge_topics.json')
    json.dump(res, io.open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for t in sorted(res):
        print('%-48s A2 %3d  B1 %3d' % (t, len(res[t]['a2']), len(res[t]['b1'])))
    print(len(res), 'chu de ->', out)


if __name__ == '__main__':
    main()
