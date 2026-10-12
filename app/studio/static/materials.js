'use strict';

const solutionTags = {'main-correct':'Main Correct', correct:'Correct', wrong:'Wrong',
  'time-limit':'Time Limit', 'memory-limit':'Memory Limit', 'runtime-error':'Runtime Error',
  'output-limit':'Output Limit', 'communication-limit':'Communication Limit', 'compile-error':'Compile Error'};
const expectedVerdicts = {'main-correct':'AC', correct:'AC', wrong:'WA / PE', 'time-limit':'TLE',
  'memory-limit':'MLE', 'runtime-error':'RE', 'output-limit':'OLE', 'communication-limit':'CLE', 'compile-error':'CE'};
const materials = {papers:[], paper:null, paperDirty:false, paperVersion:0, paperSaving:null,
  selected:new Set(), selectedProblem:null, editingSolution:null, solutionProblem:null};
const mainSolution = p => p?.solutions?.find(s=>s.tag==='main-correct');
const solutionId = () => crypto.randomUUID().replaceAll('-','').slice(0,12);
function tagOptions(value) {return Object.entries(solutionTags).map(([id,label])=>`<option value="${id}"${id===value?' selected':''}>${label}</option>`).join('');}
function renderWorkspaceNavigation() {
  document.querySelectorAll('.workspace-switch button').forEach(button=>{
    const active=(button.dataset.action==='papers')===!$('#papers-workspace').hidden;
    if(active)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');
  });
}
function setMainTag(item, tag) {
  if(tag==='main-correct')for(const s of state.p.solutions||[])if(s.id!==item.id&&s.tag==='main-correct')s.tag='correct';
  item.tag=tag;
}
function markSolutionsChanged() {setDirty();renderConfig();renderData();renderRun();}
function renderSolutions() {
  const p=state.p;if(!p)return;
  const items=p.solutions||[], main=mainSolution(p), jury=usesInteractor(p);
  $('#main-solution-hint').innerHTML=(main?`标程：<strong>${esc(main.name)}</strong> · Main Correct。`:'请将一份正确解法标记为 <strong>Main Correct</strong>。')+
    (jury?'生成数据时运行完整交互 / 通信流程进行自检；如评测工具需要 answer，可在下方配置独立答案生成程序。':'在 Tests 中生成数据时，将使用 Main Correct 作为 std。')+
    '<br>Correct 必须全部 AC；其他标签至少出现一次对应结果，IE 始终视为异常。修改后请保存题目。';
  $('#saved-solutions').innerHTML=items.length?`<table class="data-table solutions-table"><thead><tr><th>文件</th><th>语言</th><th>预期结果</th><th>大小</th><th>操作</th></tr></thead><tbody>${items.map(s=>`<tr><td><button class="problem-title-link" data-edit-solution="${s.id}">${esc(s.name)}</button>${s.receiver?'<small class="subtle"> + Receiver</small>':''}</td><td>${esc(languages[s.language]?.[0])}</td><td><select data-solution-tag="${s.id}" aria-label="${esc(s.name)} 的预期结果">${tagOptions(s.tag)}</select></td><td>${bytes(new TextEncoder().encode(s.content).length)}</td><td><div class="case-actions"><button class="text-button teal" data-edit-solution="${s.id}">编辑</button><button class="text-button danger-text" data-delete-solution="${s.id}">移除</button></div></td></tr>`).join('')}</tbody></table>`:'<div class="empty-state">尚未添加解法。支持批量上传 C / C++ / Python / Java，Python 可选择 PyPy。</div>';
  $('#legacy-reference-section').hidden=!jury&&!p.programs.reference;
  $('#reference-heading').textContent=jury?'答案生成程序 · 可选':'旧版参考标程';
  $('#reference-description').textContent=jury?'按普通输入输出生成 jury answer；它与参与交互的 Main Correct 是两个用途。':main?'当前已使用 Main Correct。旧版参考标程仅保留为兼容资料。':'现有题目可继续使用此标程，也可一键迁移到解法列表。';
  $('#migrate-reference').hidden=jury||!p.programs.reference;
  renderInvocationPicker();
}
function renderInvocationPicker() {
  if(!state.p)return;
  const items=state.p.solutions||[];
  if(materials.selectedProblem!==state.p.id){materials.selectedProblem=state.p.id;materials.selected=new Set(items.map(s=>s.id));}
  const ids=new Set(items.map(s=>s.id));
  materials.selected=new Set([...materials.selected].filter(id=>ids.has(id)));
  $('#selected-solutions-count').textContent=`${materials.selected.size} / ${items.length}`;
  $('#invocation-solutions').innerHTML=items.length?`<table class="data-table"><thead><tr><th></th><th>解法</th><th>语言</th><th>预期</th></tr></thead><tbody>${items.map(s=>`<tr><td><input type="checkbox" data-invoke-solution="${s.id}" aria-label="运行 ${esc(s.name)}"${materials.selected.has(s.id)?' checked':''}></td><td>${esc(s.name)}</td><td>${esc(languages[s.language]?.[0])}</td><td><span class="solution-tag ${s.tag==='main-correct'?'main-tag':''}">${solutionTags[s.tag]}</span> <small class="subtle">${expectedVerdicts[s.tag]}</small></td></tr>`).join('')}</tbody></table>`:'<div class="empty-state">先在 Solution 中保存解法，再选择部分或全部解法运行。</div>';
  $('#invocation-source').textContent=`已选 ${materials.selected.size} / ${items.length} 份解法`;
  $('#invocation-hint').textContent='运行前自动保存题目，使用当前有效数据。结果按「解法 × 测试点」展示，可查看每个测试点的耗时、内存和日志。';
}
function editSavedSolution(id, initial) {
  const item=initial||(state.p.solutions||[]).find(s=>s.id===id)||{name:'main.cpp',language:'cpp',content:'',tag:'correct'};
  materials.editingSolution=id||null;materials.solutionProblem=state.p.id;
  const receiverAllowed=state.p.mode==='communication'&&!isMultipass(state.p)&&!isTestlibCommunication(state.p);
  openModal(id?'编辑解法':'新建解法',`<div class="solution-form"><label>文件名<input id="saved-solution-name" maxlength="100" value="${esc(item.name)}"></label><label>运行语言<select id="saved-solution-language">${languageOptions(item.language)}</select></label><label>预期结果<select id="saved-solution-tag">${tagOptions(item.tag)}</select></label></div><textarea id="saved-solution-code" class="modal-code modal-editor" aria-label="解法源码" spellcheck="false">${esc(item.content)}</textarea>${receiverAllowed?`<details${item.receiver?' open':''}><summary>独立 Receiver · 可选</summary><label>运行语言<select id="saved-receiver-language">${languageOptions(item.receiver?.language||'cpp')}</select></label><textarea id="saved-receiver-code" class="modal-code receiver-editor" aria-label="已保存解法的 Receiver 源码" spellcheck="false" placeholder="留空则两个阶段运行同一份程序">${esc(item.receiver?.content||'')}</textarea></details>`:''}`,'<button class="button secondary" data-action="close-modal">取消</button><button class="button primary" data-action="apply-saved-solution">应用修改</button>');
}
function checkSource(content) {
  if(!content.trim()||content.includes('\0')||new TextEncoder().encode(content).length>512*1024)throw new Error('源码不能为空，且不能超过 512 KiB');
}
function applySavedSolution() {
  if(state.p?.id!==materials.solutionProblem)throw new Error('当前题目已切换，请重新打开解法');
  const content=$('#saved-solution-code').value, language=$('#saved-solution-language').value;
  checkSource(content);
  const name=$('#saved-solution-name').value.trim(), extension=name.split('.').pop().toLowerCase();
  if(!name||/[\\/]/.test(name)||!({cpp:['cpp','cc','cxx'],c:['c'],python:['py'],pypy:['py'],java:['java']}[language].includes(extension)))throw new Error('文件名后缀须与运行语言一致');
  const items=state.p.solutions??=[], id=materials.editingSolution||solutionId();
  if(!materials.editingSolution&&items.length>=32)throw new Error('每题最多保存 32 份解法');
  const item={id,name,language,content,tag:$('#saved-solution-tag').value};
  if($('#saved-receiver-code')?.value.trim()){
    checkSource($('#saved-receiver-code').value);
    item.receiver=programSource($('#saved-receiver-language').value,$('#saved-receiver-code').value);
  }
  setMainTag(item,item.tag);
  const index=items.findIndex(s=>s.id===id);if(index<0)items.push(item);else items[index]=item;
  state.p.solutions=items;materials.selected.add(id);markSolutionsChanged();$('#modal').close();toast('解法已应用，请保存题目');
}
async function invokeSolutions(all=false) {
  if(!state.p)return;
  const ids=all?(state.p.solutions||[]).map(s=>s.id):[...materials.selected];
  if(!ids.length)throw new Error('请至少选择一份已保存的解法');
  if(state.dirty)await save();
  if(state.dirty)throw new Error('保存期间又有修改，请先保存最新内容');
  const job=await api(`/api/studio/problems/${state.p.id}/invoke`,'POST',{revision:state.p.revision,solution_ids:ids});
  state.submissionJob=job;state.jobs.unshift(job);showTab('invocations');
  renderJob(job,'#submission-job');renderHistory();schedulePoll();
}
function renderBatchJob(job, el) {
  const runs=job.runs||[], active=['queued','running'].includes(job.state), cases=runs.find(r=>r.cases?.length)?.cases||[];
  el.innerHTML=`<div class="job-card"><div class="job-top"><div>${badge(job.verdict||job.state)}<h3>${active?'批量评测进行中':job.state==='failed'?'任务失败':'批量评测完成'}</h3><small>r${job.revision} · ${job.matched_count??runs.filter(r=>r.matches_expected).length} / ${runs.length||job.solution_ids?.length||0} 符合预期</small></div><small>${date(job.created)}</small></div><div class="progress-track"><div style="width:${Math.max(0,Math.min(100,job.progress||0))}%"></div></div>${job.error?`<div class="job-error">${esc(job.error)}</div>`:''}<div class="matrix-scroll"><table class="data-table invocation-matrix"><thead><tr><th>解法</th><th>预期</th><th>结果 / 预期检查</th><th>最大耗时</th><th>峰值内存</th>${cases.map(c=>`<th>#${esc(c.id)}</th>`).join('')}</tr></thead><tbody>${runs.map((r,i)=>`<tr><td><button class="problem-title-link" data-run-details="${job.id}:${i}">${esc(r.name)}</button></td><td>${solutionTags[r.tag]||esc(r.tag)}</td><td>${badge(r.verdict||r.state)} <small class="${r.matches_expected?'expect-match':'expect-mismatch'}">${r.state==='done'?(r.matches_expected?'符合':'不符'):r.state==='running'?'运行中':'排队中'}</small></td><td>${r.max_time_ms==null?'—':r.max_time_ms.toFixed(1)+' ms'}</td><td>${r.max_memory_kb==null?'—':bytes(r.max_memory_kb*1024)}</td>${cases.map((c,n)=>`<td>${r.cases?.[n]?`<button class="matrix-result" data-result="${job.id}:${n}:${i}" title="查看 ${esc(r.name)} 测试点 ${esc(c.id)}">${badge(r.cases[n].verdict)}</button>`:'—'}</td>`).join('')}</tr>`).join('')}</tbody></table></div><details${job.state==='failed'?' open':''}><summary>执行日志 · ${(job.log||[]).length} 条</summary><pre class="job-log">${esc((job.log||[]).join('\n'))}</pre></details></div>`;
}
function runDetails(jid, index) {
  const job=state.renderedJobs.get(jid)||state.jobs.find(j=>j.id===jid), run=job?.runs?.[Number(index)];if(!run)return;
  openModal(run.name+' · '+(run.verdict||run.state),`<p class="modal-caption">预期 ${esc(solutionTags[run.tag])} · ${run.matches_expected?'符合预期':run.state==='done'?'不符合预期':'尚未完成'} · 题目版本 r${job.revision}</p>${run.message?`<pre class="modal-code">${esc(run.message)}</pre>`:''}<div class="matrix-scroll"><table class="data-table"><thead><tr><th>测试点</th><th>结果</th><th>时间</th><th>内存</th><th></th></tr></thead><tbody>${(run.cases||[]).map((c,n)=>`<tr><td>#${esc(c.id)}</td><td>${badge(c.verdict)}</td><td>${c.time_ms.toFixed(1)} ms</td><td>${bytes(c.memory_kb*1024)}</td><td><button class="text-button teal" data-result="${jid}:${n}:${index}">详情</button></td></tr>`).join('')}</tbody></table></div>`);
}

async function refreshPapers() {materials.papers=(await api('/api/studio/papers')).papers;$('#paper-count').textContent=materials.papers.length;renderPapers();}
function renderPapers() {
  $('#papers-list').innerHTML=materials.papers.length?`<table class="data-table workspace-table"><thead><tr><th>试卷</th><th>题数</th><th>数据就绪</th><th>更新时间</th><th></th></tr></thead><tbody>${materials.papers.map(p=>`<tr><td><button class="problem-title-link" data-paper="${p.id}">${esc(p.title)}</button></td><td>${p.problem_ids.length}</td><td>${p.problems.filter(x=>x.data_ready&&!x.deleted_at&&!x.missing).length} / ${p.problem_ids.length}</td><td>${date(p.updated)}</td><td><button class="text-button teal" data-paper="${p.id}">编辑 →</button></td></tr>`).join('')}</tbody></table>`:'<div class="empty-state">尚未创建试卷。点击「新建试卷」，按题目 ID 添加已有题目。</div>';
}
async function savePaperIfDirty() {if(materials.paperDirty||materials.paperSaving)await savePaper();}
async function showPapers(id) {
  if(state.p&&state.dirty)await save();
  await savePaperIfDirty();
  clearProblem();materials.paper=null;materials.paperDirty=false;
  $('#welcome').hidden=true;$('#papers-workspace').hidden=false;
  $('#papers-home').hidden=!!id;$('#paper-editor').hidden=true;
  $('#breadcrumb-title').textContent='试卷管理';document.title='试卷管理 · Sakura Studio';
  await refreshLibrary();await refreshPapers();
  if(id){
    materials.paper=await api('/api/studio/papers/'+id);
    $('#paper-title').value=materials.paper.title;$('#paper-description').value=materials.paper.description;
    renderPaper();
    $('#paper-editor').hidden=false;
  }
  history.replaceState(null,'',id?'#paper/'+id:'#papers');
  renderWorkspaceNavigation();
}
function paperDirty() {materials.paperDirty=true;materials.paperVersion++;renderPaperMeta();}
function renderPaperMeta() {
  const p=materials.paper;if(!p)return;
  $('#paper-heading').textContent=p.title||'未命名试卷';
  $('#paper-status').textContent=`${materials.paperDirty?'有未保存的修改':'已保存'} · r${p.revision} · ${p.problem_ids.length} 道题`;
}
function renderPaper() {
  const p=materials.paper;if(!p)return;renderPaperMeta();
  const candidates=state.problems.filter(x=>!p.problem_ids.includes(x.id));
  $('#paper-problem-select').innerHTML='<option value="">选择题目…</option>'+candidates.map(x=>`<option value="${x.id}">${esc(x.problem_code)} · ${esc(x.title)}</option>`).join('');
  const summaries=new Map([...p.problems,...state.problems].map(x=>[x.id,x]));
  $('#paper-problems').innerHTML=p.problem_ids.length?`<table class="data-table workspace-table"><thead><tr><th>顺序</th><th>题目 ID</th><th>题目</th><th>类型</th><th>状态</th><th>操作</th></tr></thead><tbody>${p.problem_ids.map((id,i)=>{const s=summaries.get(id)||{id,title:'题目不存在',missing:true};return `<tr><td>${i+1}</td><td class="mono">${esc(s.problem_code||'—')}</td><td>${esc(s.title)}</td><td>${modeNames[s.mode]||'—'}</td><td><span class="readiness ${s.data_ready&&!s.deleted_at?'ready':''}">${s.missing?'不存在':s.deleted_at?'已在回收站':s.data_ready?'数据就绪':'草稿'}</span></td><td><div class="case-actions"><button class="text-button" data-paper-move="${i}:-1" aria-label="上移第 ${i+1} 题"${i===0?' disabled':''}>↑</button><button class="text-button" data-paper-move="${i}:1" aria-label="下移第 ${i+1} 题"${i===p.problem_ids.length-1?' disabled':''}>↓</button><button class="text-button teal" data-problem="${id}"${s.deleted_at||s.missing?' disabled':''}>编辑题目</button><button class="text-button danger-text" data-paper-remove="${id}">移除</button></div></td></tr>`;}).join('')}</tbody></table>`:'<div class="empty-state">这套试卷还没有题目。输入题目 ID 或使用下拉列表添加。</div>';
}
function addPaperProblem(id) {
  const p=materials.paper;if(!p)return;
  if(!id||!state.problems.some(x=>x.id===id))throw new Error('没有找到该题目，请填写有效题目 ID 或选择题目');
  if(p.problem_ids.includes(id))throw new Error('这道题已经在试卷中');
  if(p.problem_ids.length>=100)throw new Error('每套试卷最多包含 100 道题');
  p.problem_ids.push(id);paperDirty();renderPaper();$('#paper-problem-code').value='';
}
async function savePaper() {
  if(!materials.paper)return;
  if(materials.paperSaving)return materials.paperSaving;
  const current=materials.paper, version=materials.paperVersion;
  materials.paperSaving=(async()=>{
    const saved=await api('/api/studio/papers/'+current.id,'PUT',current);
    if(materials.paper?.id!==current.id)return;
    if(version===materials.paperVersion){materials.paper=saved;materials.paperDirty=false;}
    else {materials.paper.revision=saved.revision;materials.paper.problems=saved.problems;}
    renderPaperMeta();await refreshPapers();
  })();
  try{await materials.paperSaving;}finally{materials.paperSaving=null;}
  if(materials.paperDirty)throw new Error('保存期间又有修改，请再次保存试卷');
}
function safeMarkdown(value) {return DOMPurify.sanitize(marked.parse(value||''),{FORBID_TAGS:['style','input','button','form'],FORBID_ATTR:['style']});}
async function previewPaper() {
  await savePaperIfDirty();
  const data=await api('/api/studio/papers/'+materials.paper.id+'/preview');
  openModal(data.paper.title,`<article class="markdown paper-preview"><div>${safeMarkdown(data.paper.description)}</div>${data.problems.map((p,i)=>`<section><h1>第 ${i+1} 题 · ${esc(p.title)}</h1><p class="modal-caption">${modeNames[p.mode]} · ${p.time_ms} ms · ${p.memory_mb} MiB</p>${safeMarkdown(p.statement)}</section>`).join('')||'<p>试卷尚未添加题目。</p>'}</article>`);
  renderMathInElement($('#modal-body'),{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],throwOnError:false,trust:false,strict:'ignore'});
  $('#modal-body').querySelectorAll('a').forEach(a=>{a.target='_blank';a.rel='noopener noreferrer';});
}
const materialActions=new Set(['papers','new-paper','save-paper','preview-paper','export-paper','delete-paper','confirm-delete-paper',
  'add-paper-code','add-paper-selection','problem-library','new-saved-solution','apply-saved-solution','upload-solutions',
  'save-temporary-solution','migrate-reference','invoke','invoke-all','select-all-solutions','select-no-solutions']);
