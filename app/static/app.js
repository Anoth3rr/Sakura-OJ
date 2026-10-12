const state = {
  problems: [],
  selected: null,
  difficulty: "",
  search: "",
  pollTimer: null,
  toastTimer: null,
  searchTimer: null,
  languages: [],
  editorContext: null,
  templateContext: null,
  judgeReady: true,
  user: null,
  authMode: "login",
  authRequired: false,
  bankLoad: 0,
  bankSearchTimer: null,
  view: "library",
  page: 1,
  pageSize: 20,
  totalProblems: 0,
  problemLoad: 0,
  detailLoad: 0,
  bankItems: [],
  bankTotal: 0,
  editorDrafts: new Map(),
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const modeLabels = {normal: "普通题", interactive: "交互题", communication: "通信题"};

function canManageProblems() {
  return state.user ? ["admin", "problem_admin"].includes(state.user.role) : !state.authRequired;
}

function rememberEditor() {
  const context = state.editorContext;
  if (!context) return;
  const draft = state.editorDrafts.get(context.key) || {codes: new Map()};
  draft.language = context.language;
  draft.codes.set(context.language, $("#code-editor").value);
  state.editorDrafts.set(context.key, draft);
}

function editorOwner() {
  return state.user ? "user:" + state.user.id : "guest";
}

function templateStorageKey(owner, language) {
  return "sakura:code-template:v1:" + owner + ":" + language;
}

function readCodeTemplate(language) {
  try {
    return localStorage.getItem(templateStorageKey(editorOwner(), language)) || "";
  } catch {
    return "";
  }
}

function loadEditor(language) {
  if (!state.selected) return;
  const owner = editorOwner();
  const key = JSON.stringify([owner, state.selected.id]);
  const draft = state.editorDrafts.get(key);
  language ||= draft?.language || $("#language-select").value || "cpp";
  const available = [...$("#language-select").options].filter(option => !option.disabled);
  if (!available.some(option => option.value === language)) language = available[0]?.value || language;
  $("#language-select").value = language;
  $("#code-editor").value = draft?.codes.has(language) ? draft.codes.get(language) : readCodeTemplate(language);
  state.editorContext = {key, owner, language};
  updateEditorSize();
}

function openCodeTemplate() {
  const language = $("#language-select").value;
  const previous = readCodeTemplate(language);
  state.templateContext = {owner: editorOwner(), language, previous};
  $("#template-language-name").textContent = $("#language-select").selectedOptions[0]?.textContent || language;
  $("#template-code").value = previous;
  $("#template-feedback").textContent = "";
  $("#code-template-dialog").showModal();
}

function closeCodeTemplate() {
  $("#code-template-dialog").close();
  $("#template-code").value = "";
  state.templateContext = null;
}

function saveCodeTemplate(event) {
  event.preventDefault();
  const context = state.templateContext;
  if (!context || context.owner !== editorOwner()) {
    closeCodeTemplate();
    return;
  }
  const code = $("#template-code").value;
  const template = code.trim() ? code : "";
  try {
    const key = templateStorageKey(context.owner, context.language);
    if (template) localStorage.setItem(key, template);
    else localStorage.removeItem(key);
  } catch {
    $("#template-feedback").textContent = "模板未保存：浏览器存储不可用或空间不足，请保留并复制当前内容。";
    return;
  }
  const current = $("#code-editor").value;
  const canApply = state.editorContext?.owner === context.owner && state.editorContext?.language === context.language
    && (current === "" || current === context.previous);
  if (canApply) {
    $("#code-editor").value = template;
    updateEditorSize();
    rememberEditor();
  }
  closeCodeTemplate();
  showToast((template ? "个人模板已保存" : "已取消该语言的预设模板") + (canApply ? "" : "，当前代码已保留"));
}

function showView(view) {
  if (state.view === "detail" && view !== "detail") rememberEditor();
  state.view = view;
  if (view !== "detail") { ++state.detailLoad; clearInterval(state.pollTimer); }
  for (const [name, id] of Object.entries({library:"problem-library", detail:"problem-detail", bank:"problem-bank-page", submissions:"submissions-page"})) {
    $("#" + id).classList.toggle("is-hidden", name !== view);
  }
  $$(".top-nav a").forEach(link => link.classList.toggle("active", link.hash === (view === "bank" ? "#manage-problems" : view === "submissions" ? "#submissions" : "#problems")));
  document.title = view === "bank" ? "管理题库 · Sakura OJ" : view === "submissions" ? "提交记录 · Sakura OJ" : "Sakura OJ";
}

function acceptanceRate(accepted, total) {
  return total ? (100 * accepted / total).toFixed(2) + "%" : "—";
}

function tableMessage(body, message, columns) {
  body.replaceChildren();
  const row = document.createElement("tr"), cell = bankElement("td", message, "table-empty");
  cell.colSpan = columns;
  row.append(cell); body.append(row);
}

const verdictLabels = {
  PENDING: "等待判题",
  ACCEPTED: "Accepted",
  WRONG_ANSWER: "Wrong Answer",
  COMPILE_ERROR: "Compile Error",
  RUNTIME_ERROR: "Runtime Error",
  TIME_LIMIT_EXCEEDED: "Time Limit Exceeded",
  OUTPUT_LIMIT_EXCEEDED: "Output Limit Exceeded",
  SYSTEM_ERROR: "System Error",
  MEMORY_LIMIT_EXCEEDED: "Memory Limit Exceeded",
  PRESENTATION_ERROR: "Presentation Error",
  COMMUNICATION_LIMIT_EXCEEDED: "Communication Limit Exceeded",
};

const roleLabels = {
  admin: "管理员",
  problem_admin: "题目管理员",
  teacher: "老师",
  student: "学生",
};

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.remove("is-hidden");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => toast.classList.add("is-hidden"), 2800);
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const response = await fetch(path, {
    ...options,
    headers,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item && item.msg ? item.msg : String(item)).join("；")
      : typeof detail === "string" ? detail : "请求失败";
    throw new Error(message);
  }
  return body;
}

