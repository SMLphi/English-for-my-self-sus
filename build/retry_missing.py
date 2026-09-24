# -*- coding: utf-8 -*-
import json, io, os, sys, time, importlib.util
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from overrides import OVERRIDE, BLOCK
spec = importlib.util.spec_from_file_location('fi', os.path.join(HERE, 'fetch_images.py'))
fi = importlib.util.module_from_spec(spec); spec.loader.exec_module(fi)
META = os.path.join(ROOT, 'build', 'imgmeta.json')
meta = json.load(io.open(META, encoding='utf-8'))
missing = json.load(io.open(os.path.join(ROOT, 'build', 'missing.json'), encoding='utf-8'))
missing = [(t, w) for t, w in missing if w not in BLOCK and w not in OVERRIDE]
words = [w for _, w in missing]
print('tra lai %d tu' % len(words), flush=True)

found = {}
for i in range(0, len(words), 40):
    chunk = words[i:i+40]
    for attempt in range(3):
        got = fi.batch_titles(chunk)
        if got: break
        time.sleep(4)
    found.update(got)
    print('  %d/%d -> khop %d' % (min(i+40, len(words)), len(words), len(found)), flush=True)
    time.sleep(1.2)

# tu nao van khong khop -> tim kiem voi goi y chu de
hint = {w: fi.HINT.get(t, '') for t, w in missing}
rest = [] if os.environ.get('NO_SEARCH') else [w for w in words if w not in found]
if rest:
    print('  tim kiem cho %d tu con lai...' % len(rest), flush=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        for w, res in ex.map(lambda x: fi.search_one(x, hint.get(x, '')), rest):
            if res: found[w] = res
    print('  sau tim kiem: khop %d' % len(found), flush=True)

jobs = [(w, u, t) for w, (u, t) in found.items()]
print('  tai %d anh...' % len(jobs), flush=True)
done = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    for w, rec in ex.map(fi.download, jobs):
        meta[w] = rec; done += 1
json.dump(meta, io.open(META, 'w', encoding='utf-8'), ensure_ascii=False)
print('XONG: them %d anh' % done, flush=True)
