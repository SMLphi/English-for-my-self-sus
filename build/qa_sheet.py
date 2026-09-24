# -*- coding: utf-8 -*-
"""Dung bang anh co nhan de soi bang mat xem anh co dung nghia khong."""
import json, io, os, sys, glob
from PIL import Image, ImageDraw
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE=os.path.join(ROOT,'build','imgcache')
meta=json.load(io.open(os.path.join(ROOT,'build','imgmeta.json'),encoding='utf-8'))

tid=sys.argv[1] if len(sys.argv)>1 else 't01'
start=int(sys.argv[2]) if len(sys.argv)>2 else 0
limit=int(sys.argv[3]) if len(sys.argv)>3 else 48

items=[]; seen=set()
for t in tid.split(','):
    d=json.load(io.open(os.path.join(ROOT,'data',t+'.json'),encoding='utf-8'))
    for a in d['words']:
        if a[0] in seen: continue
        seen.add(a[0])
        p=os.path.join(CACHE,a[0].replace('/','_')+'.jpg')
        if meta.get(a[0],{}).get('ok') and os.path.exists(p):
            items.append((a[0],a[3],p,(meta[a[0]].get('title') or '')))
items=items[start:start+limit]
if not items: print('khong co anh cho',tid); sys.exit()
C=8; S=120; LH=26
rows=(len(items)+C-1)//C
sheet=Image.new('RGB',(C*S,rows*(S+LH)),'white'); dr=ImageDraw.Draw(sheet)
for i,(w,vi,p,title) in enumerate(items):
    x=(i%C)*S; y=(i//C)*(S+LH)
    try:
        im=Image.open(p).convert('RGB').resize((S,S))
        sheet.paste(im,(x,y))
    except Exception: dr.rectangle([x,y,x+S,y+S],fill='#ddd')
    dr.text((x+3,y+S+2),w[:17],fill='black')
    lab=title if title and title.lower()!=w.lower() else vi
    dr.text((x+3,y+S+13),lab[:19],fill='#888888')
out=os.path.join(ROOT,'build','qa_%s_%d.png'%(tid.replace(',','-'),start))
sheet.save(out); print(out,'|',len(items),'anh')
