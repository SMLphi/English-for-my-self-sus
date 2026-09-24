// Kiem tra module hoi thoai: danh sach, to mau tu, nghe ca doan, dong vai, dien tu.
const fs = require('fs'), path = require('path'), { JSDOM } = require('jsdom');
const html = fs.readFileSync(path.join(__dirname, '..', 'dist', 'index.html'), 'utf8');
const errors = [], spoken = [];
const dom = new JSDOM('<!doctype html><html><head></head><body>' + html + '</body></html>', {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://local.test/',
  beforeParse(w) {
    // gia lap TTS: doc xong ngay lap tuc -> kiem tra chuoi doc ca doan
    w.speechSynthesis = { getVoices: () => [], cancel() {},
      speak(u) { spoken.push(u.text); setTimeout(() => u.onend && u.onend(), 0); } };
    w.SpeechSynthesisUtterance = function (t) { this.text = t; };
    w.scrollTo = () => {}; w.confirm = () => true;
    w.Element.prototype.scrollIntoView = () => {};
    w.onerror = m => errors.push(String(m));
  },
});
const w = dom.window, d = w.document, E = x => w.eval(x);
const tick = (ms = 0) => new Promise(r => setTimeout(r, ms));
let bad = 0, passed = 0;
const fail = m => { bad++; console.log('  LOI ' + m); };
const okc = m => { passed++; console.log('  ok  ' + m); };
const $ = s => d.querySelector(s), $$ = s => [...d.querySelectorAll(s)];

