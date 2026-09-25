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
    w.speechSynthesis = { getVoices: () => [], speak(u) { (w.__said = w.__said || []).push(u); }, cancel() {} };
    w.SpeechSynthesisUtterance = function (t) { this.text = t; };
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
  okc(T.length + ' chu de con - ' + W.length + ' tu');
  // 40 chu de lon (18 doi song + 22 tu loai & cap do), chia thanh chu de con <= 30 tu
  {
    const GR = E('GROUPS'), big = T.filter(t => t.words.length > 30), orphan = T.filter(t => !E('GROUP_BY_ID').has(t.group));
    const inG = new Set(GR.flatMap(g => g.lessons)), ids = new Set(W.map(x => x.id));
    GR.filter(g => g.kind === 'theme').length === 18 && GR.filter(g => g.kind === 'level').length === 22
      ? okc('40 chu de lon: 18 doi song + 22 tu loai & cap do') : fail('so chu de lon sai');
    !big.length && !orphan.length && inG.size === T.length && ids.size === W.length
      ? okc('moi chu de con <= 30 tu, deu thuoc mot chu de lon, khong trung') : fail('chu de con qua lon/khong nhom: ' + big.map(t => t.id) + orphan.map(t => t.id));
    const t01 = GR.find(g => g.id === 't01'), names = t01.lessons.map(id => E('TOPIC_BY_ID').get(id).name);
    names.includes('Khuôn mặt') && names.includes('Dáng người') && names.includes('Con người & giới tính')
      ? okc('Con nguoi & ngoai hinh -> ' + names.length + ' chu de con: ' + names.join(', ')) : fail('tach t01 sai: ' + names);
  }
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

  // --- lap lai ngat quang kieu Anki, thu tren chu de con dau tien (Con nguoi & gioi tinh) ---
  const L1 = T[0].id, t01 = W.filter(x => x.t === L1);
  const id = t01[0].id, NL = E('nextLabel');
  const lab = () => [0, 3, 4, 5].map(q => NL(id, q)).join(' / ');
  const l1 = lab();
  l1 === '1 phút / 6 phút / 10 phút / 4 ngày' ? okc('tu moi: Lai/Kho/Tot/De = ' + l1) : fail('nhan tu moi sai: ' + l1);
  E('grade')(id, 4, 'read');                      // Tot -> buoc 10 phut
  const l2 = lab();
  l2 === '1 phút / 10 phút / 1 ngày / 4 ngày' ? okc('lan 2 trong phien: ' + l2) : fail('nhan lan 2 sai: ' + l2);
  E('P')[id].due > Date.now() + 9 * 60000 ? okc('the hen 10 phut co gio hen that') : fail('khong co gio hen phut');
  E('grade')(id, 4, 'read');                      // tot nghiep -> 1 ngay
  const ivs = [E('P')[id].i];
  for (let k = 0; k < 3; k++) {
    const hk = [3, 4, 5].map(q => E('schedule')(E('P')[id], q).i);
    if (!(hk[0] < hk[1] && hk[1] < hk[2])) fail('lan on ' + (k + 1) + ': Kho/Tot/De khong tang dan ' + hk);
    E('grade')(id, 4, 'read'); ivs.push(E('P')[id].i);
  }
  ivs.every((v, k) => !k || v > ivs[k - 1]) ? okc('on theo ngay tang dan: ' + ivs.join(' -> ') + ' ngay; luon Kho < Tot < De') : fail('khoang on sai ' + ivs);
  const e0 = E('P')[id].e;
  E('grade')(id, 0, 'read');
  const P0 = E('P')[id];
  P0.s === 3 && P0.r === 0 && P0.e < e0 && E('nextLabel')(id, 4) === '1 ngày' && P0.due > Date.now()
    ? okc('quen tu da thuoc -> hoc lai sau 10 phut, ease ' + e0.toFixed(2) + ' -> ' + P0.e.toFixed(2))
    : fail('bam Lai tren the dang on sai ' + JSON.stringify(P0));
  // ngu phap cham theo ca bai: chi tinh ngay, van Kho < Tot < De
  const gq = [3, 4, 5].map(q => E('schedule')(null, q, true).i);
  gq.join() === '1,3,5' ? okc('ngu phap moi: Kho/Tot/De = ' + gq.join('/') + ' ngay') : fail('ngu phap sai ' + gq);

  // --- trong phien: bam Lai thi the quay lai khi toi gio, khong mat the ---
  try {
    E('startSession')(L1); await tick(); await tick();
    const first = E('SES').queue[0].w.id, n0 = E('SES').queue.length;
    E('advance')(E('SES').queue[0].w, 0, 'read'); await tick();
    const back = E('SES').queue.find(x => x.w.id === first);
    back && back.at > Date.now() && E('SES').queue.length === n0 && E('SES').queue[0].w.id !== first
      ? okc('phien hoc: bam Lai -> the hen 1 phut, xep sau cac the khac') : fail('the bi Lai khong quay lai dung');
    back.at = Date.now() - 1; E('renderStudy')(); await tick();
    E('SES').queue[0].w.id === first ? okc('toi gio -> the do duoc hien lai truoc') : fail('the toi gio khong duoc uu tien');
    E('SES = null');
  } catch (e) { fail('phien hoc: ' + e.message); }

  // --- tien do cua bo chu de cu (t05:bed) chuyen sang bai moi chua dung tu do ---
  {
    const bed = W.find(x => x.w === 'bed'), src = { 't05:bed': { t: 1, i: 3 }, 'G:g01': { t: 1 }, 't99:khongco': { t: 1 } };
    const n = E('migrateProgress')(src);
    n === 1 && src[bed.id] && src[bed.id].i === 3 && !src['t05:bed'] && src['G:g01']
      ? okc('chuyen tien do cu: t05:bed -> ' + bed.id + ', giu tien do ngu phap') : fail('chuyen tien do sai ' + JSON.stringify(src));
  }

  // --- nghe lai cung cau -> doc cham, lan nua -> binh thuong ---
  w.__said = [];
  const sp = E('speak'), r0 = E('S').rate;
  sp('beard'); sp('beard'); sp('beard'); sp('chin');
  const rates = w.__said.map(u => u.rate);
  rates[0] === r0 && rates[1] < r0 && rates[2] === r0 && rates[3] === r0
    ? okc('nghe lai: thuong ' + r0 + ' -> cham ' + rates[1] + ' -> thuong; tu khac doc thuong')
    : fail('toc do nghe lai sai: ' + rates);

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
      if (css && /background-image:url\(img\/t\d+[a-z]?\.jpg\)/.test(css) && /background-position:[\d.]+% [\d.]+%/.test(css))
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
    // bo loc rong -> 40 tu/trang, co phan trang
    q.value = ''; q.dispatchEvent(new w.Event('input')); await tick();
    const all = d.querySelectorAll('#res .wrow').length, info = (d.querySelector('#res .pg-info') || {}).textContent || '';
    all === 40 && /1–40 \//.test(info) ? okc('tra tu phan trang: 40 tu/trang (' + info + ')') : fail('tra tu phan trang sai: ' + all + ' ' + info);
    E('go')('topics'); await tick();
    const secs = d.querySelectorAll('.tgroup').length, info2 = (d.querySelector('.pg-info') || {}).textContent || '';
    secs === 5 && /1–5 \/ 18 chủ đề/.test(info2) ? okc('trang Chu de: 5 chu de lon/trang (' + info2 + ')') : fail('trang Chu de hien ' + secs + ' nhom, ' + info2);
    d.querySelector('#tTabs [data-tab="level"]').click(); await tick();
    const ox = d.querySelector('.tgroup h2').textContent;
    /Từ chức năng/.test(ox) ? okc('tab Tu loai & cap do: ' + ox + ', ' + d.querySelectorAll('.tgroup .topic').length + ' chu de con') : fail('tab tu loai sai: ' + ox);
    E('go')('home'); await tick(); E('go')('topics'); await tick();
    d.querySelector('#tTabs [aria-pressed="true"]').dataset.tab === 'level' ? okc('quay lai van o tab da chon') : fail('khong nho tab');
    E('PAGES').topicsTab = 'theme';
    E('go')('browse'); await tick();
    d.querySelector('.wrow').click(); await tick(); await tick();
    if (d.querySelector('.detail')) okc('mo duoc bang chi tiet tu'); else fail('khong mo duoc chi tiet tu');
    d.querySelector('#dClose') && d.querySelector('#dClose').click();
  } catch (e) { fail('tra tu: ' + e.message); }

  finish();
})();
