# -*- coding: utf-8 -*-
"""Tai kho cau Tatoeba (Anh, Viet va lien ket dich giua hai ngon ngu).

Kho nay khong dua vao git vi nang ~106 MB. Chay lai script la co.
Nguon: https://tatoeba.org  ·  giay phep CC BY 2.0 FR
"""
import urllib.request, bz2, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build', 'corpus')
os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'BaNghinTu/1.0 (personal vocabulary study app)'}
BASE = 'https://downloads.tatoeba.org/exports/per_language/'

FILES = [
    (BASE + 'eng/eng_sentences.tsv.bz2',     'eng_sentences.tsv'),
    (BASE + 'vie/vie_sentences.tsv.bz2',     'vie_sentences.tsv'),
    (BASE + 'eng/eng-vie_links.tsv.bz2',     'eng-vie_links.tsv'),
]

for url, name in FILES:
    dst = os.path.join(OUT, name)
    if os.path.exists(dst):
        print('bo qua (da co)  %s' % name)
        continue
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read()
        txt = bz2.decompress(raw).decode('utf-8', 'replace')
        io.open(dst, 'w', encoding='utf-8', newline='').write(txt)
        print('tai xong       %-22s %6.1f MB  %d dong'
              % (name, len(raw) / 1048576, txt.count('\n')))
    except Exception as e:
        print('LOI            %-22s %s' % (name, str(e)[:90]))
