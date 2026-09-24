# -*- coding: utf-8 -*-
"""Boc tach Oxford 3000 goc (PDF cua Oxford University Press) thanh JSON."""
import re, io, json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
txt=io.open(os.path.join(ROOT,'build','oxford_raw','oxford3000.txt'),encoding='utf-8').read()

POS=(r'(?:indefinite article|definite article|modal v\.|auxiliary v\.|'
     r'n\.|v\.|adj\.|adv\.|prep\.|conj\.|pron\.|det\.|exclam\.|number)')
LEVEL=r'(A1|A2|B1|B2)'
line_re=re.compile(r'^(.+?)\s+((?:'+POS+r'|,|\s|'+LEVEL+r')+)$')

words={}
skipped=[]
for raw in txt.split('\n'):
    s=raw.strip()
    if not s: continue
    if s.startswith('©') or s.startswith('The Oxford 3000'): continue
    if re.match(r'^[A-Z]$',s): continue          # chu cai phan muc
    if not re.search(LEVEL,s): skipped.append(s); continue
    m=re.match(r'^(.*?)\s*(?=(?:'+POS+r'))(.*)$',s)
    if not m: skipped.append(s); continue
    head,rest=m.group(1).strip(),m.group(2).strip()
    if not head: skipped.append(s); continue
    levels=sorted(set(re.findall(LEVEL,rest)))
    poss=sorted(set(p.rstrip('.') for p in re.findall(POS,rest)))
    head=head.rstrip(',').strip()
    if head in words:
        words[head]['levels']=sorted(set(words[head]['levels'])|set(levels))
        words[head]['pos']=sorted(set(words[head]['pos'])|set(poss))
    else:
        words[head]={'levels':levels,'pos':poss}

order={'A1':0,'A2':1,'B1':2,'B2':3}
for w,v in words.items():
    v['cefr']=min(v['levels'],key=lambda x:order[x]) if v['levels'] else ''

json.dump(words,io.open(os.path.join(ROOT,'build','oxford3000.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
import collections
c=collections.Counter(v['cefr'] for v in words.values())
print('boc tach duoc %d muc tu'%len(words))
print('theo trinh do:',dict(sorted(c.items())))
print('bo qua %d dong'%len(skipped))
for s in skipped[:8]: print('   bo qua:',s[:70])
print('vi du:',json.dumps(dict(list(words.items())[:5]),ensure_ascii=False))
