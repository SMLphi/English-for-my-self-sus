// Chay app trong DOM gia de bat loi khoi dong + kiem tra logic hoc tap.
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'dist', 'index.html'), 'utf8');

const errors = [];
const dom = new JSDOM('<!doctype html><html><head></head><body>' + html + '</body></html>', {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'https://local.test/',
  beforeParse(w) {
    w.speechSynthesis = { getVoices: () => [], speak() {}, cancel() {} };
    w.SpeechSynthesisUtterance = function () {};
    w.scrollTo = () => {};
    w.confirm = () => true;
    w.onerror = (m) => errors.push(String(m));
  },
});
const w = dom.window, d = w.document;
const E = (x) => w.eval(x);
const tick = () => new Promise(r => setTimeout(r, 0));
w.addEventListener('error', e => errors.push(String(e.message || e.error)));

let bad = 0, passed = 0;
const fail = (m) => { bad++; console.log('  LOI ' + m); process.exitCode = 1; };
const okc = (m) => { passed++; console.log('  ok  ' + m); };
const finish = () => {
  errors.forEach(fail);
  console.log(bad ? '\n== ' + bad + ' LOI ==' : '\n== ' + passed + ' MUC DEU DAT ==');
  process.exit(bad ? 1 : 0);
};
process.on('uncaughtException', e => { fail('ngoai le: ' + e.message); finish(); });

