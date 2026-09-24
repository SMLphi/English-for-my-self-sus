# -*- coding: utf-8 -*-
"""Doi chieu bo tu trong app voi danh sach Oxford 3000 goc."""
import json, io, glob, os, re, collections, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ox=json.load(io.open(os.path.join(ROOT,'build','oxford3000.json'),encoding='utf-8'))

def norm(s): return re.sub(r'\s+',' ',s.replace(' ',' ').strip().lower().replace('’',"'").replace('‘',"'"))
# Oxford ghi mot so muc dang "a, an" -> tach thanh nhieu tu khoa
ox_keys={}
for k,v in ox.items():
    for part in [x.strip() for x in k.split(',')]:
        part=re.sub(r'\s*\(.*?\)','',part).strip()
        part=re.sub(r'\d+$','',part).strip()
        if part: ox_keys.setdefault(norm(part),v)

mine={}
for f in sorted(glob.glob(os.path.join(ROOT,'data','t*.json'))):
    d=json.load(io.open(f,encoding='utf-8'))
    for a in d['words']:
        mine.setdefault(norm(a[0]),d['id'])

hit=[w for w in mine if w in ox_keys]
extra=sorted(w for w in mine if w not in ox_keys)
missing=sorted(w for w in ox_keys if w not in mine)

print('BO TU TRONG APP        : %d tu (18 chu de)'%len(mine))
print('OXFORD 3000 GOC        : %d muc -> %d tu khoa'%(len(ox),len(ox_keys)))
print()
print('PHU DUOC               : %d / %d  (%.1f%% Oxford 3000)'%(len(hit),len(ox_keys),len(hit)/len(ox_keys)*100))
print('CO TRONG APP, KHONG CO TRONG OXFORD: %d tu (%.1f%% bo app)'%(len(extra),len(extra)/len(mine)*100))
print('THIEU SO VOI OXFORD    : %d tu'%len(missing))
print()
lv=collections.Counter(ox_keys[w]['cefr'] for w in missing)
tot=collections.Counter(v['cefr'] for v in ox_keys.values())
print('Thieu theo trinh do:')
for l in ['A1','A2','B1','B2']:
    print('   %s: thieu %4d / %4d  (da co %4d)'%(l,lv[l],tot[l],tot[l]-lv[l]))
print()
print('30 tu THIEU o trinh do A1 (co ban nhat, dang le phai co):')
print('   '+', '.join(w for w in missing if ox_keys[w]['cefr']=='A1')[:600])
print()
print('30 tu app co ma Oxford khong co:')
print('   '+', '.join(extra[:60]))
json.dump({'missing':{w:ox_keys[w] for w in missing},'extra':extra},
          io.open(os.path.join(ROOT,'build','oxford_gap.json'),'w',encoding='utf-8'),ensure_ascii=False)
