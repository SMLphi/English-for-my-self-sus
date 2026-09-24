# -*- coding: utf-8 -*-
"""Mo rong anh sang tinh tu / dong tu cu the va cac tu con sot."""
import json, io, os, sys, glob, time, importlib.util
from concurrent.futures import ThreadPoolExecutor
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0,HERE)
from overrides import OVERRIDE, BLOCK
spec=importlib.util.spec_from_file_location('fi',os.path.join(HERE,'fetch_images.py'))
fi=importlib.util.module_from_spec(spec); spec.loader.exec_module(fi)
META=os.path.join(ROOT,'build','imgmeta.json')
meta=json.load(io.open(META,encoding='utf-8'))

todo=[]; seen=set()
for f in sorted(glob.glob(os.path.join(ROOT,'data','t*.json'))):
    d=json.load(io.open(f,encoding='utf-8'))
    for a in d['words']:
        w,pos=a[0],a[1]
        if w in seen: continue
        seen.add(w)
        if w in BLOCK: continue
        if 'phr' in pos: continue          # cum dong tu khong minh hoa duoc
        if meta.get(w,{}).get('ok'): continue
        todo.append((d['id'],w))
print('thu tra anh cho %d tu con lai'%len(todo),flush=True)

words=[w for _,w in todo]; found={}
for i in range(0,len(words),40):
    chunk=words[i:i+40]
    got={}
    for att in range(3):
        got=fi.batch_titles(chunk)
        if got: break
        time.sleep(5)
    found.update(got)
    print('  %d/%d -> khop %d'%(min(i+40,len(words)),len(words),len(found)),flush=True)
    time.sleep(1.5)

jobs=[(w,u,t) for w,(u,t) in found.items()]
print('  tai %d anh...'%len(jobs),flush=True)
done=0
with ThreadPoolExecutor(max_workers=6) as ex:
    for w,rec in ex.map(fi.download,jobs):
        meta[w]=rec; done+=1
json.dump(meta,io.open(META,'w',encoding='utf-8'),ensure_ascii=False)
print('XONG: them %d anh'%done,flush=True)