(async () => {
  await tick();

  const view = d.querySelector('#view');
  if (!view || !view.innerHTML.trim()) { fail('trang Hom nay rong'); return finish(); }
  okc('trang Hom nay dung duoc');

  const W = E('WORDS'), T = E('TOPICS');
  if (!W || W.length < 1000) { fail('thieu tu vung'); return finish(); }
  okc(T.length + ' chu de - ' + W.length + ' tu');
  if (W.some(x => !x.pic)) fail('co tu thieu bieu tuong'); else okc('moi tu deu co bieu tuong');
  const badIpa = W.filter(x => !/^\/.*\/$/.test(x.ipa)).length;
  if (badIpa) fail(badIpa + ' tu co IPA sai dinh dang'); else okc('IPA dung dinh dang o ca ' + W.length + ' tu');
  const badVi = W.filter(x => !x.vi || !x.ex || !x.exvi).length;
  if (badVi) fail(badVi + ' tu thieu nghia hoac vi du'); else okc('moi tu deu co nghia + cau vi du song ngu');

  for (const v of ['topics', 'browse', 'stats', 'settings', 'home']) {
    try {
      E('go')(v); await tick();
      const r = d.querySelector('#view');
      if (!r || r.innerHTML.length < 80) fail('man hinh ' + v + ' rong'); else okc('man hinh ' + v);
    } catch (e) { fail('man hinh ' + v + ': ' + e.message); }
  }

  const id = W[0].id, ivs = [];
  [4, 4, 4, 4].forEach(q => { E('grade')(id, q, 'read'); ivs.push(E('P')[id].i); });
  if (ivs[0] === 1 && ivs[1] === 6 && ivs[2] > 6 && ivs[3] > ivs[2])
    okc('SM-2 gian cach tang dan: ' + ivs.join(' -> ') + ' ngay');
  else fail('khoang lap SM-2 sai: ' + ivs);
  const e0 = E('P')[id].e;
  E('grade')(id, 0, 'read');
  if (E('P')[id].i === 0 && E('P')[id].r === 0)
    okc('nut "Lai" dat lai the, ease ' + e0.toFixed(2) + ' -> ' + E('P')[id].e.toFixed(2));
  else fail('nut "Lai" khong dat lai the');

  for (const forced of ['auto', 'flash', 'listen', 'write', 'speak']) {
    try {
      E('P = {}'); E('S').mode = forced; E('S').goalNew = 5; E('S').goalRev = 5;
      E('startSession')(T[1].id); await tick();
      if (!E('SES')) { fail('khong tao duoc phien (' + forced + ')'); continue; }
      const total = E('SES').total;
      let guard = 0, graded = 0;
      while (E('SES') && E('SES').queue.length && guard++ < 120) {
        const cur = E('SES').queue[0].w;
        const host = d.querySelector('#cardHost');
        if (!host || !host.firstChild) { await tick(); continue; }
        const flip = d.querySelector('#flip'); if (flip) { flip.click(); await tick(); }
        const opts = [...d.querySelectorAll('.opt')];
        if (opts.length) { (opts.find(o => o.textContent.includes(cur.vi)) || opts[0]).click(); await tick(); }
        const inp = d.querySelector('#ans');
        if (inp) { inp.value = cur.w; d.querySelector('#chk').click(); await tick(); }
        const g = d.querySelector('.grade');
        if (g && g.children.length) { g.children[g.children.length - 1].click(); graded++; await tick(); }
        else { fail(forced + ': khong hien nut cham diem cho "' + cur.w + '"'); break; }
      }
      const done = d.querySelector('#studyRoot');
      if (graded >= total && done && /Xong phi/.test(done.textContent))
        okc('phien "' + forced + '": cham diem ' + graded + '/' + total + ' the, toi man hinh ket thuc');
      else fail('phien "' + forced + '": cham ' + graded + '/' + total + ' the');
    } catch (e) { fail('phien "' + forced + '": ' + e.message); }
  }


  // --- doi ky nang ngay giua phien ---
  try {
    E('P = {}'); E('S').mode = 'auto'; E('S').goalNew = 4; E('S').goalRev = 4;
    E('startSession')(T[2].id); await tick();
    const want = { flash: '#flip', listen: '.opt', write: '#ans', speak: '.mic,.speak-btn' };
    for (const [sk, sel] of Object.entries(want)) {
      const btn = [...d.querySelectorAll('#sw [data-sk]')].find(b => b.dataset.sk === sk);
      if (!btn) { fail('thieu nut ky nang ' + sk); continue; }
      btn.click(); await tick(); await tick();
      if (d.querySelector(sel)) okc('bam "' + btn.textContent.trim() + '" doi sang dung the');
      else fail('bam ' + sk + ' khong ra the tuong ung');
    }
  } catch (e) { fail('doi ky nang: ' + e.message); }

  // --- tu moi hoc bang the phai duoc luyen viet lai trong cung phien ---
  try {
    E('P = {}'); E('S').mode = 'auto'; E('S').goalNew = 3; E('S').goalRev = 0;
    E('startSession')(T[3].id); await tick();
    const t0 = E('SES').total;
    let guard = 0, sawWrite = false;
    while (E('SES') && E('SES').queue.length && guard++ < 60) {
      if (d.querySelector('#ans')) sawWrite = true;
      const flip = d.querySelector('#flip'); if (flip) { flip.click(); await tick(); }
      const inp = d.querySelector('#ans');
      if (inp) { inp.value = E('SES').queue[0].w.w; d.querySelector('#chk').click(); await tick(); }
      const g = d.querySelector('.grade');
      if (g) { g.children[g.children.length - 1].click(); await tick(); } else break;
    }
    if (sawWrite && E('SES').total > t0) okc('tu moi tu dong quay lai o dang luyen viet (' + t0 + ' -> ' + E('SES').total + ' the)');
    else fail('khong chen buoc luyen viet cho tu moi');
  } catch (e) { fail('xen ke luyen viet: ' + e.message); }

  // --- kho anh that ---
  try {
    const PH = E('PHOTOS'), tids = Object.keys(PH);
    if (!tids.length) fail('khong co kho anh nao');
    else {
      let n = 0, bad = 0;
      for (const t of tids) {
        const b = PH[t];
        for (const [word, i] of Object.entries(b.cells)) {
          n++;
          if (!(i >= 0 && i < b.rows * b.cols)) bad++;
          if (!W.some(x => x.t === t && x.w === word)) bad++;
        }
      }
      if (bad) fail(bad + ' o anh tro sai vi tri hoac sai tu');
      else okc('kho anh: ' + n + ' anh that trong ' + tids.length + ' tam, moi o tro dung tu');
      const w0 = W.find(x => PH[x.t] && PH[x.t].cells[x.w] != null);
      const css = E('photoCss')(w0);
      if (css && /background-image:url\(img\/t\d+\.jpg\)/.test(css) && /background-position:[\d.]+% [\d.]+%/.test(css))
        okc('cong thuc cat o hop le (vi du "' + w0.w + '": ' + css.split('background-position:')[1] + ')');
      else fail('cong thuc cat o sai: ' + css);
      // bieu tuong phai nam DUOI anh, khong duoc de len tren
      const box = E('photoBox')(w0, 160);
      const iFb = box.indexOf('ph-fb'), iImg = box.indexOf('ph-img');
      if (iFb > -1 && iImg > iFb) okc('bieu tuong nam duoi, anh phu len tren (khong de nhau)');
      else fail('thu tu lop anh/bieu tuong sai: ' + box.slice(0, 120));
      E('go')('study');
    }
  } catch (e) { fail('kho anh: ' + e.message); }

  try {
    const n = Object.keys(JSON.parse(w.localStorage.getItem('bnt.progress.v1') || '{}')).length;
    if (n >= 3) okc('tien do luu vao localStorage (' + n + ' the)'); else fail('tien do khong duoc luu (' + n + ')');
  } catch (e) { fail('localStorage: ' + e.message); }

  try {
    E('go')('browse'); await tick();
    const q = d.querySelector('#q'); q.value = 'family';
    q.dispatchEvent(new w.Event('input')); await tick();
    const rows = d.querySelectorAll('.wrow').length;
    if (rows) okc('tra tu: tim "family" ra ' + rows + ' ket qua'); else fail('tra tu khong ra ket qua');
    d.querySelector('.wrow').click(); await tick(); await tick();
    if (d.querySelector('.detail')) okc('mo duoc bang chi tiet tu'); else fail('khong mo duoc chi tiet tu');
    d.querySelector('#dClose') && d.querySelector('#dClose').click();
  } catch (e) { fail('tra tu: ' + e.message); }

  finish();
})();
