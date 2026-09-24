# -*- coding: utf-8 -*-
"""Kiem tra cong thuc CSS cat o sprite co khop anh goc khong."""
import json, io, os, sys
from PIL import Image, ImageChops
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
book=json.load(io.open(os.path.join(ROOT,'build','photos.json'),encoding='utf-8'))
CELL=200
bad=tot=0
for tid,b in book.items():
    sheet=Image.open(os.path.join(ROOT,'dist','img',tid+'.jpg')).convert('RGB')
    W,H=sheet.size
    for w,i in b['cells'].items():
        col,row=i%b['cols'], i//b['cols']
        # mo phong dung phep tinh cua trinh duyet:
        # background-size: cols*100% x rows*100%  ->  anh phong to bang co luoi
        # background-position: x% y%  ->  lech = x% * (anh - o)
        ew,eh=W/b['cols'], H/b['rows']              # kich thuoc mot o hien thi
        x=(col*100/(b['cols']-1)) if b['cols']>1 else 0
        y=(row*100/(b['rows']-1)) if b['rows']>1 else 0
        ox=x/100*(W-ew); oy=y/100*(H-eh)
        crop=sheet.crop((round(ox),round(oy),round(ox+ew),round(oy+eh)))
        src=os.path.join(ROOT,'build','imgcache',w.replace('/','_')+'.jpg')
        if not os.path.exists(src): continue
        orig=Image.open(src).convert('RGB').resize(crop.size)
        diff=ImageChops.difference(crop,orig)
        mean=sum(sum(ch.getdata())/ (crop.size[0]*crop.size[1]) for ch in diff.split())/3
        tot+=1
        if mean>12:
            bad+=1
            if bad<=5: print('  lech: %s (o %d, sai lech trung binh %.1f)'%(w,i,mean))
print('kiem tra %d o, lech %d'%(tot,bad))
sys.exit(1 if bad else 0)