async function materialAction(name) {
  if(name==='papers')return showPapers();
  if(name==='problem-library'){if(state.dirty)await save();await savePaperIfDirty();materials.paper=null;$('#papers-workspace').hidden=true;clearProblem();return;}
  if(name==='new-paper'){await savePaperIfDirty();const p=await api('/api/studio/papers','POST',{});await showPapers(p.id);$('#paper-title').select();return;}
  if(name==='save-paper'){await savePaper();toast('试卷已保存');return;}
  if(name==='preview-paper')return previewPaper();
  if(name==='export-paper'){
    await savePaperIfDirty();
    if(!materials.paper.problem_ids.length)throw new Error('请先向试卷添加题目');
    await api('/api/studio/papers/'+materials.paper.id+'/preview');
    const a=document.createElement('a');a.href='/api/studio/papers/'+materials.paper.id+'/export';a.download='paper-'+materials.paper.id+'.zip';a.click();return;
  }
  if(name==='delete-paper')return openModal('删除试卷',`<p>删除「${esc(materials.paper.title)}」？卷内题目会继续保留在题目库。</p>`,'<button class="button secondary" data-action="close-modal">取消</button><button class="button danger" data-action="confirm-delete-paper">删除试卷</button>');
  if(name==='confirm-delete-paper'){await api('/api/studio/papers/'+materials.paper.id+'/delete','POST',{revision:materials.paper.revision});materials.paperDirty=false;materials.paper=null;$('#modal').close();await showPapers();toast('试卷已删除');return;}
  if(name==='add-paper-code'){
    const code=$('#paper-problem-code').value.trim().replace(/^p/i,'');
    return addPaperProblem(/^\d+$/.test(code)?state.problems.find(p=>Number(p.problem_code)===Number(code))?.id:null);
  }
  if(name==='add-paper-selection')return addPaperProblem($('#paper-problem-select').value);
  if(name==='new-saved-solution')return editSavedSolution();
  if(name==='apply-saved-solution')return applySavedSolution();
  if(name==='upload-solutions'){$('#solutions-picker').value='';$('#solutions-picker').click();return;}
  if(name==='save-temporary-solution'){
    const content=$('#solution').value;checkSource(content);
    const item={...programSource($('#solution-language').value,content),tag:'correct'};
    if(state.p.mode==='communication'&&$('#separate-receiver').checked)item.receiver=programSource($('#receiver-language').value,$('#receiver').value);
    return editSavedSolution(null,item);
  }
  if(name==='migrate-reference'){
    if((state.p.solutions||[]).length>=32)throw new Error('每题最多保存 32 份解法');
    const item={...state.p.programs.reference,id:solutionId(),tag:'main-correct'};
    setMainTag(item,item.tag);(state.p.solutions??=[]).push(item);delete state.p.programs.reference;
    materials.selected.add(item.id);markSolutionsChanged();toast('已迁移为 Main Correct，请保存题目');return;
  }
  if(name==='select-all-solutions'||name==='select-no-solutions'){
    materials.selected=new Set(name==='select-all-solutions'?(state.p.solutions||[]).map(s=>s.id):[]);renderInvocationPicker();return;
  }
  if(name==='invoke'||name==='invoke-all')return invokeSolutions(name==='invoke-all');
}

