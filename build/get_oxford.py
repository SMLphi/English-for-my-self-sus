# -*- coding: utf-8 -*-
"""Tai danh sach Oxford 3000 goc tu nhieu nguon, lay nguon nao chay duoc."""
import urllib.request, urllib.error, io, os, re, sys, json
UA={'User-Agent':'Mozilla/5.0 (vocab study app; personal use)'}
OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'build','oxford_raw')
os.makedirs(OUT,exist_ok=True)

SOURCES=[
 ("oxford-pdf","https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000.pdf"),
 ("oxford-pdf-alt","https://www.oxfordlearnersdictionaries.com/media/english/oxford3000/The_Oxford_3000.pdf"),
 ("ngsl","https://raw.githubusercontent.com/nlp-compromise/nlp-corpus/master/src/ngsl/ngsl.txt"),
 ("gh-oxford3000","https://raw.githubusercontent.com/sapbmw/The-Oxford-3000/master/The_Oxford_3000.txt"),
 ("gh-oxford5000","https://raw.githubusercontent.com/tyypgzl/Oxford-5000-words/main/full-word.json"),
]
for name,url in SOURCES:
    try:
        req=urllib.request.Request(url,headers=UA)
        with urllib.request.urlopen(req,timeout=40) as r:
            data=r.read()
        ext='.pdf' if data[:4]==b'%PDF' else ('.json' if url.endswith('.json') else '.txt')
        p=os.path.join(OUT,name+ext)
        open(p,'wb').write(data)
        print('OK   %-16s %8d bytes  -> %s'%(name,len(data),os.path.basename(p)))
    except Exception as e:
        print('LOI  %-16s %s'%(name,str(e)[:70]))
