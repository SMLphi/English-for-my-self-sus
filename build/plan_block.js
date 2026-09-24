/* ============================================================
   5c. Lộ trình luyện thi TOEIC / IELTS
   ============================================================ */
const EXAM=DATA.exam||{};
const LS_PLAN='bnt.plan.v1';
let PLAN=lsGet(LS_PLAN,null);
function savePlan(){ lsSet(LS_PLAN,PLAN); clearTimeout(saveTimer); saveTimer=setTimeout(cloudPush,4000); }

const LEVEL_ORDER=['A1','A2','B1','B2','C1'];
const fmtDay=n=>{const d=new Date(n*DAY);return d.getDate()+'/'+(d.getMonth()+1);};

/* ---- xếp chuyên đề ngữ pháp theo trình độ cần cho mục tiêu ---- */
function grammarForTarget(examId,target){
  const X=EXAM[examId];
  const ratio=target/X.max;
  const cap=ratio<0.55?'B1':(ratio<0.8?'B2':'C1');
  const capIdx=LEVEL_ORDER.indexOf(cap);
  return GPOINTS.filter(p=>LEVEL_ORDER.indexOf(p.level)<=capIdx)
    .sort((a,b)=>LEVEL_ORDER.indexOf(a.level)-LEVEL_ORDER.indexOf(b.level)||a.id.localeCompare(b.id));
}

/* ---- sinh lộ trình ---- */
function buildPlan(cfg){
  const X=EXAM[cfg.exam];
  const weeks=cfg.weeks, mins=cfg.hours*60;
  // 55% thời gian cho từ vựng, 25% ngữ pháp, 20% kỹ năng thi
  const wordsPerWeek=Math.max(15,Math.round(mins*0.55/1.6));
  const gramPerWeek=Math.max(1,Math.round(mins*0.25/25));
  const topics=X.topicOrder.filter(id=>TOPIC_BY_ID.has(id));
  const gram=grammarForTarget(cfg.exam,cfg.target);

  // hàng đợi từ vựng: từng chủ đề cắt thành các lát
  const vq=[];
  topics.forEach(id=>{
    const n=TOPIC_BY_ID.get(id).words.length;
    for(let i=0;i<n;i+=wordsPerWeek) vq.push({t:id,from:i,to:Math.min(n,i+wordsPerWeek)});
  });
  let vi=0, gi=0, si=0;
  const start=today();
  const weekList=[];
  for(let w=0;w<weeks;w++){
    const r=(w+1)/weeks;
    const phase=r<=0.3?0:(r<=0.6?1:(r<=0.85?2:3));
    const item={week:w+1,from:start+w*7,to:start+w*7+6,phase,vocab:[],grammar:[],skills:[],test:false};
    // từ vựng: lấp đầy hạn mức tuần
    let budget=wordsPerWeek;
    while(budget>0&&vi<vq.length){
      const s=vq[vi];
      const take=Math.min(budget,s.to-s.from);
      item.vocab.push({t:s.t,from:s.from,to:s.from+take});
      budget-=take;
      if(s.from+take>=s.to) vi++; else s.from+=take;
    }
    // ngữ pháp
    for(let k=0;k<gramPerWeek&&gi<gram.length;k++) item.grammar.push(gram[gi++].id);
    // kỹ năng thi: ưu tiên nhiệm vụ đúng giai đoạn
    const pool=X.skills.filter(s=>s.phase===phase);
    const nSkill=phase===3?2:1;
    for(let k=0;k<nSkill&&pool.length;k++) item.skills.push(pool[(si++)%pool.length]);
    item.test=(w+1===Math.round(weeks*0.55))||(w+1===weeks);
    weekList.push(item);
  }
  return {exam:cfg.exam,target:cfg.target,level:cfg.level,weeks,hours:cfg.hours,
          start,created:Date.now(),wordsPerWeek,gramPerWeek,weekList,done:{}};
}

