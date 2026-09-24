# -*- coding: utf-8 -*-
import json, urllib.parse, urllib.request, io, sys, time
from PIL import Image, ImageDraw
UA={'User-Agent':'BaNghinTu-vocab-study/1.0 (personal study app)'}
def api(url,t=25):
    return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=t))
def fetch(q,cat='photograph'):
    u=('https://api.openverse.org/v1/images/?q=%s&category=%s&aspect_ratio=square'
       '&license_type=all-cc,commercial&page_size=1&mature=false'%(urllib.parse.quote(q),cat))
    try:
        d=api(u)
        if d.get('results'):
            r=d['results'][0]
            src=r.get('thumbnail') or r.get('url')
            raw=urllib.request.urlopen(urllib.request.Request(src,headers=UA),timeout=25).read()
            return Image.open(io.BytesIO(raw)).convert('RGB'), r.get('license',''), r.get('source','')
    except Exception as e:
        print('  loi',q,str(e)[:70])
    return None,None,None

words=sys.argv[1:] or ['apple','dog','bridge','umbrella','stairs','doctor','rice','scissors',
                       'kitchen','violin','waterfall','beard','knee','ambulance','chopsticks','wallet']
C=4; S=200
sheet=Image.new('RGB',(C*S,((len(words)+C-1)//C)*(S+22)),'white')
dr=ImageDraw.Draw(sheet)
for i,w in enumerate(words):
    im,lic,src=fetch(w)
    x=(i%C)*S; y=(i//C)*(S+22)
    if im:
        im=im.copy(); im.thumbnail((S,S)); 
        cv=Image.new('RGB',(S,S),'#eeeeee'); cv.paste(im,((S-im.width)//2,(S-im.height)//2))
        sheet.paste(cv,(x,y))
        print('%-12s %s / %s'%(w,lic,src))
    else:
        dr.rectangle([x,y,x+S,y+S],fill='#dddddd')
    dr.text((x+4,y+S+5),'%s'%w,fill='black')
    time.sleep(0.2)
sheet.save('build/sheet.png')
print('da luu build/sheet.png',sheet.size)
