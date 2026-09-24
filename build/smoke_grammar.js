// Kiem tra module ngu phap: du lieu, man hinh, va chay tron mot phien luyen.
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

const norm = s => String(s).toLowerCase().replace(/[’`]/g, "'")
  .replace(/\s+/g, ' ').replace(/\s*([.,!?])\s*/g, '$1').replace(/[.!]+$/, '').trim();

(async () => {
  await tick();
  const GP = E('GPOINTS'), GR = E('GRAMMAR');
  if (!GP || GP.length !== 50) { fail('so chuyen de sai: ' + (GP && GP.length)); return done(); }
  okc(GR.length + ' nhom - ' + GP.length + ' chuyen de - ' + GP.reduce((n, p) => n + p.ex.length, 0) + ' bai tap');

  const lv = {};
  GP.forEach(p => lv[p.level] = (lv[p.level] || 0) + 1);
  okc('phan bo trinh do: ' + Object.entries(lv).map(([k, v]) => k + '=' + v).join(' '));

  E('go')('grammar'); await tick();
  const items = d.querySelectorAll('.gr-item').length;
  items === 50 ? okc('man hinh Ngu phap liet ke du ' + items + ' chuyen de') : fail('liet ke ' + items + '/50');

  d.querySelector('.gr-item').click(); await tick();
  const hasForms = d.querySelector('.gr-forms'), hasTrap = d.querySelector('.gr-trap');
  (hasForms && hasTrap) ? okc('trang bai hoc co bang cong thuc va muc loi hay mac')
                        : fail('trang bai hoc thieu phan');

  // chay tron mot phien luyen cho 4 chuyen de, tra loi dung het
  for (const pid of ['g01', 'g16', 'g34', 'g49']) {
    try {
      E('P = {}');
      E('startDrill')([pid]); await tick();
      const total = E('DRILL').total;
      let guard = 0;
      while (E('DRILL') && E('DRILL').i < total && guard++ < 40) {
        const cur = E('DRILL').queue[E('DRILL').i], e = cur.e;
        if (e.t === 'mc') {
          d.querySelectorAll('.opt')[e.a].click();
        } else if (e.t === 'fill' || e.t === 'fix') {
          const inp = d.querySelector('#ans'); inp.value = e.a[0];
          d.querySelector('#chk').click();
        } else if (e.t === 'order') {
          const want = e.a.split(' ');
          let pos = 0, guard2 = 0;
          while (pos < want.length && guard2++ < 30) {
            const tiles = [...d.querySelectorAll('#tiles .tile')].filter(t => !t.className.includes('used'));
            const hit = tiles.find(t => {
              const tw = t.textContent.split(' ');
              return tw.every((x, k) => (want[pos + k] || '').toLowerCase() === x.toLowerCase());
            });
            if (!hit) break;
            pos += hit.textContent.split(' ').length;
            hit.click();
          }
          d.querySelector('#chk').click();
        }
        await tick();
        const fb = d.querySelector('.feedback');
        if (!fb) { fail(pid + ': khong hien phan hoi cho bai ' + e.t); break; }
        if (!/Chính xác/.test(fb.textContent)) fail(pid + ' (' + e.t + '): tra loi dung nhung bi cham sai');
        if (!d.querySelector('.why-box')) fail(pid + ': thieu phan giai thich');
        const nx = [...d.querySelectorAll('button')].find(b => b.textContent === 'Tiếp theo');
        if (!nx) { fail(pid + ': thieu nut Tiep theo'); break; }
        nx.click(); await tick();
      }
      const doneScreen = d.querySelector('#studyRoot');
      const graded = E('P')['G:' + pid];
      if (doneScreen && /Xong phi/.test(doneScreen.textContent) && graded && graded.i >= 1)
        okc('phien "' + E('GP_BY_ID').get(pid).name + '": ' + total + ' bai, dung het, lich on sau ' + graded.i + ' ngay');
      else fail(pid + ': khong ket thuc dung (graded=' + JSON.stringify(graded) + ')');
    } catch (err) { fail(pid + ': ' + err.message); }
  }

  // tra loi sai phai bi cham la sai
  try {
    E('P = {}'); E('startDrill')(['g01']); await tick();
    let guard = 0;
    while (E('DRILL') && E('DRILL').i < E('DRILL').total && guard++ < 40) {
      const e = E('DRILL').queue[E('DRILL').i].e;
      if (e.t === 'mc') d.querySelectorAll('.opt')[(e.a + 1) % e.o.length].click();
      else if (e.t === 'order') { d.querySelector('#tiles .tile').click(); d.querySelector('#chk').click(); }
      else { d.querySelector('#ans').value = 'xxx'; d.querySelector('#chk').click(); }
      await tick();
      const nx = [...d.querySelectorAll('button')].find(b => b.textContent === 'Tiếp theo');
      if (!nx) break;
      nx.click(); await tick();
    }
    const g = E('P')['G:g01'];
    (g && g.i === 0 && g.r === 0) ? okc('tra loi sai het thi chuyen de bi dat lai de on som')
                                  : fail('cham diem khi sai khong dung: ' + JSON.stringify(g));
  } catch (err) { fail('kiem tra tra loi sai: ' + err.message); }

  done();
  function done() {
    errors.forEach(fail);
    console.log(bad ? '\n== ' + bad + ' LOI ==' : '\n== ' + passed + ' MUC DEU DAT ==');
    process.exit(bad ? 1 : 0);
  }
})();