document.addEventListener('click',async event=>{
  const el=event.target.closest('button');if(!el||el.disabled)return;
  try{
    if(el.dataset.paper)await showPapers(el.dataset.paper);
    if(el.dataset.paperMove){const [index,direction]=el.dataset.paperMove.split(':').map(Number), ids=materials.paper.problem_ids;[ids[index],ids[index+direction]]=[ids[index+direction],ids[index]];paperDirty();renderPaper();}
    if(el.dataset.paperRemove){materials.paper.problem_ids=materials.paper.problem_ids.filter(id=>id!==el.dataset.paperRemove);paperDirty();renderPaper();}
    if(el.dataset.editSolution)editSavedSolution(el.dataset.editSolution);
    if(el.dataset.deleteSolution){
      const item=state.p.solutions.find(s=>s.id===el.dataset.deleteSolution);
      if(item.tag==='main-correct'&&!confirm('移除 Main Correct 标程？后续生成数据前需要重新指定标程。'))return;
      state.p.solutions=state.p.solutions.filter(s=>s.id!==item.id);markSolutionsChanged();
    }
    if(el.dataset.runDetails)runDetails(...el.dataset.runDetails.split(':'));
  }catch(e){toast(e.message,true);}
});
document.addEventListener('input',event=>{
  if(materials.paper&&['paper-title','paper-description'].includes(event.target.id)){
    materials.paper[event.target.id==='paper-title'?'title':'description']=event.target.value;paperDirty();
  }
});
document.addEventListener('change',event=>{
  const el=event.target;
  if(el.dataset.solutionTag){const item=state.p.solutions.find(s=>s.id===el.dataset.solutionTag);setMainTag(item,el.value);markSolutionsChanged();}
  if(el.dataset.invokeSolution){if(el.checked)materials.selected.add(el.dataset.invokeSolution);else materials.selected.delete(el.dataset.invokeSolution);renderInvocationPicker();}
  if(el.id==='saved-solution-language')$('#saved-solution-name').value=languages[el.value][1];
});
document.addEventListener('keydown',event=>{
  if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='s'&&materials.paper&&!$('#modal').open){event.preventDefault();materialAction('save-paper').catch(e=>toast(e.message,true));}
  if(event.key==='Enter'&&event.target.id==='paper-problem-code'){event.preventDefault();materialAction('add-paper-code').catch(e=>toast(e.message,true));}
});
window.addEventListener('beforeunload',event=>{if(materials.paperDirty){event.preventDefault();event.returnValue='';}});
document.addEventListener('DOMContentLoaded',()=>{
  $('#solutions-picker').addEventListener('change',async event=>{
    const pid=state.p?.id;
    try{
      const files=[...event.target.files];if(!files.length)return;
      if((state.p.solutions||[]).length+files.length>32)throw new Error('每题最多保存 32 份解法');
      const uploaded=[];
      for(const file of files){
        if(file.size>512*1024)throw new Error(file.name+' 超过 512 KiB');
        const language={c:'c',cpp:'cpp',cc:'cpp',cxx:'cpp',py:'python',java:'java'}[file.name.split('.').pop().toLowerCase()];
        if(!language)throw new Error(file.name+' 不是支持的源码文件');
        const content=await file.text();checkSource(content);
        uploaded.push({id:solutionId(),name:file.name,language,content,tag:'correct'});
      }
      if(state.p?.id!==pid)throw new Error('当前题目已切换，请重新上传');
      const total=[...(state.p.solutions||[]),...uploaded].reduce((sum,s)=>sum+new TextEncoder().encode(s.content+(s.receiver?.content||'')).length,0);
      if(total>4*1024*1024)throw new Error('解法源码总大小不能超过 4 MiB');
      (state.p.solutions??=[]).push(...uploaded);uploaded.forEach(s=>materials.selected.add(s.id));markSolutionsChanged();
      toast(`已添加 ${uploaded.length} 份解法，请设置预期结果并保存题目`);
    }catch(e){toast(e.message,true);}
  });
});