function renderAccount() {
  const loggedIn = Boolean(state.user);
  $("#login-button").classList.toggle("is-hidden", loggedIn);
  $("#register-button").classList.toggle("is-hidden", loggedIn);
  $("#account-profile").classList.toggle("is-hidden", !loggedIn);
  $('#nav-studio').classList.toggle('is-hidden', state.authRequired ? !loggedIn || !['admin','problem_admin'].includes(state.user.role) : loggedIn && !['admin','problem_admin'].includes(state.user.role));
  $('#nav-team').classList.toggle('is-hidden', state.authRequired ? !loggedIn || !['admin','teacher'].includes(state.user.role) : loggedIn && !['admin','teacher'].includes(state.user.role));
  $('#nav-manage-problems').classList.toggle('is-hidden', !canManageProblems());
  $('#nav-submissions').textContent = state.user && state.user.role !== 'student' ? '提交记录' : '我的提交';
  if (!loggedIn) return;
  $("#account-name").textContent = state.user.display_name || state.user.username;
  $("#account-role").textContent = state.user.role_label || roleLabels[state.user.role] || state.user.role;
  let manage = $("#manage-users-button");
  if (state.user.role === "admin") {
    if (!manage) {
      manage = document.createElement("button");
      manage.id = "manage-users-button";
      manage.className = "topbar-button";
      manage.type = "button";
      manage.textContent = "账号";
      manage.addEventListener("click", openUsersDialog);
      $("#account-profile").insertBefore(manage, $("#logout-button"));
    }
    manage.classList.remove("is-hidden");
  } else if (manage) {
    manage.classList.add("is-hidden");
  }
}

async function loadMe() {
  try {
    state.user = await api("/api/auth/me");
  } catch {
    state.user = null;
  }
  renderAccount();
}

function openAuthDialog(mode = "login") {
  state.authMode = mode;
  setAuthMode(mode);
  const dialog = $("#auth-dialog");
  if (typeof dialog.showModal === "function") dialog.showModal();
  else dialog.setAttribute("open", "");
  $("#auth-feedback").textContent = "";
  $("#auth-username").focus();
}

function closeAuthDialog() {
  const dialog = $("#auth-dialog");
  if (typeof dialog.close === "function") dialog.close();
  else dialog.removeAttribute("open");
}

function setAuthMode(mode) {
  state.authMode = mode === "register" ? "register" : "login";
  const registering = state.authMode === "register";
  $("#auth-title").textContent = registering ? "注册学生账号" : "登录";
  $("#auth-submit span").textContent = registering ? "注册并登录" : "登录";
  $("#auth-display-name-label").classList.toggle("is-hidden", !registering);
  $("#auth-password").setAttribute("autocomplete", registering ? "new-password" : "current-password");
  $("#auth-hint").textContent = registering
    ? "公开注册仅创建学生账号，老师和管理角色由管理员分配。"
    : "管理员创建的账号可直接登录。";
  $$(".auth-switch-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.authMode === state.authMode);
  });
}

async function submitAuth(event) {
  event.preventDefault();
  const form = $("#auth-form");
  const feedback = $("#auth-feedback");
  const button = $("#auth-submit");
  button.disabled = true;
  feedback.textContent = "";
  const formData = new FormData(form);
  const payload = {
    username: String(formData.get("username") || ""),
    password: String(formData.get("password") || ""),
  };
  if (state.authMode === "register") payload.display_name = String(formData.get("display_name") || "");
  try {
    const result = await api(state.authMode === "register" ? "/api/auth/register" : "/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.user = result.user;
    renderAccount();
    closeAuthDialog();
    const next = new URLSearchParams(location.search).get('next');
    if(['/studio/','/team/'].includes(next)){location.assign(next);return;}
    if(location.hash.startsWith('#submission/')){location.reload();return;}
    form.reset();
    if(canManageProblems())await loadProblemBank();
    await followHash();
    showToast(state.authMode === "register" ? "学生账号创建成功" : "登录成功");
  } catch (error) {
    feedback.textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

async function logout() {
  try {
    await api("/api/auth/logout", { method: "POST" });
  } catch {
    // Clear the local identity even if the session has already expired.
  }
  rememberEditor();
  state.user = null;
  closeCodeTemplate();
  loadEditor();
  renderAccount();
  state.bankItems = [];
  $("#problem-add-dialog").close();
  if (state.view === "bank" || state.view === "submissions") location.hash = "problems";
  renderProblemList();
  showToast("已退出登录");
}

function openUsersDialog() {
  const dialog = $("#users-dialog");
  if (typeof dialog.showModal === "function") dialog.showModal();
  else dialog.setAttribute("open", "");
  loadUsers();
}

function closeUsersDialog() {
  const dialog = $("#users-dialog");
  if (typeof dialog.close === "function") dialog.close();
  else dialog.removeAttribute("open");
}

function renderUsers(users) {
  const list = $("#users-list");
  list.replaceChildren();
  if (!users.length) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = "暂无账号";
    list.append(empty);
    return;
  }
  for (const user of users) {
    const row = document.createElement("div");
    row.className = "user-row";
    const identity = document.createElement("div");
    const name = document.createElement("strong");
    name.textContent = user.display_name || user.username;
    const username = document.createElement("small");
    username.textContent = "@" + user.username;
    identity.append(name, username);
    const role = document.createElement("select");
    role.setAttribute("aria-label", user.username + " 的角色");
    for (const [value, label] of Object.entries(roleLabels)) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = label;
      option.selected = value === user.role;
      role.append(option);
    }
    role.addEventListener("change", () => updateUser(user.id, { role: role.value }));
    const stateText = document.createElement("span");
    stateText.textContent = user.is_active ? "启用" : "停用";
    stateText.className = user.is_active ? "verdict-good" : "verdict-bad";
    role.disabled = user.id === state.user?.id;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "danger-button";
    remove.textContent = "删除";
    remove.setAttribute("aria-label", "删除账号 " + user.username);
    remove.disabled = user.id === state.user?.id;
    remove.title = remove.disabled ? "不能删除当前登录账号" : "删除账号并撤销登录会话";
    remove.addEventListener("click", () => deleteManagedUser(user, remove));
    row.append(identity, role, stateText, remove);
    list.append(row);
  }
}

async function loadUsers() {
  try {
    renderUsers(await api("/api/users"));
    $("#users-feedback").textContent = "";
  } catch (error) {
    $("#users-feedback").textContent = error.message;
  }
}

async function updateUser(userId, payload) {
  try {
    await api("/api/users/" + userId, { method: "PATCH", body: JSON.stringify(payload) });
    await loadUsers();
    showToast("角色已更新");
  } catch (error) {
    await loadUsers();
    $("#users-feedback").textContent = error.message;
  }
}

async function createManagedUser(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const feedback = $("#users-feedback");
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    await api("/api/users", { method: "POST", body: JSON.stringify(payload) });
    form.reset();
    await loadUsers();
    showToast("账号创建成功");
  } catch (error) {
    feedback.textContent = error.message;
  }
}

