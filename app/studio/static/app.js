'use strict';
const $ = s => document.querySelector(s);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const modeNames = {normal:'普通题', interactive:'交互题', communication:'通信题'};
const isMultipass = p => p?.mode==='communication' && p.communication_protocol==='domjudge-multipass-v1';
const isTestlibCommunication = p => p?.mode==='communication' && p.communication_protocol==='testlib-communication-v1';
const usesInteractor = p => p?.mode==='interactive' || isTestlibCommunication(p);
const workspaceTabs = ['general','statement','checker','validator','tests','solution','invocations'];
const tabAliases = {config:'general', data:'tests', run:'invocations', solutions:'solution', invacations:'invocations'};
const languages = {c:['C17','main.c'], cpp:['C++17','main.cpp'], python:['Python 3','main.py'], pypy:['PyPy 3','main.py'], java:['Java 21','Main.java']};
function languageOptions(selected) {return Object.entries(languages).map(([id,[label]])=>`<option value="${id}"${selected===id?' selected':''}>${label}</option>`).join('');}
function programSource(language, content) {return {language, name:languages[language][1], content};}
const modeInfo = {
  normal: {icon:'↦', en:'STANDARD', desc:'输入、运行、检查输出。适用于绝大多数算法题。', title:'数列求和'},
  interactive: {icon:'⇄', en:'INTERACTIVE', desc:'程序与交互器双向对话，按协议逐步获得信息。', title:'对话中的求和'},
  communication: {icon:'⇢', en:'COMMUNICATION', desc:'分阶段运行，可选消息传递或验证器控制多轮执行。', title:'一封短消息'},
};
const roles = {
  gen: ['数据生成器','gen','registerGen → stdout 生成输入'],
  val: ['输入校验器','val','registerValidation → 校验 stdin'],
  checker: ['答案检查器','chk','registerTestlibCmd → 检查输出'],
  interactor: ['交互器','int','registerInteraction → 双向对话'],
  reference: ['参考标程','std','生成每个测试点的标准答案'],
};
const state = {csrf:'', bootstrap:null, problems:[], p:null, tab:'general', dirty:false, jobs:[],
  generationJob:null, submissionJob:null, busy:new Set(), polling:false, search:'', uploadRole:null,
  solutionName:'main.cpp', modalRole:null, renderedJobs:new Map(), editVersion:0, savePromise:null,
  trashProblem:null, trashed:[]};
let toastTimer, previewTimer;

async function api(path, method='GET', body) {
  const response = await fetch(path, {method, headers: {'Content-Type':'application/json','X-CSRF-Token':state.csrf},
    ...(body === undefined ? {} : {body:JSON.stringify(body)})});
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || `请求失败 (${response.status})`);
  return payload;
}
function toast(message, error=false) {
  if(error&&$('#modal').open){const target=$('#modal-error');target.textContent=message;target.hidden=false;return;}
  const target = $('#toast'); target.textContent=message; target.classList.toggle('error',error); target.hidden=false;
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>target.hidden=true,error?7000:3200);
}
function bytes(n) { return n < 1024 ? `${n} B` : n < 1048576 ? `${(n/1024).toFixed(1)} KiB` : `${(n/1048576).toFixed(1)} MiB`; }
function date(n) { return new Date(n*1000).toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}); }
function badge(value) {return `<span class="verdict ${esc(value)}">${esc(value)}</span>`;}
function draftKey() {return 'newjudge-draft-' + state.p?.id;}
function setDirty() {
  state.dirty=true;
  state.editVersion++;
  try { localStorage.setItem(draftKey(),JSON.stringify(state.p)); } catch (_) { /* Saving to the server remains available. */ }
  renderMeta();
}
function dataReady() {return state.p?.data_ready && !state.dirty;}