(async () => {
  await tick();
  const D = E('DIALOGS'), tids = Object.keys(D);
  if (!tids.length) { fail('khong co du lieu hoi thoai'); return done(); }
  // du lieu: moi cau tieng Anh deu co ban dich, co tieu de
  let nd = 0, miss = [];
  for (const t of tids) for (const x of D[t]) {
    nd++;
    if (!x.title) miss.push(x.id + ' thieu tieu de');
    if (x.en.length !== x.vi.length) miss.push(x.id + ' lech so cau');
    x.vi.forEach((v, i) => { if (!v) miss.push(x.id + ' cau ' + i + ' chua dich'); });
  }
  miss.length ? fail(miss.slice(0, 5).join('; ')) : okc(nd + ' hoi thoai o ' + tids.length + ' chu de, du ban dich');

  const tid = tids[0];
  // nhan dien dang tu: so nhieu, qua khu, so sanh, gach noi
  const tk = s => E('dlgTokens')(s, 't01').filter(x => x.w).map(x => x.s + '>' + x.w.w).join(',');
  const cases = [['She has blue eyes.', 'eyes>eye'], ['He is taller than me.', 'taller>tall'], ['She looks more beautiful.', 'looks>look,beautiful>beautiful'],
                 ['He is tall and slim, fair-haired.', 'tall>tall,slim>slim,fair>fair,haired>hair'],
                 ["That girl's boyfriend", 'girl>girl']];
  const wrong = cases.filter(([s, want]) => tk(s) !== want).map(([s, want]) => s + ' => ' + tk(s) + ' (can ' + want + ')');
  wrong.length ? fail('nhan dien tu: ' + wrong.join(' | ')) : okc('nhan dien dang tu: so nhieu, so sanh, gach noi, so huu');

  // tu moi khong lap giua cac doan; khong to tu ngoai danh sach da duyet (tranh sai nghia)
  {
    const seenNew = new Set(); let dup = [], stray = [], nNew = 0;
    for (const x of D[tid]) {
      const nw = E('dlgNew')(tid, x); nNew += nw.size;
      nw.forEach(v => { if (seenNew.has(v)) dup.push(v); seenNew.add(v); });
      if (!nw.size) dup.push(x.id + ' khong co tu moi');
      const allow = new Set(x.words);
      x.en.forEach(s => E('dlgTokens')(s, tid, E('dlgAllow')(x)).forEach(t => {
        if (t.w && !allow.has(t.w.w.toLowerCase())) stray.push(x.id + ':' + t.s); }));
    }
    dup.length ? fail('tu moi bi lap: ' + dup.slice(0, 5).join(', ')) : okc('moi doan deu co tu moi, khong lap: ' + nNew + ' tu / ' + D[tid].length + ' doan');
    stray.length ? fail('to mau tu chua duyet: ' + stray.slice(0, 5).join(', ')) : okc('chi to mau tu dung nghia da duyet');
    nNew === E('dlgTopicCover')(tid) ? okc('tong tu moi = do phu chu de') : fail('lech do phu ' + nNew);
  }

  // the chu de co nut hoi thoai
  E('go')('topics'); await tick();
  const btn = $$('.topic-dlg')[0];
  btn ? okc('the chu de co nut "' + btn.textContent.trim() + '"') : fail('khong thay nut hoi thoai tren the chu de');
  btn.click(); await tick();
  const cards = $$('.dlg-card');
  const npg = Math.ceil(D[tid].length / 10);
  cards.length === Math.min(10, D[tid].length) && $$('.pager button.pg:not([aria-label])').length >= Math.min(npg, 3)
    ? okc('danh sach phan trang: ' + cards.length + ' doan/trang, ' + npg + ' trang') : fail('phan trang sai: ' + cards.length + ' the');
  E('route').v === 'dialogs' && $('[data-nav="topics"]').getAttribute('aria-current') === 'page'
    ? okc('menu van sang o muc Chu de') : fail('menu khong sang dung muc');

  // doc & nghe: thu tren doan co nhieu tu moi nhat
  const ri = D[tid].reduce((b, x, i) => E('dlgNew')(tid, x).size > E('dlgNew')(tid, D[tid][b]).size ? i : b, 0);
  const DD = D[tid][ri];
  // sang dung trang chua doan do (nut "›" lien tiep)
  for (let k = 0; k < Math.floor(ri / 10); k++) { $('.pager [aria-label="Trang sau"]').click(); await tick(); }
  const onPage = $$('.dlg-card');
  onPage[ri % 10] ? okc('sang trang ' + (Math.floor(ri / 10) + 1) + ' bang nut ›') : fail('khong sang duoc trang');
  onPage[ri % 10].click(); await tick();
  const hl = $$('.dl .dw');
  hl.length ? okc('doan ' + (ri + 1) + ': to mau ' + hl.length + ' tu cua chu de') : fail('khong to mau tu nao');
  hl[0].click(); await tick();
  $('.detail') ? okc('cham tu to mau -> mo the tu "' + $('.detail .fc-word').textContent + '"') : fail('khong mo duoc the tu');
  $('.detail') && $('.detail').remove();
  const bub = $('.dl-bub'), vi = bub.querySelector('.dl-vi');
  bub.click(); !vi.hidden ? okc('cham cau -> hien nghia tieng Viet') : fail('cham cau khong hien nghia');
  spoken.length = 0;
  $('#dPlay').click(); await tick(DD.en.length * 400 + 1500);
  const n0 = DD.en.length;
  spoken.length === n0 && spoken[n0 - 1] === DD.en[n0 - 1]
    ? okc('nghe ca doan: doc lan luot du ' + n0 + ' cau') : fail('nghe ca doan doc ' + spoken.length + '/' + n0 + ' cau');
  $('#dPlay').textContent.includes('Nghe') ? okc('xong thi nut tro ve "Nghe ca doan"') : fail('nut phat khong reset');

  // dong vai: vai B, khong co nhan dang giong -> tu bam Tiep
  $('[data-m="role"]').click(); await tick();
  $$('#rRole [data-r]')[1].click(); await tick(600);
  let steps = 0;
  while (!$('#rSwap') && steps < 60) { const g = $('#rGo'); if (g) g.click(); await tick(20); steps++; }
  const logged = $$('#rLines .dl').length;
  $('#rSwap') && logged === n0 ? okc('dong vai: di het ' + logged + ' luot, co man ket thuc') : fail('dong vai dung o luot ' + logged + '/' + n0);
  $$('#rLines .dl.me').length === Math.floor(n0 / 2) ? okc('luot cua nguoi hoc duoc danh dau "Ban"') : fail('danh dau luot sai');
  // cham diem noi
  const sc = E('sayScore')('She is very tall and slim.', ['she is tall and slim']);
  sc.s === 83 ? okc('cham noi: thieu 1/6 tu -> 83%') : fail('cham noi sai: ' + sc.s);

  // dien tu
  $('[data-m="fill"]').click(); await tick();
  const ins = $$('.gapin');
  ins.length ? okc('dien tu: ' + ins.length + ' cho trong, ngan hang ' + $$('#fBank .tile').length + ' tu') : fail('khong co cho trong');
  const blanks = E('dlgTokens');
  // dien dung het tru o cuoi
  const nw0 = E('dlgNew')(tid, DD);
  const answers = DD.en.flatMap(s => blanks(s, tid, E('dlgAllow')(DD))
    .filter(x => x.w && nw0.has(x.w.w.toLowerCase())).map(x => x.s));
  answers.length === ins.length ? okc('chi che tu moi: ' + ins.length + ' cho') : fail('so cho trong ' + ins.length + ' khac so tu moi ' + answers.length);
  ins.forEach((inp, i) => { inp.value = i < ins.length - 1 ? answers[i] : 'zzz'; });
  $('#fCheck').click(); await tick();
  const okN = $$('.gapin.ok').length, noN = $$('.gapin.no').length;
  okN === ins.length - 1 && noN === 1 && $$('.gap-fix').length === 1
    ? okc('kiem tra: ' + okN + ' dung, 1 sai kem dap an') : fail('cham sai: ok=' + okN + ' no=' + noN);
  // ngan hang tu dien vao o dang chon
  $('#fReset').click(); await tick();
  const f0 = $('.gapin'); f0.focus(); $('#fBank .tile').click();
  f0.value ? okc('cham ngan hang tu -> dien vao o') : fail('ngan hang tu khong dien');

  const p = JSON.parse(w.localStorage.getItem('bnt.dlg.v1') || '{}')[DD.id] || {};
  p.v && p.f != null ? okc('luu tien do: da doc, dien tu ' + p.f + '%') : fail('khong luu tien do ' + JSON.stringify(p));

  // chuyen doan
  $('#dNext').click(); await tick();
  E('route').i === ri + 1 ? okc('nut › sang doan ke tiep') : fail('khong sang doan ke tiep');
  $('#dBack').click(); await tick();
  const cur = $('.pager .pg.on');
  cur && +cur.textContent === Math.floor((ri + 1) / 10) + 1 ? okc('quay lai danh sach dung trang ' + cur.textContent) : fail('quay lai sai trang');
  done();
})();
function done() {
  errors.length ? fail('loi JS: ' + errors.join(' | ')) : okc('khong co loi JS');
  console.log(`\n${passed} dat, ${bad} loi`);
  process.exit(bad ? 1 : 0);
}