function planProgress(){
  if(!PLAN) return {done:0,total:0,pct:0};
  let total=0,done=0;
  PLAN.weekList.forEach(w=>{
    const n=w.vocab.length+w.grammar.length+w.skills.length+(w.test?1:0);
    total+=n;
    for(let i=0;i<n;i++) if(PLAN.done[w.week+':'+i]) done++;
  });
  return {done,total,pct:total?Math.round(done/total*100):0};
}
function currentWeek(){
  if(!PLAN) return null;
  const d=today();
  return PLAN.weekList.find(w=>d>=w.from&&d<=w.to)||PLAN.weekList.find(w=>d<w.from)||PLAN.weekList[PLAN.weekList.length-1];
}

/* ---- màn hình chính ---- */
function viewPlan(root){
  if(!PLAN) return planSetup(root);
  const X=EXAM[PLAN.exam], pr=planProgress(), cw=currentWeek();
  const band=X.bands.find(b=>PLAN.target>=b.min&&PLAN.target<=b.max)||X.bands[X.bands.length-1];
  root.innerHTML=`<div class="page-h"><div>
      <div class="eyebrow">${X.icon} ${esc(X.name)}</div>
      <h1>Lộ trình ${PLAN.weeks} tuần</h1>
      <p>Mục tiêu <b>${PLAN.target} ${esc(X.unit)}</b> · ${PLAN.hours} giờ mỗi tuần · khoảng ${PLAN.wordsPerWeek} từ và ${PLAN.gramPerWeek} chuyên đề ngữ pháp mỗi tuần.</p></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-sm" id="reset">Tạo lại</button></div></div>
    <div class="stat-row">
      <div class="stat"><b class="mono">${pr.pct}%</b><span>Hoàn thành lộ trình</span></div>
      <div class="stat new"><b class="mono">${cw?cw.week:'—'}</b><span>Tuần hiện tại</span></div>
      <div class="stat"><b class="mono">${pr.done}/${pr.total}</b><span>Đầu việc đã xong</span></div>
      <div class="stat due"><b class="mono">${Math.max(0,PLAN.weeks-(cw?cw.week-1:0))}</b><span>Tuần còn lại</span></div>
    </div>
    <div class="card" style="padding:16px 18px;margin-bottom:22px">
      <div class="eyebrow">Mức bạn đang nhắm tới</div>
      <div style="margin-top:6px;font-size:15px"><b>${esc(band.label)}</b> · tương đương ${esc(band.cefr)} — ${esc(band.desc)}</div>
    </div>
    <div id="weeks"></div>
    <div class="card" style="padding:20px;margin-top:22px">
      <div class="eyebrow" style="margin-bottom:10px">Mẹo theo từng phần thi</div>
      <div id="parts"></div>
    </div>`;
  $('#reset').onclick=()=>{ if(confirm('Xoá lộ trình hiện tại và tạo lại từ đầu?')){PLAN=null;savePlan();render();} };

  const host=$('#weeks');
  PLAN.weekList.forEach(w=>{
    const isNow=cw&&cw.week===w.week;
    const box=el('div','card');
    box.style.cssText='padding:16px 18px;margin-bottom:12px'+(isNow?';border-color:var(--accent);box-shadow:var(--shadow-lift)':'');
    let idx=0;
    const rows=[];
    w.vocab.forEach(v=>{
      const tp=TOPIC_BY_ID.get(v.t);
      rows.push({key:w.week+':'+(idx++),icon:tp.icon,
        title:`${esc(tp.name)} — từ ${v.from+1} đến ${v.to}`,
        sub:X.topicWhy[v.t]?esc(X.topicWhy[v.t]):'',
        act:()=>startSession(v.t)});
    });
    w.grammar.forEach(gidv=>{
      const pt=GP_BY_ID.get(gidv);
      rows.push({key:w.week+':'+(idx++),icon:'📐',
        title:`${esc(pt.name)} <span class="lvl ${pt.level}">${pt.level}</span>`,
        sub:esc(pt.intro.slice(0,110))+'…',
        act:()=>go('lesson',{gid:pt.id})});
    });
    w.skills.forEach(s=>{
      const part=X.parts.find(p=>p.id===s.part);
      rows.push({key:w.week+':'+(idx++),icon:'🎯',
        title:esc(s.task)+(part?` <span class="chip">${esc(part.name.split('—')[0].trim())}</span>`:''),
        sub:esc(s.detail),act:null});
    });
    if(w.test) rows.push({key:w.week+':'+(idx++),icon:'📝',
      title:'Mốc kiểm tra: thi thử một đề đầy đủ',
      sub:'Làm đúng điều kiện phòng thi, chấm điểm và so với mục tiêu để biết còn thiếu bao nhiêu.',act:null});

    const doneN=rows.filter(r=>PLAN.done[r.key]).length;
    box.innerHTML=`<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px">
        <b style="font-size:16px">Tuần ${w.week}</b>
        <span class="mono" style="color:var(--muted);font-size:13px">${fmtDay(w.from)} – ${fmtDay(w.to)}</span>
        ${isNow?'<span class="chip" style="background:var(--accent-soft);color:var(--accent-ink);border-color:transparent">đang học</span>':''}
        <span style="margin-left:auto" class="mono" style="font-size:13px">${doneN}/${rows.length}</span></div>
      <div class="wlist" style="border-radius:10px"></div>`;
    const list=box.querySelector('.wlist');
    rows.forEach(r=>{
      const row=el('div','wrow');
      row.style.cssText='grid-template-columns:auto minmax(0,1fr) auto;align-items:flex-start';
      const checked=!!PLAN.done[r.key];
      row.innerHTML=`<span class="ic">${r.icon}</span>
        <span style="min-width:0"><span class="w" style="font-size:14.5px;${checked?'opacity:.5;text-decoration:line-through':''}">${r.title}</span>
          ${r.sub?`<br><span class="m" style="white-space:normal;font-size:13px;line-height:1.45">${r.sub}</span>`:''}</span>
        <span style="display:flex;gap:6px;align-items:center;flex:none"></span>`;
      const acts=row.lastElementChild;
      if(r.act){ const b=el('button','btn btn-sm','Học'); b.onclick=r.act; acts.appendChild(b); }
      const chk=el('button','btn btn-sm',checked?'✓':'○');
      chk.title='Đánh dấu hoàn thành';
      chk.style.cssText='min-width:36px'+(checked?';background:var(--good-soft);color:var(--good);border-color:transparent':'');
      chk.onclick=()=>{ if(PLAN.done[r.key]) delete PLAN.done[r.key]; else PLAN.done[r.key]=true; savePlan(); render(); };
      acts.appendChild(chk);
      list.appendChild(row);
    });
    host.appendChild(box);
  });

  const ph=$('#parts');
  X.parts.forEach(p=>{
    const d=el('details');
    d.style.cssText='border-bottom:1px solid var(--line);padding:9px 0';
    d.innerHTML=`<summary style="cursor:pointer;font-weight:700;font-size:14.5px">${esc(p.name)}
        <span class="chip" style="margin-left:6px">${esc(p.sec)}</span></summary>
      <ul class="gr-note" style="margin-top:8px">${p.tips.map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`;
    ph.appendChild(d);
  });
}