function exampleCards(cls='example-grid') {
  return Object.entries(modeInfo).map(([mode,m],i)=>`<button class="example-card" data-example="${mode}"><small>0${i+1}</small><span class="mode-icon">${m.icon}</span><h3>${modeNames[mode]}</h3><p>${m.desc}</p><div class="example-bottom"><span>${m.title}</span><span>↗</span></div></button>`).join('');
}
function renderLibrary() {
  renderWorkspaceNavigation();
  $('#problem-count').textContent=state.problems.length;
  const list = state.problems.filter(p=>[p.title,p.problem_code].some(v=>(v||'').toLowerCase().includes(state.search.toLowerCase())));
  $('#problem-list').innerHTML=list.length ? list.map(p=>`<button class="problem-link ${state.p?.id===p.id?'active':''}" data-problem="${p.id}" title="${esc(p.title)}" aria-label="${esc(p.title)}"><span class="problem-symbol">${modeInfo[p.mode].icon}</span><div><strong>${esc(p.title)}</strong><small>${esc(p.problem_code)} · ${modeNames[p.mode]} · ${p.data_ready?'数据就绪':'草稿'} · r${p.revision}</small></div></button>`).join('') : '<div class="empty-library">'+(state.search?'没有找到匹配的题目':'还没有题目，从一个想法开始。')+'</div>';
  $('#workspace-problems').innerHTML=list.length?`<table class="data-table workspace-table"><thead><tr><th>题目 ID</th><th>题目</th><th>类型</th><th>状态</th><th>版本</th><th></th></tr></thead><tbody>${list.map(p=>`<tr><td class="mono">${esc(p.problem_code)}</td><td><button class="problem-title-link" data-problem="${p.id}">${esc(p.title)}</button></td><td>${modeNames[p.mode]}</td><td><span class="readiness ${p.data_ready?'ready':''}">${p.data_ready?'数据就绪':'草稿'}</span></td><td>r${p.revision}</td><td><button class="text-button teal" data-problem="${p.id}">编辑 →</button></td></tr>`).join('')}</tbody></table>`:'<div class="empty-state">'+(state.search?'没有找到匹配的题目。':'暂无题目。新建一道题目，或从下方示例开始。')+'</div>';
}
async function refreshLibrary() {state.problems=(await api('/api/studio/problems')).problems;renderLibrary();}
function renderMeta() {
  const p=state.p;if(!p)return;
  $('#breadcrumb-title').textContent=p.title;
  $('#problem-title').textContent=p.title||'未命名题目';
  $('#created-at').textContent=p.created?date(p.created):'—';
  $('#updated-at').textContent=p.updated?date(p.updated):'—';
  $('#mode-badge').textContent=modeNames[p.mode];
  $('#revision').textContent='版本 r'+p.revision;
  $('#save-status').textContent=state.dirty?'有未保存的修改':'已保存';
  $('#save-status').classList.toggle('dirty',state.dirty);
  $('#data-status').textContent=state.dirty?'保存后检查数据状态':p.data_ready?(p.dataset?.origin==='oj'?'原有测试数据已就绪':'数据已就绪'):p.dataset?'数据需重新生成':'尚未生成数据';
  $('#data-count').textContent=p.dataset?.cases.length || 0;
  $('#word-count').textContent=p.statement.length.toLocaleString()+' 字';
  document.title=p.title+' · Sakura Studio';
  renderPreparation();
}
function renderPreparation() {
  const p=state.p;if(!p)return;
  const rows=[['statement','Statement',p.statement.trim()?'已填写':'待填写',!!p.statement.trim()],
    ['checker','Checker',p.programs.checker?'已配置':p.mode==='interactive'?'可选':p.legacy_text_comparison?'文本比较':'待配置',!!p.programs.checker||p.mode==='interactive'||!!p.legacy_text_comparison],
    ...(usesInteractor(p)?[['checker','Interactor',p.programs.interactor?'已配置':'待配置',!!p.programs.interactor]]:[]),
    ['validator','Validator',p.programs.val?'已配置':'未配置',!!p.programs.val],
    ['tests','Generator',p.programs.gen?'已配置':'未配置',!!p.programs.gen],
    ['tests','Tests',dataReady()?`${p.dataset.cases.length} 个测试点`:p.dataset?'待检查 / 更新':'未生成',!!dataReady()],
    ['solution','Main Correct',mainSolution(p)?'已指定':p.programs.reference?'旧版标程':'未指定',!!mainSolution(p)||!!p.programs.reference]];
  $('#preparation-status').innerHTML=rows.map(([tab,name,status,ready])=>`<button data-go="${tab}"><span>${name}</span><small class="${ready?'complete':''}">${status} <span>↗</span></small></button>`).join('');
  $('#publication-status').innerHTML=p.publication?`<span class="tiny-dot"></span> 已发布到 OJ <a href="/#problem/${encodeURIComponent(p.publication.slug)}">查看题目 ↗</a>`:'尚未发布到 OJ';
}
function initMarkdown() {
  marked.use({extensions:[
    {name:'mathBlock',level:'block',start:s=>s.indexOf('$$'),tokenizer(s){const m=/^\$\$([\s\S]*?)\$\$(?:\n|$)/.exec(s);if(m)return{type:'mathBlock',raw:m[0],text:m[1]};},renderer(t){return '<div class="math-source">$$'+esc(t.text)+'$$</div>'; }},
    {name:'mathInline',level:'inline',start:s=>s.indexOf('$'),tokenizer(s){const m=/^\$(?!\$)([^$\n]+?)\$/.exec(s);if(m)return{type:'mathInline',raw:m[0],text:m[1]};},renderer(t){return '<span class="math-source">$'+esc(t.text)+'$</span>'; }},
  ]});
}
function renderPreview() {
  const content=state.p?.statement || '';
  $('#preview').innerHTML=content.trim()?DOMPurify.sanitize(marked.parse(content),{FORBID_TAGS:['style','input','button','form'],FORBID_ATTR:['style']}):'<div class="preview-empty"><span>Aa</span><p>你的题面，将在这里呈现。</p></div>';
  renderMathInElement($('#preview'), {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false},{left:'\\(',right:'\\)',display:false},{left:'\\[',right:'\\]',display:true}],throwOnError:false,trust:false,strict:'ignore'});
  $('#preview').querySelectorAll('a').forEach(a=>{a.target='_blank';a.rel='noopener noreferrer';});
  $('#word-count').textContent=content.length.toLocaleString()+' 字';
}
function renderConfig() {
  const p=state.p;
  $('#mode-options').innerHTML=Object.entries(modeInfo).map(([mode,m])=>`<button class="mode-card ${p.mode===mode?'active':''}" data-mode="${mode}" aria-pressed="${p.mode===mode}"><div class="mode-top"><span class="mode-icon">${m.icon}</span><span class="radio"></span></div><h3>${modeNames[mode]}<small>${m.en}</small></h3><p>${m.desc}</p></button>`).join('');
  $('#communication-config').hidden=p.mode!=='communication';
  $('#communication_protocol').value=p.communication_protocol||'send-receive-stdin-v1';
  $('#message-limit').hidden=p.mode!=='communication'||isMultipass(p)||isTestlibCommunication(p);
  const example=$('#communication-example');
  example.dataset.example=isTestlibCommunication(p)?'testlib-communication':isMultipass(p)?'multipass':'communication';
  example.textContent='创建当前协议示例 ↗';
  $('#pass-limit').hidden=!isMultipass(p);
  $('#validation_passes').value=p.validation_passes||2;
  for (const k of ['time_ms','memory_mb','output_kb','message_bytes']) $('#'+k).value=p[k];
  const cards=Object.fromEntries(Object.entries(roles).map(([role,[name,icon,hint]])=>{
    const file=p.programs[role];const required=!(p.mode==='interactive'&&['checker','reference'].includes(role))&&!((isMultipass(p)||isTestlibCommunication(p))&&role==='reference');
    if(isMultipass(p)&&role==='checker'){name='输出验证器';hint='检查本轮输出，可写 nextpass.in 继续下一轮';}
    if(isMultipass(p)&&role==='reference')hint='可选：运行完整多阶段流程，检查生成的数据';
    if(role==='checker'&&p.mode==='interactive')hint='可选：检查 tout 记录；不上传时由 interactor 判定';
    if(isTestlibCommunication(p)&&role==='checker')hint='检查第二轮选手输出，使用原始 input 和 answer';
    if(isTestlibCommunication(p)&&role==='interactor')hint='首轮双向交互；tout 作为第二轮输入，消息约束由交互器检查';
    if(isTestlibCommunication(p)&&role==='reference')hint='可选：按普通输入输出生成 checker / interactor 所需的答案文件';
    if(role==='checker'&&p.mode==='normal'&&p.legacy_text_comparison&&!file)hint='当前沿用标准文本比较；重新生成数据时需上传 checker';
    return [role,`<div class="program-card ${file?'loaded':''}"><span class="file-icon">${icon}</span><div class="program-content"><h4>${name} <span class="required">${required?(p.origin_problem_id?'重新生成时必需':'必需'):'可选'}</span></h4><p>${hint}</p>${file?`<div class="file-name">✓ ${esc(file.name)} · ${esc(languages[file.language]?.[0] || file.language)} <span class="subtle"> · ${bytes(new TextEncoder().encode(file.content).length)}</span></div>`:'<div class="file-name subtle">尚未添加程序</div>'}<div class="file-actions"><button class="text-button teal" data-upload="${role}">${file?'替换文件':'↑ 上传文件'}</button><button class="text-button" data-view-code="${role}">${file?'查看 / 编辑':'新建源码'}</button>${file?`<button class="text-button remove-file" data-remove="${role}">移除</button>`:''}</div></div><span class="file-type">${role==='reference'?'C / C++ / Python / PyPy / Java':'C++17 · ≤ 512 KiB'}</span></div>`];
  }));
  for(const [role,id] of Object.entries({checker:'checker',val:'validator',gen:'generator',reference:'reference',interactor:'interactor'}))$('#'+id+'-programs').innerHTML=cards[role];
  $('#interactor-section').hidden=!usesInteractor(p);
  $('#checker-description').textContent=isMultipass(p)?'输出验证器检查每一轮结果，并决定下一轮输入。':p.mode==='interactive'?'配置交互器；可选 checker 对交互记录做进一步检查。':'检查选手输出是否正确。在下方上传文件或直接编辑源码。';
  $('#solution-purpose').textContent='选择一份 Main Correct 标程；在 Invocations 中运行多份解法，验证数据能否识别错解和超限解法。';
  $('#protocol-note').innerHTML=p.mode==='normal' ? '<strong>普通题协议</strong><br>标程读取 gen 生成的输入，输出标准答案。checker 按 <code>checker input output answer</code> 调用，对参赛程序输出进行判定。' : p.mode==='interactive' ? '<strong>交互题协议</strong><br>使用 <code>registerInteraction(argc, argv)</code>；参数依次为 <code>input transcript answer</code>。stdin / stdout 与参赛程序双向连接，记得 flush。<br>checker 可选：未上传时，interactor 返回 <code>_ok</code> 且选手正常退出、资源未超限，即判 AC；上传时，交互成功后再检查 <code>tout</code> 记录。interactor 应检查最终答案、询问次数等交互规则。<br>参考标程可选，按普通输入输出生成 jury answer；未上传时 answer 为空。' : '<strong>run-twice · send-receive-stdin-v1</strong><br>同一程序运行两次，<code>argv[1]</code>（Python / PyPy 为 <code>sys.argv[1]</code>，Java 为 <code>args[0]</code>）或环境变量 <code>JUDGE_PHASE</code> 为 <code>send</code> 或 <code>receive</code>。Sender 读取完整输入；Receiver 在全新沙箱中只读取 Sender 的 stdout。消息按原始字节计数（包括换行），超限返回 CLE。checker 检查 Receiver 的输出。';
  if(isMultipass(p))$('#protocol-note').innerHTML='<strong>多阶段通信协议</strong><br>每轮在全新沙箱运行同一程序，阶段信息放在输入中。输出验证器按 <code>validator input answer feedback_dir</code> 调用，从 stdin 读取选手输出；返回 <code>42</code> 表示通过，<code>43</code> 表示答案错误，其他退出码表示评测错误。<br>通过后若写入 <code>feedback_dir/nextpass.in</code>，则作为下一轮输入；未写入则结束。超过最大轮数仍要求继续时判评测错误。通信量限制由验证器检查；参考标程可选，用于多阶段自检，answer 文件为空。<br>此输出验证器使用多阶段协议，不使用普通 checker 的 <code>registerTestlibCmd</code> 注册方式。';
  if(isTestlibCommunication(p)){
    $('#checker-description').textContent='首轮配置 interactor，第二轮配置 checker。两者均为必需组件。';
    $('#protocol-note').innerHTML='<strong>testlib 两轮通信协议</strong><br>首轮使用 <code>registerInteraction(argc, argv)</code> 双向交互，interactor 将第二轮输入写入 <code>tout</code>。首轮成功后，同一选手程序在全新沙箱中运行，只从 stdin 读取这份输入。<br>第二轮结束后，以原始 <code>input</code>、第二轮 <code>output</code> 和原始 <code>answer</code> 调用 checker，使用 <code>registerTestlibCmd(argc, argv)</code>。阶段标记需由题目协议在输入中给出。<br>消息内容和信息量限制由 interactor 检查；tout 文件须存在，可为空，最多 8 MiB。两轮分别限制时间和内存，任一轮超限或异常都会判失败。参考标程可选，仅用于生成答案文件。';
  }
  renderSolutions();
}
function renderData() {
  const p=state.p, cases=p.dataset?.cases || [];
  $('#answer-step').innerHTML='<b>4</b> '+(mainSolution(p)&&usesInteractor(p)?'Main Correct 自检':isMultipass(p)?(mainSolution(p)||p.programs.reference?'多阶段自检':'保存输入'):usesInteractor(p)&&!p.programs.reference?'跳过标准答案':'标准答案');
  $('#dataset-number').textContent=cases.length || '—';
  $('#dataset-count-label').textContent=p.dataset?.origin==='oj'?'个原有测试点':'个已验证测试点';
  $('#data-change-hint').textContent=p.dataset?.origin==='oj'?'修改题面和资源限制可沿用原有数据；修改判题方式、程序或生成参数后，需要重新生成。':'修改判题方式、程序、参数或资源限制后，需要重新生成数据。';
  $('#dataset-info').textContent=p.dataset ? `${p.dataset.origin==='oj'?'原有 OJ 测试数据 · ':''}${bytes(p.dataset.bytes)} · ${date(p.dataset.created)}${p.data_ready?'':' · 配置已变更，请重新生成'}`:'上传程序，准备第一份测试数据。';
  $('#case-table-caption').textContent=p.dataset?`${p.data_ready?'当前有效数据':'旧版本数据'} · r${p.dataset.revision}`:'输入 .in / 答案 .ans';
  $('#case-table').innerHTML=cases.length ? `<table class="data-table"><thead><tr><th>测试点</th><th>输入大小</th><th>答案大小</th><th>Validator</th><th>查看文件</th></tr></thead><tbody>${cases.map(c=>`<tr><td>#${c.id}${c.name?' · '+esc(c.name):''}${c.is_sample?' · 公开样例':''}</td><td>${bytes(c.input_bytes)}</td><td>${bytes(c.answer_bytes)}</td><td>${c.validated?badge('AC'):'<span class="subtle">原有数据</span>'}</td><td><div class="case-actions"><button class="text-button teal" data-preview="${c.id}.in">输入 ↗</button><button class="text-button teal" data-preview="${c.id}.ans">答案 ↗</button></div></td></tr>`).join('')}</tbody></table>`:'<div class="empty-state">还没有测试数据。配置生成参数后，点击「生成并验证」。</div>';
}
function renderRun() {
  const p=state.p;
  $('#env-mode').textContent=modeNames[p.mode];
  $('#env-time').textContent=p.time_ms+' ms'+(p.mode==='communication'?' / 阶段':'');
  $('#env-memory').textContent=p.memory_mb+' MiB';
  $('#env-cases').textContent=(p.dataset?.cases.length||0)+(p.data_ready?' 个':' · 未就绪');
  $('#solution-protocol').textContent=p.mode==='communication'?($('#solution-language').value==='java'?'args[0]':'argv[1]')+'：send / receive':p.mode==='interactive'?'stdin ⇄ stdout · 记得 flush':'标准输入 → 标准输出';
  $('#run-description').textContent=p.mode==='communication'?'Sender 与 Receiver 运行在独立沙箱中，消息超限返回 CLE。':p.mode==='interactive'?(p.programs.checker?'交互成功后，再由 checker 检查 tout 记录。':'interactor 判定通过，且选手正常结束、资源未超限，即判 AC。'):'选择部分或全部解法，验证当前测试数据与各份解法的预期结果。';
  if(isMultipass(p)){
    $('#solution-protocol').textContent='每轮同一程序 · 阶段由输入决定';
    $('#run-description').textContent=`最多执行 ${p.validation_passes||2} 轮，输出验证器检查结果并决定是否进入下一轮。通信量由验证器检查。`;
    $('#separate-receiver').checked=false;
  }
  if(isTestlibCommunication(p)){
    $('#solution-protocol').textContent='首轮交互 · 次轮读取 tout · 每轮同一程序';
    $('#run-description').textContent='首轮 interactor 与选手交互，tout 转为次轮输入；checker 检查第二轮输出。';
    $('#separate-receiver').checked=false;
  }
  $('#separate-receiver-label').hidden=p.mode!=='communication'||isMultipass(p)||isTestlibCommunication(p);
  $('#receiver-card').hidden=p.mode!=='communication'||isMultipass(p)||isTestlibCommunication(p)||!$('#separate-receiver').checked;
  const hasSource=!!$('#solution').value.trim();
  $('#invocation-source').textContent=hasSource?`${state.solutionName} · ${languages[$('#solution-language').value][0]}`:'尚未填写待测程序';
  $('#invocation-tests').textContent=dataReady()?`${p.dataset.cases.length} 个测试点 · r${p.dataset.revision}`:state.dirty?'保存后检查数据状态':p.dataset?'测试数据需要更新':'尚无测试数据';
  $('#invocation-limits').textContent=`${p.time_ms} ms · ${p.memory_mb} MiB`;
  $('#invocation-mode').textContent=modeNames[p.mode]+(p.mode==='communication'?' · 每阶段独立限制':'');
  $('#invocation-hint').innerHTML=!hasSource?'先在 <button class="text-button teal" data-go="solution">Solution</button> 中上传或粘贴待测程序。':!dataReady()?'开始评测时会先保存修改。请确认 <button class="text-button teal" data-go="tests">Tests</button> 中的数据已生成并验证。':'将使用当前保存版本的全部测试点运行待测程序，下方会显示逐点结果与执行日志。';
  renderInvocationPicker();
}
function showTab(tab) {
  tab=tabAliases[tab]||tab;
  if(!workspaceTabs.includes(tab))tab='general';
  state.tab=tab;
  document.querySelectorAll('[data-tab]').forEach(b=>{const active=b.dataset.tab===tab;b.classList.toggle('active',active);b.setAttribute('aria-selected',String(active));b.tabIndex=active?0:-1;});
  document.querySelectorAll('.panel').forEach(p=>p.hidden=p.id!=='panel-'+tab);
  if(state.p)history.replaceState(null,'',`#${state.p.id}/${tab}`);
  if(tab==='tests')renderData();if(['solution','invocations'].includes(tab))renderRun();if(tab==='general')renderPreparation();
}
async function selectProblem(id, tab='general') {
  if(state.p&&state.dirty)await save();
  await savePaperIfDirty();materials.paper=null;$('#papers-workspace').hidden=true;
  const p=await api('/api/studio/problems/'+id);
  state.p=p;state.dirty=false;state.jobs=[];state.generationJob=null;state.submissionJob=null;
  renderJob(null,'#generation-job');renderJob(null,'#submission-job');state.renderedJobs.clear();
  try {const draft=JSON.parse(localStorage.getItem(draftKey()));if(draft?.revision===p.revision){state.p={...draft,problem_code:p.problem_code};state.dirty=true;toast('已恢复此题未保存的本地草稿');}}catch(_){}
  const selected=state.p;
  $('#welcome').hidden=true;$('#editor').hidden=false;
  for(const key of ['title','statement','generation'])$('#'+key).value=selected[key];
  let solution={code:'',language:'cpp',name:'main.cpp'};
  try{solution=JSON.parse(localStorage.getItem('newjudge-solution-'+id))||solution;}catch(_){}
  $('#solution').value=solution.code;$('#solution-language').value=solution.language;state.solutionName=solution.name;$('#solution-name').textContent=solution.name;
  $('#receiver').value='';$('#separate-receiver').checked=false;
  renderMeta();renderLibrary();renderConfig();renderPreview();renderData();renderRun();showTab(tab);
  await loadJobs();
}
async function save() {
  if(!state.p)return;
  if(state.savePromise)return state.savePromise;
  const version=state.editVersion, pid=state.p.id;
  state.savePromise=(async()=>{
    const p=await api('/api/studio/problems/'+pid,'PUT',state.p);
    if(state.p?.id!==pid)return;
    if(version===state.editVersion){state.p=p;state.dirty=false;localStorage.removeItem(draftKey());}
    else {state.p.revision=p.revision;state.p.dataset=p.dataset;state.p.data_ready=false;setDirty();}
    renderMeta();renderConfig();renderData();renderRun();await refreshLibrary();
  })();
  try{return await state.savePromise;}finally{state.savePromise=null;}
}
async function create(template) {
  if(state.p&&state.dirty)await save();
  await savePaperIfDirty();
  const p=await api('/api/studio/problems','POST',template?{template}:{});
  $('#modal').close();await refreshLibrary();await selectProblem(p.id);
  if(template)toast('示例已创建，testlib 程序与生成参数已填入');else $('#title').select();
}
function openModal(title,body,actions='') {
  $('#modal-error').hidden=true;$('#modal-error').textContent='';
  $('#modal-title').textContent=title;$('#modal-body').innerHTML=body;$('#modal-actions').innerHTML=actions;
  if(!$('#modal').open)$('#modal').showModal();
}
function clearProblem() {
  state.p=null;state.dirty=false;state.jobs=[];state.generationJob=null;state.submissionJob=null;
  $('#editor').hidden=true;$('#welcome').hidden=false;
  $('#breadcrumb-title').textContent='录题工作台';document.title='Sakura Studio · 录题工作台';
  history.replaceState(null,'',location.pathname+location.search);
  renderJob(null,'#generation-job');renderJob(null,'#submission-job');renderLibrary();
}
async function confirmTrash() {
  if(!state.p)return;
  const pid=state.p.id;
  if(state.dirty||state.savePromise)await save();
  if(state.p?.id!==pid)return;
  if(state.dirty)throw new Error('保存期间又有修改，请先保存最新内容');
  state.trashProblem={id:pid,revision:state.p.revision,title:state.p.title};
  openModal('删除题目',`<p class="trash-confirm">将「<strong>${esc(state.p.title)}</strong>」移入回收站？</p><p class="modal-caption">题面、程序、测试数据和评测记录都会保留，可以随时从右上角「回收站」恢复。</p>`,
    '<button class="button secondary" data-action="close-modal">取消</button><button class="button danger" data-action="confirm-trash">移入回收站</button>');
}
async function trashProblem() {
  const p=state.trashProblem;if(!p)return;
  await api(`/api/studio/problems/${p.id}/trash`,'POST',{revision:p.revision});
  state.trashProblem=null;$('#modal').close();
  if(state.p?.id===p.id)clearProblem();
  await refreshLibrary();
  if(!state.p&&state.problems.length)await selectProblem(state.problems[0].id);
  toast('「'+p.title+'」已移入回收站，可从右上角恢复');
}
async function openTrash() {
  state.trashed=(await api('/api/studio/trash')).problems;
  openModal('回收站',`<p class="modal-caption">删除的题目会保存在这里，恢复后可继续编辑和评测。</p>${state.trashed.length?'<div class="trash-list">'+state.trashed.map(p=>`<div class="trash-item"><div><strong>${esc(p.title)}</strong><small>${modeNames[p.mode]} · ${esc(p.problem_code)} · ${date(p.deleted_at)} 删除</small></div><button class="button secondary" data-restore="${p.id}">恢复</button></div>`).join('')+'</div>':'<div class="empty-state">回收站为空。</div>'}`);
}
async function restoreProblem(pid) {
  const p=state.trashed.find(item=>item.id===pid);if(!p)return;
  await api(`/api/studio/problems/${pid}/restore`,'POST',{revision:p.revision});
  $('#modal').close();await refreshLibrary();
  if(!state.p)await selectProblem(pid);
  toast('「'+p.title+'」已恢复到题目库');
}
function renderJob(job, container) {
  const el=$(container);if(!job){el.innerHTML='';delete el.dataset.stamp;return;}
  const stamp=job.id+job.updated+job.state;
  if(el.dataset.stamp===stamp)return;el.dataset.stamp=stamp;
  state.renderedJobs.set(job.id,job);
  if(job.kind==='invoke'){renderBatchJob(job,el);return;}
  const running=['running','queued'].includes(job.state), cases=job.cases||[];
  const label=running?(job.state==='queued'?'排队中':'运行中'):job.state==='failed'?'任务失败':job.kind==='generate'?'数据已生成':'评测完成';
  const verdict=job.verdict||(job.state==='done'?'done':job.state);
  el.innerHTML=`<div class="job-card"><div class="job-top"><div>${badge(verdict)}<h3>${label}</h3><small>r${job.revision||state.p.revision} · ${job.progress||0}%</small></div><small>${date(job.created)}</small></div><div class="progress-track"><div style="width:${Math.max(0,Math.min(100,job.progress||0))}%"></div></div>${job.error||job.message?`<div class="job-error">${esc(job.error||job.message)}</div>`:''}${job.kind!=='generate'&&cases.length?`<table class="data-table"><thead><tr><th>测试点</th><th>结果</th><th>CPU 时间</th><th>峰值内存</th>${state.p.mode==='communication'?'<th>消息</th>':''}<th></th></tr></thead><tbody>${cases.map((c,i)=>`<tr><td>#${esc(c.id)}</td><td>${badge(c.verdict)}</td><td>${c.time_ms.toFixed(1)} ms</td><td>${bytes(c.memory_kb*1024)}</td>${state.p.mode==='communication'?`<td>${c.message_bytes??'—'} B</td>`:''}<td><button class="text-button teal" data-result="${job.id}:${i}">详情 ↗</button></td></tr>`).join('')}</tbody></table>`:''}<details ${running||job.state==='failed'?'open':''}><summary>执行日志 · ${(job.log||[]).length} 条</summary><pre class="job-log">${esc((job.log||[]).join('\n'))}</pre></details></div>`;
  const log=el.querySelector('.job-log');if(running&&log)log.scrollTop=log.scrollHeight;
}
function renderHistory() {
  const trials=state.jobs.filter(j=>['submit','invoke'].includes(j.kind)), generated=state.jobs.filter(j=>j.kind==='generate');
  $('#invocation-count').textContent=`最近记录中共 ${trials.length} 次评测`;
  $('#job-history').innerHTML=trials.length?`<table class="data-table"><thead><tr><th>时间</th><th>版本</th><th>结果</th><th>预期检查 / 通过测试点</th><th>类型</th><th></th></tr></thead><tbody>${trials.map(j=>`<tr><td>${date(j.created)}</td><td>r${j.revision||'—'}</td><td>${badge(j.verdict||j.state)}</td><td>${j.kind==='invoke'?`${j.matched_count??(j.runs||[]).filter(r=>r.matches_expected).length} / ${(j.runs||j.solution_ids||[]).length} 份符合`:`${(j.cases||[]).filter(c=>c.verdict==='AC').length} / ${(j.cases||[]).length} 点 AC`}</td><td>${j.kind==='invoke'?'批量解法':'临时代码'}</td><td><button class="text-button teal" data-job="${j.id}">查看结果 →</button></td></tr>`).join('')}</tbody></table>`:'<div class="empty-state">暂无运行记录。选择解法后点击「运行所选」或「运行全部」。</div>';
  $('#generation-history').innerHTML=generated.length?`<table class="data-table"><thead><tr><th>时间</th><th>版本</th><th>状态</th><th>已生成测试点</th><th></th></tr></thead><tbody>${generated.map(j=>`<tr><td>${date(j.created)}</td><td>r${j.revision||'—'}</td><td>${badge(j.state)}</td><td>${(j.cases||[]).length}</td><td><button class="text-button teal" data-job="${j.id}">查看日志 →</button></td></tr>`).join('')}</tbody></table>`:'<div class="empty-state">暂无生成记录。</div>';
}