function confirmManagement(title, message) {
  const dialog = $("#management-confirm");
  $("#management-confirm-title").textContent = title;
  $("#management-confirm-text").textContent = message;
  return new Promise((resolve) => {
    const finish = (accepted) => { dialog.close(); resolve(accepted); };
    $("#confirm-management").onclick = () => finish(true);
    $("#cancel-management").onclick = () => finish(false);
    dialog.oncancel = (event) => { event.preventDefault(); finish(false); };
    dialog.showModal();
  });
}

async function deleteManagedUser(user, button) {
  button.disabled = true;
  try {
    if (!await confirmManagement("删除账号 @" + user.username, "该账号将无法登录，所有登录会话立即失效。历史提交保留，原用户名不可重新注册。确认删除吗？")) return;
    await api("/api/users/" + user.id, { method: "DELETE" });
    await loadUsers();
    showToast("账号已删除");
  } catch (error) {
    $("#users-feedback").textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

function bankElement(tag, text, className = "") {
  const element = document.createElement(tag);
  element.textContent = text;
  element.className = className;
  return element;
}

async function openProblemBank() {
  if (!canManageProblems()) {
    showView("library");
    if (!state.user) openAuthDialog("login");
    else showToast("当前账号没有管理题库的权限");
    return;
  }
  showView("bank");
  $("#bank-feedback").textContent = "";
  await loadProblemBank();
}

async function loadProblemBank() {
  const load = ++state.bankLoad;
  try {
    const result = await api("/api/problem-bank?search=" + encodeURIComponent($("#bank-search").value));
    if (load !== state.bankLoad) return;
    state.bankItems = result.items;
    state.bankTotal = result.total;
    renderProblemBank();
    renderProblemList();
  } catch (error) {
    $("#bank-feedback").textContent = error.message;
  }
}

function renderProblemBank() {
    const rows = $("#bank-rows"); rows.replaceChildren();
    $("#bank-feedback").textContent = "";
    const select = $("#bank-select");
    const selectedCode = select.value;
    select.replaceChildren(bankElement("option", "请选择题目"));
    select.options[0].value = "";
    const filter = $("#bank-status").value;
    const items = state.bankItems.filter(item => filter === "trashed" ? item.trashed && !item.listed : filter === "listed" ? item.listed : filter === "unlisted" ? !item.listed && !item.trashed : !item.trashed || item.listed);
    $("#bank-count").textContent = items.length;
    for (const item of state.bankItems.filter(item => item.can_add)) {
      const option = bankElement("option", `${item.problem_code} · ${item.title}`);
      option.value = item.problem_code; select.append(option);
    }
    if (state.bankItems.some(item => item.can_add && item.problem_code === selectedCode)) select.value = selectedCode;
    for (const item of items) {
      const label = item.listed ? "已在题库" : item.can_add ? "可添加" : item.trashed ? "草稿在回收站" : "待生成数据";
      const row = document.createElement("tr");
      row.append(bankElement("td", item.problem_code, "bank-code"), bankElement("td", item.title, "table-title"),
        bankElement("td", modeLabels[item.mode] || item.mode), bankElement("td", item.difficulty || "—"),
        bankElement("td", item.submission_count, "numeric"), bankElement("td", acceptanceRate(item.accepted_count, item.submission_count), "numeric"),
        bankElement("td", label, item.listed ? "listed-status" : "draft-status"));
      const actions = bankElement("td", "", "bank-actions");
      if (item.listed && item.url) {
        const preview = bankElement("a", "预览", "text-link");
        preview.href = item.url;
        preview.setAttribute("aria-label", "预览题目 " + item.problem_code);
        actions.append(preview);
      }
      if (item.studio_url) {
        const edit = bankElement("a", "编辑", "text-link");
        edit.href = item.studio_url;
        edit.setAttribute("aria-label", "编辑题目 " + item.problem_code);
        actions.append(edit);
      }
      if (item.listed || item.can_add) {
        const action = bankElement("button", item.listed ? "删除" : "添加", item.listed ? "text-link text-danger" : "text-link");
        action.type = "button";
        action.setAttribute("aria-label", (item.listed ? "从题库删除 " : "添加题目 ") + item.problem_code);
        action.addEventListener("click", () => item.listed ? removeBankProblem(item, action) : addBankProblem(item.problem_code, action));
        actions.append(action);
      }
      row.append(actions);
      rows.append(row);
    }
    if (!items.length) tableMessage(rows, "未找到题目，请调整筛选或前往录题工作台创建。", 8);
    if (state.bankTotal > state.bankItems.length) $("#bank-feedback").textContent = "当前检索前 200 项，可按 ID 或标题缩小范围。";
}

async function refreshBankAndProblems() {
  await Promise.all([loadProblemBank(), loadStats(), loadProblems()]);
}

async function addBankProblem(code, button) {
  button.disabled = true;
  $("#bank-feedback").textContent = "";
  $("#bank-add-feedback").textContent = "";
  try {
    const result = await api("/api/problem-bank", { method:"POST", body:JSON.stringify({problem_code:code.trim()}) });
    $("#bank-code").value = result.problem.problem_code;
    await refreshBankAndProblems();
    $("#problem-add-dialog").close();
    showToast(result.problem.problem_code + " 已加入题库");
  } catch (error) {
    $($("#problem-add-dialog").open ? "#bank-add-feedback" : "#bank-feedback").textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

async function removeBankProblem(item, button) {
  button.disabled = true;
  try {
    if (!await confirmManagement("从题库删除 " + item.problem_code, `《${item.title}》将停止公开访问和接受新提交。草稿、发布数据和历史提交保留，可用原 ID 重新添加。`)) return;
    await api("/api/problem-bank/" + encodeURIComponent(item.problem_code), {method:"DELETE"});
    if (state.selected?.problem_code === item.problem_code) state.selected = null;
    await refreshBankAndProblems();
    showToast(item.problem_code + " 已移出题库");
  } catch (error) {
    $("#bank-feedback").textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("zh-CN", { hour12: false });
}

function formatBytes(length) {
  if (length < 1024) return length + " B";
  return (length / 1024).toFixed(1) + " KB";
}

function renderProblemList() {
  const list = $("#problem-list");
  list.replaceChildren();
  $("#problem-count").textContent = state.totalProblems;
  const pages = Math.max(1, Math.ceil(state.totalProblems / state.pageSize));
  $("#page-number").textContent = `${state.page} / ${pages}`;
  $("#page-summary").textContent = state.totalProblems ? `第 ${(state.page - 1) * state.pageSize + 1}–${Math.min(state.page * state.pageSize, state.totalProblems)} 项，共 ${state.totalProblems} 道题目` : "共 0 道题目";
  $("#previous-page").disabled = state.page <= 1;
  $("#next-page").disabled = state.page >= pages;
  if (!state.problems.length) {
    tableMessage(list, "没有找到匹配题目，请调整搜索或筛选条件。", 7);
    return;
  }
  for (const problem of state.problems) {
    const row = document.createElement("tr"), titleCell = bankElement("td", "", "table-title");
    const title = bankElement("a", problem.title, "problem-title-link");
    title.href = "#problem/" + encodeURIComponent(problem.slug);
    titleCell.append(title);
    row.append(bankElement("td", problem.problem_code, "bank-code"), titleCell,
      bankElement("td", modeLabels[problem.judge_mode] || "普通题"), bankElement("td", problem.difficulty),
      bankElement("td", problem.submission_count, "numeric"), bankElement("td", acceptanceRate(problem.accepted_count, problem.submission_count), "numeric"));
    const actions = bankElement("td", "", "bank-actions"), preview = bankElement("a", "预览", "text-link");
    preview.href = title.href;
    preview.setAttribute("aria-label", "预览题目 " + problem.problem_code);
    actions.append(preview);
    const managed = canManageProblems() && state.bankItems.find(item => item.problem_code === problem.problem_code);
    if (managed?.studio_url) {
      const edit = bankElement("a", "编辑", "text-link");
      edit.href = managed.studio_url;
      edit.setAttribute("aria-label", "编辑题目 " + problem.problem_code);
      actions.append(edit);
    }
    row.append(actions); list.append(row);
  }
}

function showProblemTab(name, focusEditor = false) {
  $$("#problem-view .tab").forEach(button => {
    const selected = button.dataset.tab === name;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-selected", String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
  $$("#problem-view .tab-panel").forEach(panel => panel.classList.toggle("is-hidden", panel.id !== name + "-panel"));
  $("#problem-outline-card").classList.toggle("is-hidden", name !== "statement");
  if (focusEditor) $("#code-editor").focus({preventScroll: true});
}

function renderProblem(problem) {
  rememberEditor();
  state.selected = problem;
  showProblemTab("statement");
  $("#empty-state").classList.add("is-hidden");
  $("#problem-view").classList.remove("is-hidden");
  $("#problem-title").textContent = problem.title;
  $("#problem-difficulty").textContent = problem.difficulty;
  $("#problem-difficulty").dataset.level = problem.difficulty;
  $("#problem-mode").textContent = modeLabels[problem.judge_mode || "normal"];
  $("#problem-time").textContent = (problem.time_limit_ms / 1000).toFixed(2) + " s";
  $("#problem-memory").textContent = problem.memory_limit_mb + " MB";
  $("#problem-submissions").textContent = problem.submission_count;
  $("#problem-accepted").textContent = problem.accepted_count;
  $("#problem-rate").textContent = acceptanceRate(problem.accepted_count, problem.submission_count);
  loadEditor();
  renderStatement(problem);
  $("#history-panel").replaceChildren(bankElement("p", "正在加载提交记录…", "history-empty"));
  loadHistory(problem.id);
  renderProblemList();
  document.title = problem.title + " · Sakura OJ";
  $("#submission-card").classList.add("is-hidden");
  clearInterval(state.pollTimer);
}

async function copyText(text, message) {
  try {
    await navigator.clipboard.writeText(text);
    showToast(message);
  } catch {
    showToast("复制失败，请手动选择并复制内容");
  }
}

function renderStatement(problem) {
  const panel = $("#statement-panel");
  panel.replaceChildren();
  const content = bankElement("div", "", "statement-content markdown-body");
  // All HTML fragments are sanitized by the API Markdown renderer.
  content.innerHTML = problem.statement_html || "";
  const first = content.firstElementChild;
  const firstTitle = first?.textContent.trim() || "";
  const numberedTitle = firstTitle.match(/^(P?\d+)\s+(.+)$/i);
  if (first?.matches("h1") && (firstTitle === problem.title || (numberedTitle
    && numberedTitle[2] === problem.title && Number(numberedTitle[1].replace(/^P/i, "")) === Number(problem.problem_code)))) first.remove();
  for (const title of content.querySelectorAll("h1")) {
    const heading = document.createElement("h2");
    heading.append(...title.childNodes);
    title.replaceWith(heading);
  }
  if (!content.firstElementChild?.matches("h2,h3,h4")) content.prepend(bankElement("h2", "题目描述"));
  const headingNames = new Set([...content.querySelectorAll("h2,h3,h4")].map(heading => heading.textContent.replace(/[\s：:]/g, "")));
  const sourceParts = [problem.statement_markdown || problem.description || ""];
  for (const [title, text, html, aliases] of [
    ["输入格式", problem.input_format, problem.input_format_html, ["输入格式", "输入描述"]],
    ["输出格式", problem.output_format, problem.output_format_html, ["输出格式", "输出描述"]],
  ]) {
    // Studio statements already contain their sections; avoid legacy placeholder duplicates.
    if (!text?.trim() || text.trim() === "见题面中的输入与交互协议。" || text.trim() === "见题面中的输出与交互协议。" || aliases.some(name => headingNames.has(name))) continue;
    content.append(bankElement("h2", title));
    const body = document.createElement("div");
    if (html) body.innerHTML = html;
    else body.append(bankElement("p", text));
    content.append(body);
    sourceParts.push("## " + title + "\n\n" + text);
  }
  formatInlineSamples(content);
  const extraSamples = renderSamples(problem, content);
  if (extraSamples.length) {
    const examples = extraSamples.map(({sample, number}) => [
      ["input", sample.input_data], ["output", sample.expected_output],
    ].map(([kind, text]) => {
      const fence = "`".repeat(Math.max(3, ...(text.match(/`+/g) || []).map(run => run.length + 1)));
      return fence + "text " + kind + ":#" + number + "\n" + text + (text.endsWith("\n") ? "" : "\n") + fence;
    }).join("\n\n")).join("\n\n");
    sourceParts.push("## 输入输出样例\n\n" + examples);
  }
  const toolbar = bankElement("div", "", "statement-toolbar");
  const copy = bankElement("button", "复制 Markdown", "statement-tool");
  copy.type = "button";
  copy.addEventListener("click", () => copyText(sourceParts.join("\n\n"), "题面 Markdown 已复制"));
  toolbar.append(copy);
  panel.append(toolbar, content);
  const outline = $("#problem-outline");
  outline.replaceChildren();
  content.querySelectorAll("h2,h3").forEach((heading, index) => {
    heading.id = "statement-section-" + index;
    const button = bankElement("button", heading.textContent, heading.tagName === "H3" ? "outline-child" : "");
    button.type = "button";
    button.addEventListener("click", () => {
      showProblemTab("statement");
      heading.scrollIntoView({behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start"});
    });
    outline.append(button);
  });
  typesetMath(panel);
}

function typesetMath(root) {
  if (!window.katex || typeof window.katex.render !== "function") return;
  const renderElement = (element) => {
    if (element.dataset.katexRendered === "true") return;
    const source = element.textContent || "";
    const displayMode = element.classList.contains("math-display");
    const formula = displayMode
      ? source.replace(/^\\\[/, "").replace(/\\\]$/, "")
      : source.replace(/^\\\(/, "").replace(/\\\)$/, "");
    try {
      window.katex.render(formula, element, { displayMode, throwOnError: false, output: "htmlAndMathml" });
      element.dataset.katexRendered = "true";
    } catch {
      // Keep the escaped delimiters visible when a malformed formula is entered.
    }
  };
  if (root.matches && root.matches(".math-inline, .math-display")) renderElement(root);
  root.querySelectorAll(".math-inline, .math-display").forEach(renderElement);
}

function sampleBlock(kind, number, text) {
  const label = (kind === "input" ? "输入" : "输出") + " #" + number;
  const block = bankElement("div", "", "sample-block");
  block.dataset.sampleKind = kind;
  block.dataset.sampleNumber = number;
  const header = document.createElement("header");
  const copy = bankElement("button", "复制", "sample-copy");
  copy.type = "button";
  copy.setAttribute("aria-label", "复制" + label);
  copy.addEventListener("click", () => copyText(text, label + " 已复制"));
  header.append(bankElement("span", label), copy);
  block.append(header, bankElement("pre", text));
  return block;
}

function formatInlineSamples(content) {
  // Metadata identifies explicit `text input:#1` / `text output:#1` fences.
  for (const code of content.querySelectorAll("pre > code[data-sample-kind]")) {
    const pre = code.parentElement;
    if (!content.contains(pre)) continue;
    const next = pre.nextElementSibling;
    const output = next?.matches("pre") ? next.querySelector("code[data-sample-kind='output']") : null;
    const pair = bankElement("div", "", "sample-case-body");
    pair.append(sampleBlock(code.dataset.sampleKind, code.dataset.sampleNumber, code.textContent));
    if (code.dataset.sampleKind === "input" && output?.dataset.sampleNumber === code.dataset.sampleNumber) {
      pair.append(sampleBlock("output", output.dataset.sampleNumber, output.textContent));
      next.remove();
    } else pair.classList.add("single-sample");
    pre.replaceWith(pair);
  }
}

function renderSamples(problem, content) {
  const blocks = [...content.querySelectorAll(".sample-block")];
  const sameText = (a, b) => a.replace(/\r\n?/g, "\n").replace(/\n$/, "") === b.replace(/\r\n?/g, "\n").replace(/\n$/, "");
  const samples = (problem.test_cases || []).map((sample, index) => ({sample, number: index + 1})).filter(({sample, number}) =>
    ![["input", sample.input_data], ["output", sample.expected_output]].every(([kind, text]) =>
      blocks.some(block => block.dataset.sampleKind === kind && block.dataset.sampleNumber === String(number) && sameText(block.querySelector("pre").textContent, text))));
  if (!samples.length) return [];
  content.append(bankElement("h2", "输入输出样例"));
  const list = bankElement("div", "", "sample-list");
  samples.forEach(({sample, number}) => {
    const pair = bankElement("div", "", "sample-case-body");
    pair.append(sampleBlock("input", number, sample.input_data), sampleBlock("output", number, sample.expected_output));
    list.append(pair);
  });
  content.append(list);
  return samples;
}

function renderHistory(items) {
  const panel = $("#history-panel");
  panel.replaceChildren(bankElement("h2", "提交记录", "panel-title"));
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = "还没有提交记录";
    panel.append(empty);
    return;
  }
  const list = document.createElement("div");
  list.className = "history-list";
  for (const item of items) {
    const row = document.createElement("div");
    row.className = "history-row";
    const id = document.createElement("span");
    id.className = "history-id";
    id.textContent = item.id.slice(0, 10);
    const verdict = document.createElement("span");
    verdict.className = item.verdict === "ACCEPTED" ? "verdict-good" : "verdict-bad";
    verdict.textContent = verdictLabels[item.verdict] || item.verdict;
    const score = document.createElement("span");
    score.textContent = item.score + " 分";
    const date = document.createElement("span");
    date.className = "history-date";
    date.textContent = formatDate(item.created_at);
    row.append(id, verdict, score, date);
    row.addEventListener("click", () => loadSubmission(item.id));
    row.style.cursor = "pointer";
    list.append(row);
  }
  panel.append(list);
}

async function loadHistory(problemId) {
  try {
    const data = await api("/api/submissions?problem_id=" + problemId + "&limit=20");
    if (state.selected?.id === problemId) renderHistory(data.items);
  } catch {
    if (state.selected?.id === problemId) renderHistory([]);
  }
}

function renderSubmission(submission) {
  const card = $("#submission-card");
  card.classList.remove("is-hidden");
  const isDone = submission.status === "COMPLETED";
  const isGood = submission.verdict === "ACCEPTED";
  $("#submission-verdict").textContent = verdictLabels[submission.verdict] || submission.verdict;
  $("#submission-status").textContent = isDone
    ? submission.score + " 分"
    : submission.status === "RUNNING" ? "判题中" : "排队中";
  $("#submission-status").className = "status-badge" + (isGood ? " good" : isDone ? " bad" : "");
  $("#submission-message").textContent = submission.error_message ||
    (isDone ? "所有测试点已完成。" : "代码正在编译和运行，请稍候。");
  $("#submission-progress").style.width = isDone ? "100%" : submission.status === "RUNNING" ? "62%" : "26%";
  const wrap = $("#result-table-wrap");
  wrap.replaceChildren();
  if (!submission.results || !submission.results.length) return;
  const table = document.createElement("table");
  table.className = "result-table";
  const head = document.createElement("thead");
  const headRow = document.createElement("tr");
  ["测试点", "结果", "耗时", "内存", "通信量"].forEach((label) => {
    const cell = document.createElement("th");
    cell.textContent = label;
    headRow.append(cell);
  });
  head.append(headRow);
  const body = document.createElement("tbody");
  for (const result of submission.results) {
    const row = document.createElement("tr");
    const name = document.createElement("td");
    name.textContent = result.test_case_name;
    const verdict = document.createElement("td");
    verdict.className = result.verdict === "ACCEPTED" ? "verdict-good" : "verdict-bad";
    verdict.textContent = verdictLabels[result.verdict] || result.verdict;
    const time = document.createElement("td");
    time.textContent = result.runtime_ms == null ? "-" : result.runtime_ms + " ms";
    const memory=document.createElement('td');memory.textContent=result.memory_kb==null?'—':result.memory_kb+' KiB';
    const message=document.createElement('td');message.textContent=result.message_bytes==null?'—':result.message_bytes+' B';
    row.append(name, verdict, time, memory, message);
    body.append(row);
  }
  table.append(head, body);
  wrap.append(table);
}

async function loadSubmission(id) {
  try {
    const submission = await api("/api/submissions/" + encodeURIComponent(id));
    showProblemTab("editor");
    renderSubmission(submission);
    if (submission.status !== "COMPLETED") pollSubmission(id);
  } catch (error) {
    showToast(error.message);
  }
}

function pollSubmission(id) {
  clearInterval(state.pollTimer);
  state.pollTimer = setInterval(async () => {
    try {
      const submission = await api("/api/submissions/" + encodeURIComponent(id));
      renderSubmission(submission);
      if (submission.status === "COMPLETED") {
        clearInterval(state.pollTimer);
        if (state.selected) loadHistory(state.selected.id);
        loadStats();
      }
    } catch (error) {
      clearInterval(state.pollTimer);
      showToast(error.message);
    }
  }, 1200);
}

async function submitCode() {
  if (!state.selected) return;
  if (!state.judgeReady) {
    showToast("评测机尚未就绪，请检查服务状态");
    return;
  }
  const source = $("#code-editor").value;
  if (!source.trim()) {
    showToast("请先写入代码");
    return;
  }
  const button = $("#submit-button");
  button.disabled = true;
  button.querySelector("span").textContent = "提交中…";
  try {
    const submission = await api("/api/submissions", {
      method: "POST",
      body: JSON.stringify({
        problem_id: state.selected.id,
        language: $("#language-select").value,
        source_code: source,
      }),
    });
    renderSubmission(submission);
    pollSubmission(submission.id);
    showToast("提交成功，判题任务已排队");
  } catch (error) {
    showToast(error.message);
  } finally {
    button.disabled = !state.judgeReady;
    button.querySelector("span").textContent = "提交判题";
  }
}

async function loadStats() {
  try {
    const stats = await api("/api/stats");
    $("#service-label").textContent = stats.problem_count + " 道题目在线";
    try {
      const health = await api("/health");
      state.authRequired = Boolean(health.auth_required);
      renderAccount();
    } catch {
      // Keep the local development default when health metadata is unavailable.
    }
  } catch {
    $("#service-label").textContent = "服务检查失败";
    $(".state-dot").style.background = "#e06b76";
  }
}

async function loadLanguages() {
  try {
    state.languages = await api("/api/languages");
    const select = $("#language-select");
    const current = select.value || "cpp";
    select.replaceChildren();
    for (const language of state.languages) {
      const option = document.createElement("option");
      option.value = language.id;
      option.textContent = language.label + (language.available ? "" : "（未启用）");
      option.disabled = !language.available;
      select.append(option);
    }
    const availableLanguages = state.languages.filter((item) => item.available);
    state.judgeReady = availableLanguages.length > 0;
    $("#submit-button").disabled = !state.judgeReady;
    if (!state.judgeReady && state.languages.length) {
      $("#service-label").textContent = "判题环境未就绪";
      $(".state-dot").style.background = "#e06b76";
    }
    const preferred = state.languages.find((item) => item.id === current && item.available)
      || availableLanguages[0];
    if (preferred) select.value = preferred.id;
  } catch {
    // The server still validates the language; keep the static fallback option.
  }
}

async function loadProblems() {
  const load = ++state.problemLoad;
  const params = new URLSearchParams({ page: String(state.page), page_size: String(state.pageSize) });
  if (state.search) params.set("search", state.search);
  if (state.difficulty) params.set("difficulty", state.difficulty);
  $("#library-feedback").textContent = "";
  try {
    const data = await api("/api/problems?" + params.toString());
    if (load !== state.problemLoad) return;
    state.totalProblems = data.total;
    const lastPage = Math.max(1, Math.ceil(data.total / state.pageSize));
    if (state.page > lastPage) { state.page = lastPage; return loadProblems(); }
    state.problems = data.items;
    renderProblemList();
  } catch (error) {
    if (load !== state.problemLoad) return;
    $("#library-feedback").textContent = error.message;
    tableMessage($("#problem-list"), "题库加载失败，请点击刷新重试。", 7);
  }
}

async function showSubmissions() {
  if (state.authRequired && !state.user) { showView("library"); openAuthDialog("login"); return; }
  showView("submissions");
  const rows = $("#submissions-rows");
  tableMessage(rows, "正在加载提交记录…", 7);
  try {
    const result = await api("/api/submissions?limit=100");
    $("#submissions-summary").textContent = `共 ${result.total} 条记录，显示最近 ${result.items.length} 条`;
    rows.replaceChildren();
    for (const item of result.items) {
      const row = document.createElement("tr");
      const title = state.problems.find(p => p.id === item.problem_id)?.title || item.problem_slug;
      row.append(bankElement("td", item.id.slice(0, 10), "bank-code"), bankElement("td", title, "table-title"),
        bankElement("td", state.languages.find(language => language.id === item.language)?.label || item.language),
        bankElement("td", verdictLabels[item.verdict] || item.verdict, item.verdict === "ACCEPTED" ? "listed-status" : ""),
        bankElement("td", item.score), bankElement("td", formatDate(item.created_at)));
      const actions = bankElement("td", ""), link = bankElement("a", "查看", "text-link");
      link.href = "#submission/" + encodeURIComponent(item.id); actions.append(link); row.append(actions); rows.append(row);
    }
    if (!result.items.length) tableMessage(rows, "还没有提交记录。", 7);
  } catch (error) { tableMessage(rows, error.message, 7); }
}

async function selectProblem(slug, refresh = true) {
  if (refresh) history.pushState(null, "", "#problem/" + encodeURIComponent(slug));
  showView("detail");
  const load = ++state.detailLoad;
  $("#problem-view").classList.add("is-hidden");
  $("#empty-state").classList.remove("is-hidden");
  $("#empty-state h2").textContent = "正在加载题目";
  $("#empty-state p:last-child").textContent = "请稍候…";
  try {
    const problem = await api("/api/problems/" + encodeURIComponent(slug));
    if (load !== state.detailLoad || state.view !== "detail") return false;
    renderProblem(problem);
    return true;
  } catch (error) {
    if (load !== state.detailLoad || state.view !== "detail") return false;
    $("#empty-state h2").textContent = "无法打开题目";
    $("#empty-state p:last-child").textContent = error.message;
    return false;
  }
}

function updateEditorSize() {
  $("#editor-size").textContent = formatBytes(new TextEncoder().encode($("#code-editor").value).length);
}

function bindEvents() {
  $("#login-button").addEventListener("click", () => openAuthDialog("login"));
  $("#register-button").addEventListener("click", () => openAuthDialog("register"));
  $("#logout-button").addEventListener("click", logout);
  $("#close-auth").addEventListener("click", closeAuthDialog);
  $("#auth-form").addEventListener("submit", submitAuth);
  $$(".auth-switch-button").forEach((button) => {
    button.addEventListener("click", () => setAuthMode(button.dataset.authMode));
  });
  $("#close-users").addEventListener("click", closeUsersDialog);
  $("#user-create-form").addEventListener("submit", createManagedUser);
  $("#open-problem-add").addEventListener("click", async () => {
    $("#bank-add-feedback").textContent = "";
    $("#problem-add-dialog").showModal();
    await loadProblemBank();
    $("#bank-code").focus();
  });
  $("#close-problem-add").addEventListener("click", () => $("#problem-add-dialog").close());
  $("#bank-status").addEventListener("change", renderProblemBank);
  $("#bank-select").addEventListener("change", (event) => { $("#bank-code").value = event.target.value; });
  $("#bank-search").addEventListener("input", () => { clearTimeout(state.bankSearchTimer); state.bankSearchTimer = setTimeout(loadProblemBank, 200); });
  $("#problem-bank-form").addEventListener("submit", (event) => { event.preventDefault(); addBankProblem($("#bank-code").value, $("#bank-add-button")); });
  $("#search-input").addEventListener("input", (event) => {
    state.search = event.target.value.trim();
    state.page = 1;
    clearTimeout(state.searchTimer);
    state.searchTimer = setTimeout(loadProblems, 220);
  });
  $("#refresh-button").addEventListener("click", () => {
    loadStats();
    loadProblems();
  });
  $("#previous-page").addEventListener("click", () => { if (state.page > 1) { --state.page; loadProblems(); } });
  $("#next-page").addEventListener("click", () => { if (state.page * state.pageSize < state.totalProblems) { ++state.page; loadProblems(); } });
  $$(".filter-chip").forEach((button) => button.addEventListener("click", () => {
    $$(".filter-chip").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.difficulty = button.dataset.difficulty || "";
    state.page = 1;
    loadProblems();
  }));
  const tabs = $$("#problem-view .tab");
  tabs.forEach((button, index) => {
    button.addEventListener("click", () => showProblemTab(button.dataset.tab));
    button.addEventListener("keydown", event => {
      const next = {ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1}[event.key];
      if (next === undefined) return;
      event.preventDefault();
      showProblemTab(tabs[next].dataset.tab);
      tabs[next].focus();
    });
  });
  $("#open-editor").addEventListener("click", () => showProblemTab("editor", true));
  $("#view-history").addEventListener("click", () => showProblemTab("history"));
  $("#submit-button").addEventListener("click", submitCode);
  $("#code-editor").addEventListener("input", updateEditorSize);
  $("#open-code-template").addEventListener("click", openCodeTemplate);
  $("#close-code-template").addEventListener("click", closeCodeTemplate);
  $("#cancel-code-template").addEventListener("click", closeCodeTemplate);
  $("#code-template-dialog").addEventListener("cancel", event => { event.preventDefault(); closeCodeTemplate(); });
  $("#code-template-form").addEventListener("submit", saveCodeTemplate);
  $("#copy-editor-template").addEventListener("click", () => {
    $("#template-code").value = $("#code-editor").value;
    $("#template-code").focus();
  });
  $("#clear-code-template").addEventListener("click", () => {
    $("#template-code").value = "";
    $("#template-code").focus();
  });
  $("#language-select").addEventListener("change", () => {
    rememberEditor();
    loadEditor($("#language-select").value);
  });
  $("#code-editor").addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      submitCode();
    }
  });
}

async function bootstrap() {
  bindEvents();
  await loadMe();
  await loadStats();
  await loadLanguages();
  await loadProblems();
  if (canManageProblems()) await loadProblemBank();
  await followHash();
}

async function followHash() {
  const hash=location.hash.slice(1);
  if(hash.startsWith('problem/'))return selectProblem(decodeURIComponent(hash.slice(8)),false);
  if(hash.startsWith('problem-'))return selectProblem(decodeURIComponent(hash.slice(8)),false);
  if(hash==='manage-problems')return openProblemBank();
  if(hash==='submissions')return showSubmissions();
  if(hash.startsWith('submission/')){
    if(state.authRequired&&!state.user){openAuthDialog('login');return;}
    const submission=await api('/api/submissions/'+encodeURIComponent(hash.slice(11)));
    if (!await selectProblem(submission.problem_slug,false)) return;
    showProblemTab("editor");
    renderSubmission(submission);
    if(submission.status!=='COMPLETED')pollSubmission(submission.id);
    return;
  }
  showView('library');
  if(hash==='login')openAuthDialog('login');
}

window.addEventListener("load", () => {
  if (state.selected) typesetMath($("#statement-panel"));
});

window.addEventListener('hashchange',()=>followHash().catch(error=>showToast(error.message)));

bootstrap().catch(error=>showToast(error.message));