/* ---- thiết lập lộ trình ---- */
let setupCfg={exam:'toeic',level:null,target:null,weeks:12,hours:7};
function planSetup(root){
  const X=EXAM[setupCfg.exam];
  if(setupCfg.target==null) setupCfg.target=X.defaultTarget;
  root.innerHTML=`<div class="page-h"><div><h1>Lộ trình luyện thi</h1>
    <p>Trả lời bốn câu hỏi, app sẽ xếp lịch từng tuần: học chủ đề từ vựng nào, chuyên đề ngữ pháp nào, và luyện kỹ năng gì cho từng phần thi.</p></div></div>
  <div class="card" style="padding:6px 20px;margin-bottom:16px">
    <div class="set-row"><div><div class="lbl">1. Bạn thi kỳ thi nào?</div>
      <div class="hint">Lộ trình sẽ đổi thứ tự chủ đề và nhiệm vụ kỹ năng theo kỳ thi.</div></div>
      <div class="seg">${Object.keys(EXAM).map(k=>
        `<button data-ex="${k}" aria-pressed="${setupCfg.exam===k}">${EXAM[k].icon} ${esc(EXAM[k].short)}</button>`).join('')}</div></div>
    <div class="set-row"><div><div class="lbl">2. Trình độ hiện tại</div>
      <div class="hint">${setupCfg.level?`Đang chọn: <b>${setupCfg.level}</b>`:'Chưa rõ thì làm bài kiểm tra 10 câu, mất khoảng 3 phút.'}</div></div>
      <div style="display:flex;gap:7px;flex-wrap:wrap;align-items:center">
        <div class="seg">${LEVEL_ORDER.map(l=>`<button data-lv="${l}" aria-pressed="${setupCfg.level===l}">${l}</button>`).join('')}</div>
        <button class="btn btn-sm" id="quiz">Kiểm tra trình độ</button></div></div>
    <div class="set-row"><div><div class="lbl">3. Mục tiêu</div>
      <div class="hint">Mục tiêu càng cao thì lộ trình càng nhiều chuyên đề ngữ pháp nâng cao.</div></div>
      <div class="seg">${X.targets.map(t=>
        `<button data-tg="${t}" aria-pressed="${setupCfg.target===t}">${t}</button>`).join('')}</div></div>
    <div class="set-row"><div><div class="lbl">4. Thời gian</div>
      <div class="hint">Còn bao nhiêu tuần và mỗi tuần học được mấy giờ.</div></div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <label style="font-size:14px">Số tuần <input type="number" id="wk" min="2" max="52" value="${setupCfg.weeks}" style="width:72px"></label>
        <label style="font-size:14px">Giờ/tuần <input type="number" id="hr" min="1" max="40" value="${setupCfg.hours}" style="width:72px"></label></div></div>
  </div>
  <div id="preview"></div>
  <button class="btn btn-primary btn-lg" id="make" style="width:100%">Tạo lộ trình</button>`;

  root.querySelectorAll('[data-ex]').forEach(b=>b.onclick=()=>{setupCfg.exam=b.dataset.ex;setupCfg.target=EXAM[b.dataset.ex].defaultTarget;render();});
  root.querySelectorAll('[data-lv]').forEach(b=>b.onclick=()=>{setupCfg.level=b.dataset.lv;render();});
  root.querySelectorAll('[data-tg]').forEach(b=>b.onclick=()=>{setupCfg.target=+b.dataset.tg;render();});
  $('#wk').onchange=e=>{setupCfg.weeks=Math.max(2,Math.min(52,+e.target.value||12));drawPreview();};
  $('#hr').onchange=e=>{setupCfg.hours=Math.max(1,Math.min(40,+e.target.value||7));drawPreview();};
  $('#quiz').onclick=()=>go('placement');
  $('#make').onclick=()=>{ PLAN=buildPlan({...setupCfg,level:setupCfg.level||'A2'}); savePlan(); render(); toast('Đã tạo lộ trình'); };
  drawPreview();

  function drawPreview(){
    const mins=setupCfg.hours*60;
    const wpw=Math.max(15,Math.round(mins*0.55/1.6));
    const gpw=Math.max(1,Math.round(mins*0.25/25));
    const gram=grammarForTarget(setupCfg.exam,setupCfg.target).length;
    const totalW=WORDS.length;
    const weeksNeeded=Math.ceil(totalW/wpw);
    $('#preview').innerHTML=`<div class="card" style="padding:16px 18px;margin-bottom:16px">
      <div class="eyebrow">Lộ trình sẽ trông như thế này</div>
      <ul class="gr-note" style="margin-top:8px">
        <li>Mỗi tuần khoảng <b>${wpw} từ mới</b> và <b>${gpw} chuyên đề ngữ pháp</b>, cộng 1–2 nhiệm vụ luyện kỹ năng thi.</li>
        <li>Với mục tiêu này cần học <b>${gram}/${GPOINTS.length} chuyên đề ngữ pháp</b> (tới trình độ ${LEVEL_ORDER[Math.min(4,LEVEL_ORDER.indexOf(grammarForTarget(setupCfg.exam,setupCfg.target).slice(-1)[0].level))]}).</li>
        <li>Toàn bộ ${totalW} từ trong app cần <b>${weeksNeeded} tuần</b> ở nhịp này${setupCfg.weeks<weeksNeeded?` — lộ trình ${setupCfg.weeks} tuần của bạn sẽ dừng ở chủ đề ưu tiên cao nhất.`:'.'}</li>
        <li>Có <b>2 mốc thi thử</b>: giữa chặng và tuần cuối.</li>
      </ul></div>`;
  }
}

