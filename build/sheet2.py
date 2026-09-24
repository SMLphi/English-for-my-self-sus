# -*- coding: utf-8 -*-
import json, urllib.parse, urllib.request, io, sys, time
from PIL import Image, ImageDraw
UA={'User-Agent':'BaNghinTu/1.0 (personal vocabulary study app; contact: local user)'}
API='https://en.wikipedia.org/w/api.php'
def api(params):
    u=API+'?'+urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25))
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(2+attempt*3); continue
            raise
    return {}

def page_image(title):
    d=api({'action':'query','format':'json','formatversion':'2','redirects':'1',
           'titles':title,'prop':'pageimages|pageprops','piprop':'thumbnail',
           'pithumbsize':'400'})
    for p in d.get('query',{}).get('pages',[]):
        if 'disambiguation' in (p.get('pageprops') or {}): return None,'(disambig)'
        if p.get('thumbnail'): return p['thumbnail']['source'], p.get('title')
    return None,None

def search_image(q):
    d=api({'action':'query','format':'json','formatversion':'2','generator':'search',
           'gsrsearch':q,'gsrlimit':'3','gsrnamespace':'0','prop':'pageimages|pageprops',
           'piprop':'thumbnail','pithumbsize':'400'})
    pages=sorted(d.get('query',{}).get('pages',[]),key=lambda p:p.get('index',9))
    for p in pages:
        if 'disambiguation' in (p.get('pageprops') or {}): continue
        if p.get('thumbnail'): return p['thumbnail']['source'], p.get('title')
    return None,None

def get(word,hint=''):
    for t in [word.capitalize(), word.lower()]:
        u,title=page_image(t)
        if u: return u,title
        time.sleep(.4)
    return search_image((word+' '+hint).strip())

words=[('apple','fruit'),('dog','animal'),('bridge','structure'),('umbrella',''),
       ('stairs',''),('doctor','physician'),('rice','food'),('scissors',''),
       ('kitchen',''),('violin',''),('waterfall',''),('beard',''),
       ('knee','anatomy'),('ambulance',''),('chopsticks',''),('wallet','')]
C=4;S=200
sheet=Image.new('RGB',(C*S,((len(words)+C-1)//C)*(S+22)),'white');dr=ImageDraw.Draw(sheet)
hit=0
for i,(w,h) in enumerate(words):
    x=(i%C)*S;y=(i//C)*(S+22)
    u,title=get(w,h)
    if u:
        try:
            raw=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25).read()
            im=Image.open(io.BytesIO(raw)).convert('RGB');im.thumbnail((S,S))
            cv=Image.new('RGB',(S,S),'#eeeeee');cv.paste(im,((S-im.width)//2,(S-im.height)//2))
            sheet.paste(cv,(x,y));hit+=1
            print('%-12s -> %s'%(w,title))
        except Exception as e: print('%-12s tai loi %s'%(w,str(e)[:50]))
    else:
        dr.rectangle([x,y,x+S,y+S],fill='#dddddd');print('%-12s -> khong co (%s)'%(w,title))
    dr.text((x+4,y+S+5),w,fill='black')
    time.sleep(.6)
sheet.save('build/sheet2.png');print('\nco anh: %d/%d'%(hit,len(words)))