async function loadJobs() {
  const pid=state.p?.id;if(!pid)return;
  const result=await api(`/api/studio/problems/${pid}/jobs`);if(state.p?.id!==pid)return;
  state.jobs=result.jobs;
  state.generationJob=state.jobs.find(j=>j.kind==='generate')||null;
  state.submissionJob=state.jobs.find(j=>['submit','invoke'].includes(j.kind))||null;
  renderJob(state.generationJob,'#generation-job');renderJob(state.submissionJob,'#submission-job');renderHistory();
  schedulePoll();
}
function schedulePoll() {
  if(state.polling||!state.jobs.some(j=>['queued','running'].includes(j.state)))return;
  state.polling=true;
  setTimeout(async()=>{
    state.polling=false;const pid=state.p?.id;if(!pid)return;
    try {
      const oldActive=state.jobs.filter(j=>['queued','running'].includes(j.state)).map(j=>j.id);
      const result=await api(`/api/studio/problems/${pid}/jobs`);if(state.p?.id!==pid)return;
      state.jobs=result.jobs;
      for(const field of ['generationJob','submissionJob']){const old=state[field];if(old)state[field]=state.jobs.find(j=>j.id===old.id)||old;}
      renderJob(state.generationJob,'#generation-job');renderJob(state.submissionJob,'#submission-job');renderHistory();
      const finished=state.jobs.filter(j=>oldActive.includes(j.id)&&!['queued','running'].includes(j.state));
      if(finished.length){
        const fresh=await api('/api/studio/problems/'+pid);
        if(state.p?.id!==pid)return;
        if(!state.dirty)state.p=fresh;else{state.p.dataset=fresh.dataset;state.p.data_ready=false;}
        renderMeta();renderConfig();renderData();renderRun();await refreshLibrary();
        for(const j of finished)toast(j.state==='failed'?'任务失败，请查看执行日志':j.kind==='generate'?'测试数据已生成并验证':'评测完成：'+j.verdict,j.state==='failed');
      }
    }catch(e){toast(e.message,true);}finally{schedulePoll();}
  },1200);
}
async function startJob(kind) {
  if(state.dirty)await save();
  if(state.dirty)throw new Error('保存期间又有修改，请先保存最新内容');
  const body={revision:state.p.revision};
  if(kind==='submit'){
    if(!$('#solution').value.trim()){showTab('solution');$('.temporary-solution').open=true;throw new Error('请先填写临时代码');}
    body.solution=programSource($('#solution-language').value,$('#solution').value);
    if(state.p.mode==='communication'&&$('#separate-receiver').checked)body.receiver=programSource($('#receiver-language').value,$('#receiver').value);
  }
  const job=await api(`/api/studio/problems/${state.p.id}/${kind}`,'POST',body);
  state[kind==='generate'?'generationJob':'submissionJob']=job;
  state.jobs.unshift(job);showTab(kind==='generate'?'tests':'invocations');
  renderJob(job,kind==='generate'?'#generation-job':'#submission-job');renderHistory();schedulePoll();
}
function saveSolution() {
  state.solutionName=languages[$('#solution-language').value][1];
  $('#solution-name').textContent=state.solutionName;
  try{localStorage.setItem('newjudge-solution-'+state.p.id,JSON.stringify({code:$('#solution').value,language:$('#solution-language').value,name:state.solutionName}));}catch(_){}
  renderRun();
}
function pickFile(role) {
  state.uploadRole=role;
  const picker=$('#file-picker');picker.accept=['solution','reference'].includes(role)?'.c,.cpp,.cc,.cxx,.py,.java':'.cpp,.cc,.cxx';picker.value='';picker.click();
}
async function previewCase(file) {
  const data=await api(`/api/studio/problems/${state.p.id}/cases/${file}`);
  openModal(file,`<p class="modal-caption">${bytes(data.bytes)}${data.truncated?' · 仅预览前 64 KiB':''}</p><pre class="modal-code">${esc(data.content)||'（空文件）'}</pre>`,`<a class="button secondary" href="/api/studio/problems/${state.p.id}/cases/${file}?download=1">↓ 下载文件</a>`);
}
function resultDetails(id,index,runIndex) {
  const job=state.renderedJobs.get(id)||state.jobs.find(j=>j.id===id),c=(runIndex===undefined?job?.cases:job?.runs?.[Number(runIndex)]?.cases)?.[Number(index)];if(!c)return;
  const sections=[['checker / 评测信息',c.message],['程序 stderr',c.stderr],['交互器 stderr',c.judge_stderr],['输出 / 交互记录预览',c.output_preview]];
  if(c.phases)sections.push(['阶段详情',JSON.stringify(c.phases,null,2)]);
  if(c.passes)sections.push(['各轮详情',JSON.stringify(c.passes,null,2)]);
  if(c.interactor)sections.push(['交互器状态',JSON.stringify(c.interactor,null,2)]);
  openModal('测试点 #'+c.id+' · '+c.verdict,`<div class="detail-grid"><div>CPU 时间<b>${c.time_ms.toFixed(1)} ms</b></div><div>峰值内存<b>${bytes(c.memory_kb*1024)}</b></div><div>退出码 / 信号<b>${c.exit_code} / ${c.signal}</b></div></div>${sections.filter(([,v])=>v).map(([title,value])=>`<div class="detail-label">${title}</div><pre class="modal-code">${esc(value)}</pre>`).join('')}`);
}
function help() {
  openModal('录题工作区',`<div class="help-content"><p>按题目材料划分为七个分区，随时切换；修改后点击「保存题目」或按 Ctrl+S。</p><ol><li><b>General Info：</b>题目名称、题型、通信协议、时间与内存限制。</li><li><b>Statement：</b>Markdown 题面与 LaTeX 预览。</li><li><b>Checker：</b>答案检查程序；交互题在此配置 interactor，checker 可选。</li><li><b>Validator：</b>校验输入格式和数据范围。</li><li><b>Tests：</b>生成器、生成参数、输入与答案、生成日志。</li><li><b>Solution：</b>批量上传并保存解法，标记 Correct、Wrong、Time Limit、Memory Limit 等预期结果。指定唯一的 Main Correct 作为 std。临时代码可在折叠区单独试运行。</li><li><b>Invocations：</b>勾选部分或全部解法运行，查看结果矩阵、逐点详情及预期检查。Correct 必须全部 AC；其他标签至少出现一次对应结果，IE 始终视为异常。</li></ol><p>普通题和 run-twice 用 Main Correct 生成答案；交互题、testlib 两轮通信、多阶段题用 Main Correct 执行完整流程自检。交互器或 checker 需要 jury answer 时，在 Solution 单独配置普通输入输出答案生成程序。旧版参考标程继续兼容。</p><p><b>试卷管理：</b>从侧栏进入，按题目 ID 或下拉选择题目，调整顺序、预览和导出整卷。保存试卷不会复制题目，移除卷内题目也不会删除原题。</p><p>通过验证后，可发布到 OJ 或导出题包。</p></div>`);
}
function editProgram(role) {
  const file=state.p.programs[role]||{name:role+'.cpp',language:'cpp',content:''};
  state.modalRole=role;
  openModal(file.content?file.name:'新建 '+roles[role][0],`<p class="modal-caption">${roles[role][0]} · 应用后请保存题目</p>${role==='reference'?`<label>运行语言 <select id="reference-language" aria-label="标程语言">${languageOptions(file.language)}</select></label><p class="modal-caption">Python 可选 CPython 或 PyPy；Java 使用无 package 声明的 Main 类。</p>`:''}<textarea id="modal-source" class="modal-code modal-editor" spellcheck="false" aria-label="程序源码" placeholder="粘贴或编写源码">${esc(file.content)}</textarea>`,'<button class="button primary" data-action="save-code">应用修改</button>');
}

