/* ============================================================
   5b. Ngữ pháp
   ============================================================ */
const normEn=t=>String(t).toLowerCase().replace(/[’`]/g,"'").replace(/\s+/g,' ')
  .replace(/\s*([.,!?])\s*/g,'$1').replace(/[.!]+$/,'').trim();
const accepts=(ans,val)=>(Array.isArray(ans)?ans:[ans]).some(a=>normEn(a)===normEn(val));

function gstat(p){
  const pr=P[gid(p.id)];
  return {p, done:!!pr, due:!!(pr&&pr.d<=today()), known:!!(pr&&pr.i>=21),
          acc:pr&&pr.n?Math.round(pr.c/pr.n*100):null};
}
function grammarCounts(){
  let done=0,due=0,known=0;
  for(const pt of GPOINTS){const g=gstat(pt);if(g.done)done++;if(g.due)due++;if(g.known)known++;}
  return {done,due,known,total:GPOINTS.length};
}

function viewGrammar(root){
  const c=grammarCounts();
  const nEx=GPOINTS.reduce((n,p)=>n+p.ex.length,0);
  root.innerHTML=`<div class="page-h"><div><h1>Ngữ pháp</h1>
      <p>${GPOINTS.length} chuyên đề từ A1 đến C1 · ${nEx} bài tập. Mỗi chuyên đề có giải thích, bảng công thức, lỗi hay mắc và bài luyện.</p></div>
      <button class="btn btn-primary" id="gAll">${c.due?`Ôn ${c.due} chuyên đề tới hạn`:'Luyện ngẫu nhiên'}</button></div>
    <div class="stat-row">
      <div class="stat due"><b class="mono">${c.due}</b><span>Tới hạn ôn</span></div>
      <div class="stat"><b class="mono">${c.done}</b><span>Đã luyện</span></div>
      <div class="stat"><b class="mono">${c.known}</b><span>Đã vững</span></div>
      <div class="stat new"><b class="mono">${c.total-c.done}</b><span>Chưa học</span></div>
    </div><div id="gGroups"></div>`;
  const host=$('#gGroups');
  GRAMMAR.forEach(g=>{
    const sec=el('div','gr-group');
    sec.innerHTML=`<h2><span>${g.icon}</span>${esc(g.group)}</h2><div class="gr-list"></div>`;
    const list=sec.querySelector('.gr-list');
    g.points.forEach(pt=>{
      const st=gstat(pt);
      const b=el('button','gr-item');
      const dot=st.known?'d-known':st.done?'d-learn':'d-new';
      b.innerHTML=`<div class="top"><span class="lvl ${pt.level}">${pt.level}</span>
          <span class="dot ${dot}" title="${st.known?'đã vững':st.done?'đang học':'chưa học'}"></span></div>
        <h3>${esc(pt.name)}</h3><div class="en">${esc(pt.en)}</div>
        ${st.acc!=null?`<div class="topic-meta">độ chính xác ${st.acc}%${st.due?' · <span style="color:var(--chalk)">tới hạn</span>':''}</div>`:''}`;
      b.onclick=()=>go('lesson',{gid:pt.id});
      list.appendChild(b);
    });
    host.appendChild(sec);
  });
  $('#gAll').onclick=()=>{
    const pool=GPOINTS.filter(pt=>{const g=gstat(pt);return g.due||!g.done;});
    startDrill(shuffle(pool.length?pool:[...GPOINTS]).slice(0,5).map(p=>p.id),true);
  };
}

function viewLesson(root){
  const pt=GP_BY_ID.get(route.gid);
  if(!pt){go('grammar');return;}
  const st=gstat(pt);
  root.innerHTML=`
    <button class="btn btn-sm" id="back" style="margin-bottom:14px">← Ngữ pháp</button>
    <div class="page-h"><div>
      <div style="display:flex;align-items:center;gap:9px;margin-bottom:6px">
        <span class="lvl ${pt.level}">${pt.level}</span><span class="eyebrow">${esc(pt.group)}</span></div>
      <h1>${esc(pt.name)}</h1><p style="font-family:var(--mono);font-size:14px">${esc(pt.en)}</p></div></div>
    <div class="card" style="padding:20px">
      <p style="margin:0;font-size:16px;line-height:1.6">${esc(pt.intro)}</p>
      <div class="gr-sec"><div class="eyebrow">Công thức</div>
        <table class="gr-forms"><tbody>${pt.forms.map(f=>
          `<tr><td>${esc(f[0])}</td><td>${esc(f[1])}</td><td>${esc(f[2])}</td></tr>`).join('')}</tbody></table>
        <button class="btn btn-sm" id="readAll">🔊 Nghe các câu mẫu</button></div>
      <div class="gr-sec"><div class="eyebrow">Cần nhớ</div>
        <ul class="gr-note">${pt.notes.map(n=>`<li>${esc(n)}</li>`).join('')}</ul></div>
      <div class="gr-sec"><div class="eyebrow">Lỗi hay mắc</div>
        ${pt.traps.map(t=>`<div class="gr-trap"><span class="no">${esc(t[0])}</span> → <span class="yes">${esc(t[1])}</span>
          <span class="why">${esc(t[2])}</span></div>`).join('')}</div>
    </div>
    <div style="display:flex;gap:10px;margin-top:18px;flex-wrap:wrap;align-items:center">
      <button class="btn btn-primary btn-lg" id="drill">Luyện ${pt.ex.length} bài tập</button>
      ${st.done?`<span class="chip">Đã luyện ${P[gid(pt.id)].n} lượt · đúng ${st.acc}%</span>`:''}
    </div>`;
  $('#back').onclick=()=>go('grammar');
  $('#drill').onclick=()=>startDrill([pt.id]);
  $('#readAll').onclick=()=>speak(pt.forms.map(f=>f[2]).join('. '));
}

/* ---------- phiên luyện ngữ pháp ---------- */
let DRILL=null;
function startDrill(ids,mixed){
  const q=[];
  ids.forEach(id=>{
    const pt=GP_BY_ID.get(id); if(!pt) return;
    const list=mixed?shuffle([...pt.ex]).slice(0,3):shuffle([...pt.ex]);
    list.forEach(e=>q.push({pt,e}));
  });
  if(!q.length){toast('Không có bài tập nào');return;}
  DRILL={queue:mixed?shuffle(q):q,i:0,right:0,byPoint:{},total:q.length,start:Date.now(),ids};
  ids.forEach(id=>DRILL.byPoint[id]={n:0,c:0});
  go('gdrill');
}
function renderDrill(){
  const root=$('#studyRoot'); if(!root) return;
  STUDY_SEQ++;
  if(!DRILL){go('grammar');return;}
  if(DRILL.i>=DRILL.queue.length){renderDrillDone(root);return;}
  const {pt,e}=DRILL.queue[DRILL.i];
  const pct=Math.round(DRILL.i/DRILL.total*100);
  const label={mc:'Chọn đáp án',fill:'Điền từ',order:'Sắp xếp câu',fix:'Sửa lỗi sai'}[e.t];
  root.innerHTML=`
    <div class="study-bar">
      <button class="btn btn-sm" id="quit" aria-label="Thoát">✕</button>
      <span class="bar" style="flex:1"><i class="b-known" style="width:${pct}%"></i></span>
      <span class="study-count">${DRILL.i+1}/${DRILL.total}</span>
    </div>
    <div style="display:flex;justify-content:center;gap:8px;margin-bottom:14px;flex-wrap:wrap">
      <span class="mode-tag">${label}</span><span class="chip">${esc(pt.name)}</span>
    </div>
    <div class="fc" id="cardHost"></div>`;
  $('#quit').onclick=()=>{ if(confirm('Kết thúc phiên luyện?')){DRILL=null;go('grammar');} };
  const host=$('#cardHost');
  ({mc:exMC,fill:exFill,order:exOrder,fix:exFix}[e.t])(host,pt,e);
}
function drillNext(pt,ok){
  DRILL.byPoint[pt.id].n++; if(ok){DRILL.byPoint[pt.id].c++;DRILL.right++;}
  DRILL.i++; renderDrill();
}
function drillFeedback(host,pt,e,ok,extra){
  const box=el('div');
  box.innerHTML=`<div class="feedback ${ok?'ok':'no'}">${ok?'Chính xác':'Chưa đúng'}</div>
    ${extra||''}<div class="why-box"><b>Vì sao</b>${esc(e.w)}</div>`;
  host.appendChild(box);
  const next=el('button','btn btn-primary btn-lg','Tiếp theo');
  next.style.cssText='width:100%;margin-top:14px';
  next.onclick=()=>drillNext(pt,ok);
  host.appendChild(next);
}
const gapHtml=t=>esc(t).replace(/___+/g,'<span class="gap">&nbsp;&nbsp;&nbsp;</span>');

function exMC(host,pt,e){
  host.innerHTML=`<div class="q-text">${gapHtml(e.q)}</div><div class="opts" id="o"></div><div id="after"></div>`;
  const ob=host.querySelector('#o');
  e.o.forEach((opt,i)=>{
    const b=el('button','opt',`<span class="n">${'ABCD'[i]}</span><span>${esc(opt)}</span>`);
    b.onclick=()=>{
      ob.querySelectorAll('.opt').forEach((x,j)=>{x.disabled=true;
        if(j===e.a) x.classList.add('right'); else if(j===i) x.classList.add('wrong');});
      const ok=i===e.a;
      speak(e.q.replace(/___+/,e.o[e.a]));
      drillFeedback(host.querySelector('#after'),pt,e,ok);
    };
    ob.appendChild(b);
  });
}
function exFill(host,pt,e){
  host.innerHTML=`<div class="q-text">${gapHtml(e.q)}</div>
    <div style="margin-top:18px"><input class="write-in" id="ans" autocomplete="off" autocapitalize="off"
      spellcheck="false" placeholder="điền vào chỗ trống…" aria-label="Điền vào chỗ trống"></div>
    <div id="after"></div>
    <button class="btn btn-primary btn-lg" id="chk" style="width:100%;margin-top:14px">Kiểm tra</button>`;
  const inp=host.querySelector('#ans'); setTimeout(()=>inp.focus(),100);
  const check=()=>{
    const v=inp.value.trim(); if(!v) return;
    const ok=accepts(e.a,v);
    inp.disabled=true; inp.classList.add(ok?'ok':'no');
    const btn=host.querySelector('#chk'); if(btn) btn.remove();
    drillFeedback(host.querySelector('#after'),pt,e,ok,
      ok?'':`<div class="q-hint">Đáp án: <b style="color:var(--good)">${esc(e.a[0])}</b></div>`);
  };
  host.querySelector('#chk').onclick=check;
  inp.onkeydown=ev=>{if(ev.key==='Enter'){ev.preventDefault();check();}};
}
function exOrder(host,pt,e){
  host.innerHTML=`<div class="eyebrow" style="text-align:center">Ghép thành câu đúng</div>
    <div class="slot" id="slot" style="margin-top:12px"></div>
    <div class="tiles" id="tiles"></div><div id="after"></div>
    <button class="btn btn-primary btn-lg" id="chk" style="width:100%;margin-top:16px">Kiểm tra</button>`;
  const slot=host.querySelector('#slot'), tiles=host.querySelector('#tiles');
  const picked=[];
  shuffle([...e.q]).forEach(word=>{
    const t=el('button','tile',esc(word));
    t.onclick=()=>{
      t.classList.add('used');
      const c=el('button','tile',esc(word));
      const rec={word,el:t};
      picked.push(rec);
      c.onclick=()=>{ t.classList.remove('used'); c.remove();
        const k=picked.indexOf(rec); if(k>-1) picked.splice(k,1); };
      slot.appendChild(c);
    };
    tiles.appendChild(t);
  });
  host.querySelector('#chk').onclick=()=>{
    if(!picked.length) return;
    const got=picked.map(x=>x.word).join(' ');
    const ok=normEn(got)===normEn(e.a);
    const btn=host.querySelector('#chk'); if(btn) btn.remove();
    tiles.querySelectorAll('.tile').forEach(t=>t.classList.add('used'));
    slot.querySelectorAll('.tile').forEach(t=>{t.style.pointerEvents='none';});
    speak(e.a);
    drillFeedback(host.querySelector('#after'),pt,e,ok,
      ok?'':`<div class="q-hint">Đáp án: <b style="color:var(--good)">${esc(e.a)}</b></div>`);
  };
}
function exFix(host,pt,e){
  host.innerHTML=`<div class="eyebrow" style="text-align:center">Câu sau có một lỗi — hãy viết lại cho đúng</div>
    <div class="q-text" style="margin-top:10px;color:var(--again)">${esc(e.q)}</div>
    <div style="margin-top:18px"><input class="write-in" id="ans" style="font-size:16px;text-align:left"
      autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="viết lại cả câu…" aria-label="Viết lại câu"></div>
    <div id="after"></div>
    <button class="btn btn-primary btn-lg" id="chk" style="width:100%;margin-top:14px">Kiểm tra</button>`;
  const inp=host.querySelector('#ans'); setTimeout(()=>inp.focus(),100);
  const check=()=>{
    const v=inp.value.trim(); if(!v) return;
    const ok=accepts(e.a,v);
    inp.disabled=true; inp.classList.add(ok?'ok':'no');
    const btn=host.querySelector('#chk'); if(btn) btn.remove();
    speak(e.a[0]);
    drillFeedback(host.querySelector('#after'),pt,e,ok,
      `<div class="q-hint">Câu đúng: <b style="color:var(--good)">${esc(e.a[0])}</b></div>`);
  };
  host.querySelector('#chk').onclick=check;
  inp.onkeydown=ev=>{if(ev.key==='Enter'){ev.preventDefault();check();}};
}
function renderDrillDone(root){
  const acc=DRILL.total?Math.round(DRILL.right/DRILL.total*100):0;
  const mins=Math.max(1,Math.round((Date.now()-DRILL.start)/60000));
  const rows=[];
  // chấm mỗi chuyên đề theo độ chính xác rồi đưa vào lịch ôn ngắt quãng
  for(const id of Object.keys(DRILL.byPoint)){
    const r=DRILL.byPoint[id];
    if(!r.n) continue;
    const a=r.c/r.n;
    const q=a>=0.9?5:(a>=0.7?4:(a>=0.5?3:0));
    grade(gid(id),q,'grammar');
    rows.push(`<div class="sb"><span style="font-size:13.5px">${esc(GP_BY_ID.get(id).name)}</span>
      <span class="bar"><i class="b-known" style="width:${Math.round(a*100)}%"></i></span>
      <span class="mono" style="text-align:right">${r.c}/${r.n}</span></div>`);
  }
  const ids=DRILL.ids;
  root.innerHTML=`<div class="fc" style="min-height:auto;text-align:center;align-items:center">
    <div style="font-size:52px">${acc>=80?'🎯':acc>=50?'📈':'📚'}</div>
    <h2 style="font-size:26px;margin-top:8px">Xong phiên luyện</h2>
    <p style="color:var(--muted);margin:8px 0 18px">${DRILL.right}/${DRILL.total} câu đúng · ${acc}% · ${mins} phút</p>
    <div class="skill-bars" style="width:100%;text-align:left">${rows.join('')}</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:20px">
      <button class="btn btn-primary btn-lg" id="again">Luyện lại</button>
      <button class="btn btn-lg" id="home">Về danh sách</button>
    </div></div>`;
  $('#again').onclick=()=>startDrill(ids);
  $('#home').onclick=()=>{DRILL=null;go('grammar');};
}