/* ---- kiểm tra trình độ ---- */
let QUIZ=null;
function startPlacement(){
  const want={A1:2,A2:2,B1:3,B2:2,C1:1};
  const qs=[];
  LEVEL_ORDER.forEach(lv=>{
    const pool=[];
    GPOINTS.filter(p=>p.level===lv).forEach(p=>p.ex.filter(e=>e.t==='mc').forEach(e=>pool.push({p,e})));
    shuffle(pool).slice(0,want[lv]).forEach(x=>qs.push(x));
  });
  QUIZ={qs,i:0,right:0,byLevel:{}};
  LEVEL_ORDER.forEach(l=>QUIZ.byLevel[l]={n:0,c:0});
  go('placement');
}
function viewPlacement(root){
  if(!QUIZ) { startPlacement(); return; }
  if(QUIZ.i>=QUIZ.qs.length) return placementResult(root);
  const {p,e}=QUIZ.qs[QUIZ.i];
  root.innerHTML=`<div class="page-h" style="margin-bottom:12px"><div><h1 style="font-size:22px">Kiểm tra trình độ</h1>
    <p>Câu ${QUIZ.i+1} / ${QUIZ.qs.length} · chọn đáp án đúng nhất</p></div>
    <button class="btn btn-sm" id="skip">Bỏ qua</button></div>
    <span class="bar" style="display:flex;margin-bottom:18px"><i class="b-known" style="width:${QUIZ.i/QUIZ.qs.length*100}%"></i></span>
    <div class="fc" style="min-height:auto"><div class="q-text">${gapHtml(e.q)}</div>
      <div class="opts" id="o"></div></div>`;
  $('#skip').onclick=()=>{QUIZ=null;go('plan');};
  const ob=$('#o');
  e.o.forEach((opt,i)=>{
    const b=el('button','opt',`<span class="n">${'ABCD'[i]}</span><span>${esc(opt)}</span>`);
    b.onclick=()=>{
      const lv=p.level;
      QUIZ.byLevel[lv].n++;
      if(i===e.a){QUIZ.right++;QUIZ.byLevel[lv].c++;}
      QUIZ.i++; render();
    };
    ob.appendChild(b);
  });
}
function placementResult(root){
  const s=QUIZ.right, n=QUIZ.qs.length;
  const lv=s<=3?'A1':(s<=5?'A2':(s<=7?'B1':(s<=9?'B2':'C1')));
  setupCfg.level=lv;
  const rows=LEVEL_ORDER.map(l=>{
    const r=QUIZ.byLevel[l];
    if(!r.n) return '';
    return `<div class="sb"><span class="lvl ${l}">${l}</span>
      <span class="bar"><i class="b-known" style="width:${r.c/r.n*100}%"></i></span>
      <span class="mono" style="text-align:right">${r.c}/${r.n}</span></div>`;
  }).join('');
  const est=Object.keys(EXAM).map(k=>{
    const X=EXAM[k], b=X.bands.find(x=>x.cefr===lv)||X.bands[0];
    return `<div class="kv"><b>${X.icon} ${esc(X.short)}:</b> ước chừng ${b.min}–${b.max} ${esc(X.unit)} (${esc(b.label)})</div>`;
  }).join('');
  root.innerHTML=`<div class="fc" style="min-height:auto;text-align:center;align-items:center">
    <div style="font-size:50px">${s>=8?'🎉':s>=5?'📈':'📚'}</div>
    <h2 style="font-size:26px;margin-top:8px">Trình độ ước tính: <span class="lvl ${lv}" style="font-size:20px;padding:4px 10px">${lv}</span></h2>
    <p style="color:var(--muted);margin:8px 0 16px">Đúng ${s}/${n} câu ngữ pháp trải đều các trình độ</p>
    <div class="skill-bars" style="width:100%;text-align:left">${rows}</div>
    <div class="fc-body" style="width:100%;text-align:left">${est}
      <div class="kv" style="margin-top:4px;color:var(--faint)">Đây chỉ là ước lượng dựa trên ngữ pháp, chưa tính kỹ năng nghe và đọc. Hãy coi là điểm khởi đầu để xếp lộ trình.</div></div>
    <button class="btn btn-primary btn-lg" id="ok" style="margin-top:18px">Dùng kết quả này</button></div>`;
  $('#ok').onclick=()=>{QUIZ=null;go('plan');};
}