async function action(name) {
  if(materialActions.has(name))return materialAction(name);
  if(name==='publish'){
    if(state.dirty)await save();
    if(!state.p.data_ready)throw new Error('请先为当前评测配置生成并验证数据');
    const slug=state.p.publication?.slug || state.p.problem_code.toLowerCase();
    openModal('发布到 Sakura OJ',`<p class="modal-caption">保存当前题面、评测程序和测试数据的快照，供 OJ 提交使用。更新同一题目会保留历史提交结果。新生成的数据默认隐藏，原有公开样例保持可见。</p><input id="publish-slug" type="hidden" value="${esc(slug)}"><label class="publish-field">难度<input id="publish-difficulty" value="${esc(state.p.publication?.difficulty || '进阶')}" maxlength="20" aria-label="发布难度"></label>`,'<button class="button primary" data-action="confirm-publish">确认发布</button>');return;
  }
  if(name==='confirm-publish'){
    const published=await api(`/api/studio/problems/${state.p.id}/publish`,'POST',{revision:state.p.revision,slug:$('#publish-slug').value,difficulty:$('#publish-difficulty').value});
    state.p.publication=published.publication;renderPreparation();
    openModal('已发布到 OJ',`<p>《${esc(published.problem.title)}》已就绪。之后修改录题草稿不会自动改变已发布版本。</p>`,`<a class="button primary" href="${esc(published.url)}">打开 OJ 题目 →</a>`);return;
  }
  if(name==='new')return create();
  if(name==='templates')return openModal('选择一条示例流程',`<p class="modal-caption">包含题面、testlib 程序、标程与生成参数。创建后可以直接生成数据。</p><div class="modal-template-grid">${exampleCards()}</div>`);
  if(name==='close-modal')return $('#modal').close();
  if(name==='help')return help();
  if(name==='trash')return confirmTrash();
  if(name==='confirm-trash')return trashProblem();
  if(name==='open-trash')return openTrash();
  if(name==='save'){await save();toast('题目已保存');return;}
  if(name==='export'){if(state.dirty)await save();const a=document.createElement('a');a.href=`/api/studio/problems/${state.p.id}/export`;a.download='problem-'+state.p.id+'.zip';a.click();if(!state.p.data_ready)toast('已导出题目配置；生成有效数据后，导出将包含测试点');return;}
  if(name==='generate')return startJob('generate');
  if(name==='submit')return startJob('submit');
  if(name==='upload-solution')return pickFile('solution');
  if(name==='copy-reference'){
    const file=mainSolution(state.p)||state.p.programs.reference;if(!file)throw new Error('请先在 Solution 中指定 Main Correct');
    if($('#solution').value.trim()&&!confirm('用参考标程替换当前待测代码？'))return;
    $('#solution').value=file.content;$('#solution-language').value=file.language;saveSolution();
    return;
  }
  if(name==='save-code'){
    const role=state.modalRole,content=$('#modal-source').value;
    if(!content.trim()||content.includes('\0')||new TextEncoder().encode(content).length>512*1024)throw new Error('源码不能为空，且不能超过 512 KiB');
    if(role==='reference')state.p.programs[role]=programSource($('#reference-language').value,content);
    else state.p.programs[role]={name:state.p.programs[role]?.name||role+'.cpp',language:'cpp',content};
    setDirty();renderConfig();renderData();renderRun();$('#modal').close();toast('程序已修改，保存后重新生成数据');return;
  }
  if(name==='statement-template'){
    if(state.p.statement.trim()&&!confirm('用空白题面模板替换当前题面？'))return;
    state.p.statement='# '+state.p.title+'\n\n## 题目描述\n\n在这里描述题目。\n\n## 输入格式\n\n## 输出格式\n\n## 样例\n\n输入：\n```text\n\n```\n\n输出：\n```text\n\n```\n\n## 数据范围\n\n$1 \\le n \\le 10^5$\n';
    $('#statement').value=state.p.statement;setDirty();renderPreview();return;
  }
}
document.addEventListener('click',async event=>{
  const el=event.target.closest('button,[data-go]');if(!el||el.disabled)return;
  try {
    if(el.dataset.action){const name=el.dataset.action;if(state.busy.has(name))return;state.busy.add(name);el.disabled=true;try{await action(name);}finally{state.busy.delete(name);el.disabled=false;}}
    else if(el.dataset.problem)await selectProblem(el.dataset.problem);
    else if(el.dataset.restore){el.disabled=true;try{await restoreProblem(el.dataset.restore);}finally{el.disabled=false;}}
    else if(el.dataset.example){el.disabled=true;try{await create(el.dataset.example);}finally{el.disabled=false;}}
    else if(el.dataset.tab||el.dataset.go)showTab(el.dataset.tab||el.dataset.go);
    else if(el.dataset.mode){state.p.mode=el.dataset.mode;setDirty();renderConfig();renderData();renderRun();}
    else if(el.dataset.upload)pickFile(el.dataset.upload);
    else if(el.dataset.remove){delete state.p.programs[el.dataset.remove];setDirty();renderConfig();renderData();renderRun();}
    else if(el.dataset.viewCode)editProgram(el.dataset.viewCode);
    else if(el.dataset.preview)await previewCase(el.dataset.preview);
    else if(el.dataset.result)resultDetails(...el.dataset.result.split(':'));
    else if(el.dataset.job){const job=await api('/api/studio/jobs/'+el.dataset.job);state[job.kind==='generate'?'generationJob':'submissionJob']=job;showTab(job.kind==='generate'?'tests':'invocations');renderJob(job,job.kind==='generate'?'#generation-job':'#submission-job');}
    else if(el.dataset.insert){const field=$('#statement'),selection=field.value.slice(field.selectionStart,field.selectionEnd),snippets={bold:['**','**'],heading:['\n## ','\n'],math:['$','$'],code:['\n```cpp\n','\n```\n']},[left,right]=snippets[el.dataset.insert];field.setRangeText(left+(selection||'内容')+right,field.selectionStart,field.selectionEnd,'select');state.p.statement=field.value;setDirty();renderPreview();field.focus();}
  }catch(e){toast(e.message,true);}
});
document.addEventListener('input',event=>{
  const el=event.target;
  if(el.dataset.key&&state.p){state.p[el.dataset.key]=el.type==='number'?Number(el.value):el.value;setDirty();if(el.id==='statement'){clearTimeout(previewTimer);previewTimer=setTimeout(renderPreview,120);}if(['time_ms','memory_mb','output_kb','message_bytes','validation_passes'].includes(el.id))renderRun();}
  if(el.id==='communication_protocol'){renderConfig();renderData();renderRun();}
  if(el.id==='search'){state.search=el.value;renderLibrary();}
  if(el.id==='solution'||el.id==='solution-language')saveSolution();
  if(el.id==='separate-receiver')renderRun();
});
$('#file-picker').addEventListener('change',async event=>{
  try {
    const file=event.target.files[0];if(!file)return;if(file.size>512*1024)throw new Error('源码文件不能超过 512 KiB');
    const suffix=file.name.split('.').pop().toLowerCase();
    let language={cpp:'cpp',cc:'cpp',cxx:'cpp',c:'c',py:'python',java:'java'}[suffix];
    if(!language||(language!=='cpp'&&!['reference','solution'].includes(state.uploadRole)))throw new Error('testlib 组件请上传 C++；标程和提交支持 C/C++、Python 3、PyPy 3、Java');
    const previous=state.uploadRole==='solution'?$('#solution-language').value:state.p.programs[state.uploadRole]?.language;
    if(suffix==='py'&&previous==='pypy')language='pypy';
    const content=await file.text();if(!content.trim()||content.includes('\0'))throw new Error('请选择非空的 UTF-8 源码文件');
    if(state.uploadRole==='solution'){$('#solution').value=content;$('#solution-language').value=language;saveSolution();}
    else {state.p.programs[state.uploadRole]={name:file.name,content,language};setDirty();renderConfig();renderData();renderRun();}
    toast(file.name+' 已载入');
  }catch(e){toast(e.message,true);}
});
document.addEventListener('keydown',event=>{
  if(event.target.matches('[role="tab"]')&&['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){
    event.preventDefault();const index=workspaceTabs.indexOf(state.tab),next=event.key==='Home'?0:event.key==='End'?workspaceTabs.length-1:(index+(event.key==='ArrowRight'?1:-1)+workspaceTabs.length)%workspaceTabs.length;
    showTab(workspaceTabs[next]);$('#tab-'+state.tab).focus();return;
  }
  if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='s'){event.preventDefault();if(!$('#modal').open&&state.p)action('save').catch(e=>toast(e.message,true));}
  if(event.key==='Tab'&&event.target.tagName==='TEXTAREA'){event.preventDefault();const el=event.target;el.setRangeText('    ',el.selectionStart,el.selectionEnd,'end');el.dispatchEvent(new Event('input',{bubbles:true}));}
  if(!['INPUT','TEXTAREA','SELECT'].includes(event.target.tagName)&&!$('#modal').open){if(event.key==='/'){event.preventDefault();$('#search').focus();}if(event.key.toLowerCase()==='n'&&!event.ctrlKey&&!event.metaKey)create().catch(e=>toast(e.message,true));}
});
window.addEventListener('hashchange',()=>{const [id,tab]=location.hash.slice(1).split('/');if(id==='papers'||id==='paper')showPapers(id==='paper'?tab:null).catch(e=>toast(e.message,true));else if(id===state.p?.id)showTab(tab);else if(state.problems.some(p=>p.id===id))selectProblem(id,tab).catch(e=>toast(e.message,true));else if(!id)materialAction('problem-library').catch(e=>toast(e.message,true));});
window.addEventListener('beforeunload',e=>{if(state.dirty){e.preventDefault();e.returnValue='';}});
async function init() {
  try {
    initMarkdown();$('#welcome-examples').innerHTML=exampleCards();
    $('#solution-language').innerHTML=languageOptions('cpp');$('#receiver-language').innerHTML=languageOptions('cpp');
    state.bootstrap=await api('/api/studio/bootstrap');state.csrf=state.bootstrap.csrf;
    const health=state.bootstrap.health;
    $('#engine-status').classList.toggle('offline',!health.ready);
    $('#engine-status').innerHTML=`<span class="status-light"></span><div>${health.ready?'评测机已连接':'评测机未就绪'}<small>newjudge / lrun · ${health.ready?'在线':'检查配置'}</small></div>`;
    $('#engine-status').title=health.error||health.kernel;
    await refreshLibrary();
    await refreshPapers();
    const [id,tab]=location.hash.slice(1).split('/');
    if(id==='papers'||id==='paper')await showPapers(id==='paper'?tab:null);
    else if(state.problems.some(p=>p.id===id))await selectProblem(id,tab);
  }catch(e){toast('初始化失败：'+e.message,true);$('#engine-status').classList.add('offline');}
}
init();

fetch('/api/auth/me').then(r=>r.ok?r.json():null).then(user=>{
  if(user && !['admin','teacher'].includes(user.role)) document.getElementById('team-link').hidden=true;
});
