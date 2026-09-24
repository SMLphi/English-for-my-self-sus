// Kiem tra module lo trinh: sinh ke hoach, kiem tra trinh do, danh dau hoan thanh.
const fs = require('fs'), path = require('path'), { JSDOM } = require('jsdom');
const html = fs.readFileSync(path.join(__dirname, '..', 'dist', 'index.html'), 'utf8');
const errors = [];
const dom = new JSDOM('<!doctype html><html><head></head><body>' + html + '</body></html>', {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://local.test/',
  beforeParse(w) {
    w.speechSynthesis = { getVoices: () => [], speak() {}, cancel() {} };
    w.SpeechSynthesisUtterance = function () {};
    w.scrollTo = () => {}; w.confirm = () => true;
    w.onerror = m => errors.push(String(m));
  },
});
const w = dom.window, d = w.document, E = x => w.eval(x);
const tick = () => new Promise(r => setTimeout(r, 0));
let bad = 0, passed = 0;
const fail = m => { bad++; console.log('  LOI ' + m); };
const okc = m => { passed++; console.log('  ok  ' + m); };

(async () => {
  await tick();
  const X = E('EXAM');
  if (!X || !X.toeic || !X.ielts) { fail('thieu du lieu ky thi'); return done(); }
  okc('du lieu ky thi: ' + Object.keys(X).map(k => X[k].short + ' (' + X[k].parts.length + ' phan)').join(', '));

  E('go')('plan'); await tick();
  d.querySelector('[data-ex]') ? okc('man hinh thiet lap lo trinh hien ra') : fail('khong thay man hinh thiet lap');

  // sinh lo trinh cho ca hai ky thi, nhieu cau hinh
  for (const [exam, target, weeks, hours] of [['toeic', 700, 12, 7], ['ielts', 6.5, 8, 10], ['toeic', 900, 24, 4]]) {
    try {
      const plan = E('buildPlan')({ exam, target, weeks, hours, level: 'B1' });
      if (plan.weekList.length !== weeks) { fail(exam + ': so tuan sai ' + plan.weekList.length); continue; }
      const nv = plan.weekList.reduce((n, wk) => n + wk.vocab.reduce((m, v) => m + (v.to - v.from), 0), 0);
      const ng = plan.weekList.reduce((n, wk) => n + wk.grammar.length, 0);
      const ns = plan.weekList.reduce((n, wk) => n + wk.skills.length, 0);
      const tests = plan.weekList.filter(wk => wk.test).length;
      // moi tuan phai co viec de lam
      const empty = plan.weekList.filter(wk => !wk.vocab.length && !wk.grammar.length && !wk.skills.length).length;
      // chuyen de ngu phap khong duoc lap lai
      const gids = plan.weekList.flatMap(wk => wk.grammar);
      const dupG = gids.length !== new Set(gids).size;
      // lat tu vung khong duoc chong nhau
      const seen = new Set(); let overlap = 0;
      plan.weekList.forEach(wk => wk.vocab.forEach(v => {
        for (let i = v.from; i < v.to; i++) { const k = v.t + ':' + i; if (seen.has(k)) overlap++; seen.add(k); }
      }));
      if (empty) fail(exam + ': ' + empty + ' tuan trong rong');
      else if (dupG) fail(exam + ': chuyen de ngu phap bi lap');
      else if (overlap) fail(exam + ': ' + overlap + ' tu bi xep trung tuan');
      else if (tests < 1) fail(exam + ': khong co moc thi thu');
      else okc(`${X[exam].short} ${target} / ${weeks} tuan / ${hours}h: ${nv} tu, ${ng} chuyen de, ${ns} nhiem vu, ${tests} moc thi thu`);
    } catch (e) { fail(exam + ': ' + e.message); }
  }

  // muc tieu cao phai keo theo nhieu ngu phap hon muc tieu thap
  const lo = E('grammarForTarget')('toeic', 450).length, hi = E('grammarForTarget')('toeic', 900).length;
  hi > lo ? okc('muc tieu cao doi hoi nhieu ngu phap hon (' + lo + ' → ' + hi + ' chuyen de)')
          : fail('so chuyen de khong tang theo muc tieu');

  // thu tu chu de phai khac nhau giua hai ky thi
  (X.toeic.topicOrder[0] !== X.ielts.topicOrder[0])
    ? okc('thu tu chu de khac nhau theo ky thi (TOEIC bat dau ' + X.toeic.topicOrder[0] + ', IELTS ' + X.ielts.topicOrder[0] + ')')
    : fail('hai ky thi dung chung thu tu chu de');

  // luu va hien thi lo trinh
  try {
    E('PLAN = buildPlan({exam:"toeic",target:700,weeks:6,hours:7,level:"B1"}); savePlan();');
    E('go')('plan'); await tick();
    // 4 tuan mot trang: trang 1 co 4 tuan, trang 2 co 2 tuan
    const weeks = d.querySelectorAll('#weeks .card').length;
    const pgs = d.querySelectorAll('#weeks .pager [data-p]').length;
    const info = (d.querySelector('#weeks .pg-info') || {}).textContent || '';
    weeks === 4 && /1–4 \/ 6 tuần/.test(info) ? okc('lo trinh phan trang: trang 1 hien 4/6 tuan') : fail('trang 1 hien ' + weeks + ' tuan, "' + info + '"');
    d.querySelector('#weeks .pager [data-p="1"]').click(); await tick();
    d.querySelectorAll('#weeks .card').length === 2 ? okc('sang trang 2: 2 tuan con lai') : fail('trang 2 sai');
    d.querySelector('#weeks .pager [data-p="0"]').click(); await tick();
    const rows = d.querySelectorAll('#weeks .wrow').length;
    rows > 10 ? okc(rows + ' dau viec co the danh dau hoan thanh') : fail('qua it dau viec: ' + rows);
    const btns = [...d.querySelectorAll('#weeks .wrow button')].filter(b => b.textContent === '○');
    btns[0].click(); await tick();
    const saved = JSON.parse(w.localStorage.getItem('bnt.plan.v1'));
    Object.keys(saved.done).length === 1 ? okc('danh dau hoan thanh duoc luu lai')
                                         : fail('khong luu duoc trang thai hoan thanh');
    E('go')('home'); await tick();
    /Lộ trình/.test(d.querySelector('#view').textContent) ? okc('trang Hom nay hien thi tien do lo trinh')
                                                          : fail('trang chu khong hien lo trinh');
  } catch (e) { fail('luu lo trinh: ' + e.message); }

  // kiem tra trinh do
  try {
    E('startPlacement()'); await tick();
    const n = E('QUIZ').qs.length;
    let guard = 0;
    while (E('QUIZ') && E('QUIZ').i < n && guard++ < 30) {
      const cur = E('QUIZ').qs[E('QUIZ').i];
      d.querySelectorAll('.opt')[cur.e.a].click(); await tick();
    }
    const txt = d.querySelector('#view').textContent;
    (/Trình độ ước tính/.test(txt) && /C1/.test(txt))
      ? okc('kiem tra trinh do: dung het ' + n + ' cau → xep C1, co uoc luong diem ca hai ky thi')
      : fail('ket qua kiem tra trinh do sai: ' + txt.slice(0, 80));
  } catch (e) { fail('kiem tra trinh do: ' + e.message); }

  done();
  function done() {
    errors.forEach(fail);
    console.log(bad ? '\n== ' + bad + ' LOI ==' : '\n== ' + passed + ' MUC DEU DAT ==');
    process.exit(bad ? 1 : 0);
  }
})();
