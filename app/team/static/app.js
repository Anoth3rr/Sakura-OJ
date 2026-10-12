const state = {
  view: "overview",
  overview: null,
  members: [],
  contests: [],
  submissions: [],
  memberStatus: "",
  memberSearch: "",
  ratingMember: "",
  ratingPlatform: "all",
  contestPlatform: "",
  submissionVerdict: "",
  submissionMember: "",
  editingMemberId: null,
  profileMemberId: null,
  toastTimer: null,
  loading: false,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const platformLabels = { codeforces: "Codeforces", atcoder: "AtCoder", nowcoder: "NowCoder", manual: "训练赛", oj: "Sakura OJ" };
const verdictLabels = { ACCEPTED: "Accepted", AC: "Accepted", WRONG_ANSWER: "Wrong Answer", PRESENTATION_ERROR: "Presentation Error", TIME_LIMIT_EXCEEDED: "Time Limit", MEMORY_LIMIT_EXCEEDED: "Memory Limit", OUTPUT_LIMIT_EXCEEDED: "Output Limit", COMMUNICATION_LIMIT_EXCEEDED: "Communication Limit", COMPILE_ERROR: "Compile Error", RUNTIME_ERROR: "Runtime Error", SYSTEM_ERROR: "System Error", PENDING: "Pending" };
const pageLabels = { overview: ["总览", "训练队状态"], members: ["队员", "队员档案"], ratings: ["Rating 曲线", "跨平台拟合"], contests: ["比赛复盘", "比赛结果"], submissions: ["提交分析", "提交情报"] };

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("zh-CN");
}

function formatDate(value, short = false) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value).slice(0, short ? 10 : 16);
  return date.toLocaleDateString("zh-CN", short ? { month: "2-digit", day: "2-digit" } : { month: "short", day: "numeric" });
}

function showToast(message, tone = "normal") {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.remove("is-hidden");
  toast.style.borderColor = tone === "error" ? "#f2b6b2" : "#bce4dd";
  toast.style.background = tone === "error" ? "#fff2f1" : "#effaf8";
  toast.style.color = tone === "error" ? "#b14e49" : "#17796e";
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => toast.classList.add("is-hidden"), 3200);
}

async function api(path, options = {}) {
  const request = { ...options, headers: { ...(options.headers || {}) } };
  if (request.body && typeof request.body !== "string") {
    request.headers["Content-Type"] = "application/json";
    request.body = JSON.stringify(request.body);
  }
  const response = await fetch(path, request);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail;
    const message = Array.isArray(detail) ? detail.map((item) => item?.msg || String(item)).join("；") : detail || "请求失败";
    throw new Error(message);
  }
  return body;
}

function openDialog(id) {
  const dialog = document.getElementById(id);
  if (typeof dialog.showModal === "function") dialog.showModal();
  else dialog.setAttribute("open", "");
}

function closeDialog(id) {
  const dialog = document.getElementById(id);
  if (typeof dialog.close === "function") dialog.close();
  else dialog.removeAttribute("open");
}

function switchView(view) {
  if (!pageLabels[view]) return;
  state.view = view;
  $$(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
  $$(".page").forEach((page) => page.classList.toggle("active", page.dataset.page === view));
  $("#crumb-root").textContent = pageLabels[view][0];
  $("#crumb-leaf").textContent = pageLabels[view][1];
  $("#sidebar").classList.remove("open");
  if (view === "members") renderMembers();
  if (view === "ratings") renderRatings();
  if (view === "contests") loadContests();
  if (view === "submissions") loadSubmissions();
}

function initialLetter(name) {
  return String(name || "?").trim().slice(0, 1) || "?";
}

function memberAvatar(member, mini = false) {
  return `<span class="${mini ? "mini-avatar" : "member-avatar"}" style="background:${escapeHtml(member.color || "#2dd4bf")}">${escapeHtml(initialLetter(member.name))}</span>`;
}

function renderMetrics(metrics) {
  const cards = [
    { label: "训练中队员", value: metrics.active_member_count, meta: `共 ${metrics.member_count} 人建档`, icon: "◎", cls: "" },
    { label: "队伍平均 rating", value: metrics.average_rating, meta: `${metrics.rating_delta >= 0 ? "+" : ""}${metrics.rating_delta} · 较周期起点`, icon: "↗", cls: "coral", delta: metrics.rating_delta },
    { label: "线上比赛场次", value: metrics.contest_count, meta: `${metrics.active_days} 个活跃训练日`, icon: "▣", cls: "amber" },
    { label: "提交通过率", value: `${metrics.acceptance_rate}%`, meta: `${formatNumber(metrics.accepted_count)} / ${formatNumber(metrics.submission_count)} 次 AC`, icon: "⌁", cls: "blue" },
  ];
  $("#metric-grid").innerHTML = cards.map((card) => {
    const displayValue = typeof card.value === "string" ? escapeHtml(card.value) : formatNumber(card.value);
    return `<article class="metric-card ${card.cls}"><div class="metric-label"><span>${card.label}</span><i class="metric-icon">${card.icon}</i></div><strong class="metric-value">${displayValue}</strong><small class="metric-meta ${card.delta > 0 ? "positive" : card.delta < 0 ? "negative" : ""}">${card.meta}</small></article>`;
  }).join("");
}

function lineChart(points, options = {}) {
  const width = 820;
  const height = options.height || 220;
  const pad = { top: 15, right: 18, bottom: 25, left: 38 };
  if (!points || points.length === 0) return `<div class="empty-table">暂无足够的比赛记录</div>`;
  const values = points.map((point) => Number(point.rating ?? point.fitted_rating ?? 0));
  const min = Math.floor((Math.min(...values) - 80) / 100) * 100;
  const max = Math.ceil((Math.max(...values) + 80) / 100) * 100;
  const x = (index) => pad.left + (points.length === 1 ? (width - pad.left - pad.right) / 2 : index / (points.length - 1) * (width - pad.left - pad.right));
  const y = (value) => height - pad.bottom - ((value - min) / Math.max(1, max - min)) * (height - pad.top - pad.bottom);
  const path = points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(Number(point.rating ?? point.fitted_rating ?? 0)).toFixed(1)}`).join(" ");
  const area = `${path} L ${x(points.length - 1).toFixed(1)},${height - pad.bottom} L ${x(0).toFixed(1)},${height - pad.bottom} Z`;
  const grids = Array.from({ length: 4 }, (_, index) => {
    const value = min + ((max - min) / 3) * index;
    const yy = y(value);
    return `<line x1="${pad.left}" y1="${yy}" x2="${width - pad.right}" y2="${yy}" stroke="#e8edef" stroke-width="1"/><text x="${pad.left - 9}" y="${yy + 3}" fill="#a2adb7" font-size="10" text-anchor="end">${Math.round(value)}</text>`;
  }).join("");
  const labels = points.map((point, index) => index === 0 || index === points.length - 1 || index === Math.floor(points.length / 2) ? `<text x="${x(index)}" y="${height - 5}" fill="#a2adb7" font-size="9" text-anchor="middle">${escapeHtml(formatDate(point.date, true))}</text>` : "").join("");
  const dots = points.map((point, index) => `<circle cx="${x(index)}" cy="${y(Number(point.rating ?? point.fitted_rating ?? 0))}" r="${index === points.length - 1 ? 4 : 2.5}" fill="${options.color || "#1aa795"}" stroke="#fff" stroke-width="${index === points.length - 1 ? 2 : 1}"/>`).join("");
  return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="rating 趋势图" preserveAspectRatio="none"><g>${grids}</g><path d="${area}" fill="#e9f7f4" opacity=".75"></path><path d="${path}" fill="none" stroke="${options.color || "#1aa795"}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>${dots}${labels}</svg>`;
}

function renderOverviewChart() {
  const trend = state.overview?.trend || [];
  const range = $("#trend-range")?.value || "all";
  const points = range === "all" ? trend : trend.filter((point) => Date.now() - new Date(point.date).getTime() <= Number(range) * 86400000);
  $("#overview-chart").innerHTML = lineChart(points, { height: 220 });
  if (!points.length) return;
  const start = Number(points[0].rating || 0);
  const end = Number(points[points.length - 1].rating || 0);
  $("#trend-start").textContent = formatNumber(start);
  $("#trend-end").textContent = formatNumber(end);
  $("#trend-change").textContent = `${end - start >= 0 ? "+" : ""}${formatNumber(end - start)}`;
}

function renderInsights(items) {
  const marks = { mint: "✦", amber: "↗", coral: "!" };
  $("#insight-list").innerHTML = (items || []).map((item) => `<div class="insight-item ${escapeHtml(item.tone || "mint")}"><span class="insight-mark">${marks[item.tone] || "•"}</span><div><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.text)}</small></div><b class="insight-value">${escapeHtml(item.value)}</b></div>`).join("");
}

function renderPlatforms(items) {
  const max = Math.max(...(items || []).map((item) => Number(item.average || 0)), 1);
  $("#platform-list").innerHTML = (items || []).map((item) => `<div class="platform-row"><div class="platform-name"><i class="platform-dot" style="background:${escapeHtml(item.color)}"></i>${escapeHtml(item.label)}</div><div class="platform-track"><span style="width:${Math.max(4, Number(item.average || 0) / max * 100)}%;background:${escapeHtml(item.color)}"></span></div><div class="platform-score"><b>${formatNumber(item.average)}</b><small>${item.change >= 0 ? "+" : ""}${formatNumber(item.change)}</small></div></div>`).join("");
}

function renderLeaderboard(items) {
  $("#leaderboard").innerHTML = (items || []).slice(0, 6).map((member, index) => `<div class="leader-row"><span class="leader-rank ${index < 3 ? "top" : ""}">${String(index + 1).padStart(2, "0")}</span><div class="leader-person">${memberAvatar(member, true)}<div><strong>${escapeHtml(member.name)}</strong><small>${escapeHtml(member.team_group)}</small></div></div><b class="leader-rating">${formatNumber(member.fitted_rating || member.current_rating)}</b><span class="leader-delta ${Number(member.rating_change || 0) < 0 ? "down" : ""}">${Number(member.rating_change || 0) >= 0 ? "+" : ""}${member.rating_change || 0}</span></div>`).join("");
}

function renderActivity(items) {
  $("#activity-list").innerHTML = (items || []).slice(0, 4).map((item) => {
    const good = ["ACCEPTED", "AC"].includes(item.verdict);
    return `<div class="activity-item"><div class="activity-top"><i class="verdict-dot ${good ? "" : "bad"}"></i><strong>${escapeHtml(item.member_name || "未归属")}</strong><time>${escapeHtml(formatDate(item.submitted_at, true))}</time></div><p>${escapeHtml(item.problem_name || item.problem_id || "未命名题目")} · ${escapeHtml(verdictLabels[item.verdict] || item.verdict)}</p></div>`;
  }).join("");
}

function renderOverview() {
  if (!state.overview) return;
  renderMetrics(state.overview.metrics);
  renderOverviewChart();
  renderInsights(state.overview.insights);
  renderPlatforms(state.overview.platforms);
  renderLeaderboard(state.overview.leaderboard);
  renderActivity(state.overview.recent_submissions);
  const syncs = state.overview.syncs || [];
  if (syncs.length) $("#last-sync").textContent = `最近同步 · ${formatDate(syncs[0].finished_at || syncs[0].started_at)}`;
}

function statusLabel(status) { return { active: "训练中", paused: "暂休", graduated: "毕业" }[status] || status || "—"; }

function renderMembers() {
  const filtered = state.members.filter((member) => {
    const matchesStatus = !state.memberStatus || member.status === state.memberStatus;
    const needle = state.memberSearch.toLowerCase();
    const matchesSearch = !needle || [member.name, member.student_id, member.cf_handle, member.atcoder_handle, member.nowcoder_handle, member.nowcoder_uid].some((value) => String(value || "").toLowerCase().includes(needle));
    return matchesStatus && matchesSearch;
  });
  $("#member-total").textContent = filtered.length;
  if (!filtered.length) {
    $("#member-table").innerHTML = `<div class="empty-table">没有匹配的队员</div>`;
    return;
  }
  $("#member-table").innerHTML = `<table class="data-table"><thead><tr><th>队员</th><th>训练组</th><th>综合 rating</th><th>平台快照</th><th>状态</th><th>操作</th></tr></thead><tbody>${filtered.map((member) => {
    const ratings = member.ratings || {};
    const fitted = member.fitted_rating || member.current_rating;
    return `<tr data-member-id="${member.id}"><td><div class="member-cell">${memberAvatar(member)}<div><strong>${escapeHtml(member.name)}</strong><small>${escapeHtml(member.student_id || "未填写学号")}</small></div></div></td><td><span class="group-pill">${escapeHtml(member.team_group)}</span></td><td><div class="rating-cell"><strong>${formatNumber(fitted)}</strong><small>${member.rating_change >= 0 ? "+" : ""}${member.rating_change || 0} 本周期</small></div></td><td><div class="rating-chips">${["codeforces", "atcoder", "nowcoder"].map((platform) => ratings[platform] ? `<span class="rating-chip">${platform === "codeforces" ? "CF" : platform === "atcoder" ? "AC" : "NC"} <b>${ratings[platform].rating}</b></span>` : "").join("")}</div></td><td><span class="status-pill ${escapeHtml(member.status)}">${statusLabel(member.status)}</span></td><td><button class="row-action" data-open-profile="${member.id}">查看画像 →</button></td></tr>`;
  }).join("")}</tbody></table>`;
}

function populateMemberSelects() {
  const options = state.members.map((member) => `<option value="${member.id}">${escapeHtml(member.name)}</option>`).join("");
  const ratingSelect = $("#rating-member-select");
  const submissionSelect = $("#submission-member-select");
  if (ratingSelect) ratingSelect.innerHTML = `<option value="">全队均值</option>${options}`;
  if (submissionSelect) submissionSelect.innerHTML = `<option value="">全队提交</option>${options}`;
  if (ratingSelect) ratingSelect.value = state.ratingMember;
  if (submissionSelect) submissionSelect.value = state.submissionMember;
  const ratingFormSelect = $("#rating-form-member");
  if (ratingFormSelect) ratingFormSelect.innerHTML = options;
  const ojFormSelect = $("#oj-form-member");
  if (ojFormSelect) ojFormSelect.innerHTML = `<option value="">不指定（仅做队伍汇总）</option>${options}`;
}

async function renderRatings() {
  populateMemberSelects();
  const query = new URLSearchParams();
  if (state.ratingMember) query.set("member_id", state.ratingMember);
  if (state.ratingPlatform !== "all") query.set("platform", state.ratingPlatform);
  try {
    const data = await api(`/api/team/ratings/trend?${query.toString()}`);
    const series = data.series || [];
    $("#rating-chart").innerHTML = lineChart(series, { height: 320, color: state.ratingPlatform === "atcoder" ? "#568ccf" : state.ratingPlatform === "codeforces" ? "#ef8b45" : "#1aa795" });
    $("#rating-chart-title").textContent = state.ratingMember ? `${state.members.find((item) => String(item.id) === String(state.ratingMember))?.name || "队员"} 的成长轨迹` : "全队成长轨迹";
    if (series.length) {
      const first = Number(series[0].rating ?? series[0].fitted_rating ?? 0);
      const last = Number(series[series.length - 1].rating ?? series[series.length - 1].fitted_rating ?? 0);
      $("#rating-chart-start").textContent = formatNumber(first);
      $("#rating-chart-current").textContent = formatNumber(last);
      $("#rating-chart-delta").textContent = `${last - first >= 0 ? "+" : ""}${formatNumber(last - first)}`;
    } else {
      ["#rating-chart-start", "#rating-chart-current", "#rating-chart-delta"].forEach((id) => $(id).textContent = "—");
    }
    renderRatingSnapshot();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function renderRatingSnapshot() {
  const selected = state.ratingMember ? state.members.filter((member) => String(member.id) === String(state.ratingMember)) : state.members;
  const platforms = ["codeforces", "atcoder", "nowcoder"];
  $("#rating-snapshot").innerHTML = `<div class="snapshot-grid">${platforms.map((platform) => {
    const values = selected.map((member) => member.ratings?.[platform]).filter(Boolean);
    const average = values.length ? Math.round(values.reduce((sum, item) => sum + Number(item.rating || 0), 0) / values.length) : 0;
    const change = values.reduce((sum, item) => sum + Number(item.rating_change || 0), 0);
    return `<div class="snapshot-item"><header><span>${platformLabels[platform]}</span><span>${values.length} 人</span></header><strong>${formatNumber(average)}</strong><small>${change >= 0 ? "+" : ""}${formatNumber(change)} · 合计增幅</small></div>`;
  }).join("")}</div>`;
}

async function loadContests() {
  try {
    const contestQuery = new URLSearchParams({ limit: "100" });
    if (state.contestPlatform) contestQuery.set("platform", state.contestPlatform);
    const data = await api(`/api/team/contests?${contestQuery.toString()}`);
    state.contests = data.items || [];
    const total = state.contests.length;
    const avg = total ? Math.round(state.contests.reduce((sum, item) => sum + Number(item.avg_performance || 0), 0) / total) : 0;
    const top = total ? Math.max(...state.contests.map((item) => Number(item.top_performance || 0))) : 0;
    $("#contest-summary").innerHTML = `<div class="summary-card"><span>已记录比赛</span><strong>${formatNumber(total)}</strong><small>来自三个平台与训练赛</small></div><div class="summary-card"><span>平均 performance</span><strong>${formatNumber(avg)}</strong><small>跨比赛结果均值</small></div><div class="summary-card"><span>单场峰值</span><strong>${formatNumber(top)}</strong><small>最强单场表现</small></div>`;
    if (!state.contests.length) {
      $("#contest-table").innerHTML = `<div class="empty-table">暂无比赛记录</div>`;
      return;
    }
    $("#contest-table").innerHTML = `<table class="data-table"><thead><tr><th>比赛</th><th>平台</th><th>时间</th><th>参赛人数</th><th>参与队员</th><th>平均表现</th><th>峰值</th></tr></thead><tbody>${state.contests.map((contest) => `<tr><td><div class="contest-name"><strong>${escapeHtml(contest.name)}</strong><small>${escapeHtml(contest.external_id)}</small></div></td><td><span class="platform-pill ${escapeHtml(contest.platform)}">${escapeHtml(platformLabels[contest.platform] || contest.platform)}</span></td><td>${escapeHtml(formatDate(contest.contest_time))}</td><td>${contest.participant_count ? formatNumber(contest.participant_count) : "—"}</td><td>${formatNumber(contest.result_count)}</td><td class="performance">${formatNumber(Math.round(contest.avg_performance || 0))}</td><td class="performance good">${formatNumber(Math.round(contest.top_performance || 0))}</td></tr>`).join("")}</tbody></table>`;
  } catch (error) {
    showToast(error.message, "error");
  }
}

function verdictClass(verdict) {
  if (["ACCEPTED", "AC"].includes(verdict)) return "ac";
  if (verdict === "WRONG_ANSWER") return "wa";
  if (verdict === "TIME_LIMIT_EXCEEDED") return "tle";
  if (verdict === "COMPILE_ERROR") return "ce";
  return "pending";
}

async function loadSubmissions() {
  const query = new URLSearchParams({ limit: "500" });
  if (state.submissionMember) query.set("member_id", state.submissionMember);
  if (state.submissionVerdict) query.set("verdict", state.submissionVerdict);
  try {
    const data = await api(`/api/team/submissions?${query.toString()}`);
    state.submissions = data.items || [];
    const allCount = state.submissions.length;
    const accepted = state.submissions.filter((item) => ["ACCEPTED", "AC"].includes(item.verdict)).length;
    const wa = state.submissions.filter((item) => item.verdict === "WRONG_ANSWER").length;
    const languages = new Set(state.submissions.map((item) => item.language).filter(Boolean)).size;
    $("#submission-kpis").innerHTML = `<div class="submission-kpi"><span>样本提交</span><strong>${formatNumber(allCount)}</strong><small>当前筛选范围</small></div><div class="submission-kpi"><span>AC 率</span><strong>${allCount ? (accepted / allCount * 100).toFixed(1) : "0.0"}%</strong><small>${formatNumber(accepted)} 次通过</small></div><div class="submission-kpi"><span>WA 占比</span><strong>${allCount ? (wa / allCount * 100).toFixed(1) : "0.0"}%</strong><small>${formatNumber(wa)} 次需要复盘</small></div><div class="submission-kpi"><span>使用语言</span><strong>${languages}</strong><small>不同工具链</small></div>`;
    const verdictCounts = {};
    const languageCounts = {};
    state.submissions.forEach((item) => {
      const verdict = item.verdict || "PENDING";
      const language = item.language || "未标注";
      verdictCounts[verdict] = (verdictCounts[verdict] || 0) + 1;
      languageCounts[language] = (languageCounts[language] || 0) + 1;
    });
    const verdictOrder = Object.keys(verdictLabels);
    const verdictRows = verdictOrder.filter((key) => verdictCounts[key]).map((key) => {
      const color = key === "ACCEPTED" ? "#1aa795" : key === "WRONG_ANSWER" || key === "RUNTIME_ERROR" ? "#ed706b" : "#d89522";
      return `<div class="breakdown-row"><span>${escapeHtml(verdictLabels[key] || key)}</span><div class="breakdown-track"><span style="width:${verdictCounts[key] / Math.max(allCount, 1) * 100}%;background:${color}"></span></div><strong>${verdictCounts[key]}</strong></div>`;
    });
    const languageRows = Object.entries(languageCounts).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([key, count]) => `<div class="breakdown-row"><span>${escapeHtml(key)}</span><div class="breakdown-track"><span style="width:${count / Math.max(allCount, 1) * 100}%"></span></div><strong>${count}</strong></div>`);
    $("#verdict-breakdown").innerHTML = verdictRows.join("") || `<div class="empty-table">暂无结果</div>`;
    $("#language-breakdown").innerHTML = languageRows.join("") || `<div class="empty-table">暂无语言数据</div>`;
    if (!state.submissions.length) {
      $("#submission-table").innerHTML = `<div class="empty-table">暂无提交记录</div>`;
      return;
    }
    $("#submission-table").innerHTML = `<table class="data-table"><thead><tr><th>队员</th><th>题目</th><th>结果</th><th>语言</th><th>运行时间</th><th>提交时间</th><th>来源</th></tr></thead><tbody>${state.submissions.map((item) => `<tr><td>${escapeHtml(item.member_name || "未归属")}</td><td><div class="contest-name"><strong>${escapeHtml(item.problem_name || item.problem_id || "未命名题目")}</strong><small>${escapeHtml(item.problem_id || "")}</small></div></td><td><span class="submission-verdict ${verdictClass(item.verdict)}"><i class="verdict-dot ${["ACCEPTED", "AC"].includes(item.verdict) ? "" : "bad"}"></i>${escapeHtml(verdictLabels[item.verdict] || item.verdict)}</span></td><td>${escapeHtml(item.language || "—")}</td><td>${item.runtime_ms == null ? "—" : `${item.runtime_ms} ms`}</td><td>${escapeHtml(formatDate(item.submitted_at))}</td><td><span class="platform-pill ${escapeHtml(item.platform)}">${escapeHtml(platformLabels[item.platform] || item.platform)}</span></td></tr>`).join("")}</tbody></table>`;
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function loadAll() {
  state.loading = true;
  $("#today-label").textContent = new Date().toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric", weekday: "long" });
  try {
    const [overview, members] = await Promise.all([api("/api/team/overview"), api("/api/team/members")]);
    state.overview = overview;
    state.members = members.items || [];
    renderOverview();
    populateMemberSelects();
    if (state.view === "members") renderMembers();
    if (state.view === "ratings") await renderRatings();
    if (state.view === "contests") await loadContests();
    if (state.view === "submissions") await loadSubmissions();
    const integration = await api("/api/team/integrations/status").catch(() => null);
    if (integration) {
      $("#oj-state").textContent = integration.oj_database_exists ? "LOCAL" : "OFFLINE";
      const ojLink = $("#open-oj-button");
      if (ojLink) ojLink.href = integration.oj_base_url || "/";
      if (integration.latest_sync) $("#last-sync").textContent = `最近同步 · ${formatDate(integration.latest_sync.finished_at || integration.latest_sync.started_at)}`;
    }
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    state.loading = false;
  }
}

async function openProfile(memberId) {
  try {
    const member = await api(`/api/team/members/${memberId}`);
    state.profileMemberId = String(memberId);
    const profile = member.profile || {};
    const nc = member.ratings?.nowcoder;
    const nowcoderAccount = member.nowcoder_uid ? `<div class="profile-account"><div><span>牛客 UID · <a href="https://ac.nowcoder.com/acm/contest/profile/${encodeURIComponent(member.nowcoder_uid)}" target="_blank" rel="noopener noreferrer">${escapeHtml(member.nowcoder_uid)}</a>${member.nowcoder_handle ? ` · ${escapeHtml(member.nowcoder_handle)}` : ""}</span><p>${nc ? `Rating <b>${nc.rating}</b> · 峰值 ${nc.peak_rating} · ${nc.contest_count} 场 Rating 赛 · 最近 ${nc.rating_change >= 0 ? "+" : ""}${nc.rating_change}` : "尚未同步牛客 Rating"}</p></div><button class="secondary-btn" type="button" data-sync-nowcoder="${member.id}">同步牛客 Rating</button></div>` : "";
    const history = (member.rating_history || []).slice(-12);
    $("#profile-content").innerHTML = `<div class="profile-hero">${memberAvatar(member)}<div><h2 id="profile-title">${escapeHtml(member.name)}</h2><p>${escapeHtml(member.student_id || "未填写学号")} · ${escapeHtml(member.team_group)}</p></div><div class="profile-score"><strong>${formatNumber(profile.current_rating)}</strong><small>${escapeHtml(profile.headline || "持续训练")}</small></div></div><div class="profile-body">${nowcoderAccount}<div class="profile-tags">${(profile.tags || []).map((tag) => `<span class="profile-tag">${escapeHtml(tag)}</span>`).join("")}</div><div class="profile-stats"><div class="profile-stat"><span>峰值 rating</span><strong>${formatNumber(profile.peak_rating)}</strong></div><div class="profile-stat"><span>比赛场次</span><strong>${formatNumber(profile.contest_count)}</strong></div><div class="profile-stat"><span>AC 率</span><strong>${profile.acceptance_rate}%</strong></div><div class="profile-stat"><span>稳定度</span><strong>${profile.consistency}%</strong></div></div><h3 class="profile-section-title">个人拟合曲线</h3><div class="profile-mini-chart">${lineChart(history, { height: 125, color: member.color || "#1aa795" })}</div><p class="method-intro">${escapeHtml(profile.summary || "")}</p><div class="modal-actions"><button class="secondary-btn" type="button" data-edit-member="${member.id}">编辑档案</button></div></div>`;
    if (!$("#profile-dialog").open) openDialog("profile-dialog");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function submitMember(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const feedback = $("#member-form-feedback");
  feedback.textContent = "";
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const editing = state.editingMemberId;
    await api(editing ? `/api/team/members/${editing}` : "/api/team/members", { method: editing ? "PATCH" : "POST", body: payload });
    closeDialog("member-dialog");
    form.reset();
    state.editingMemberId = null;
    $("#member-dialog-title").textContent = "添加队员";
    showToast(editing ? "队员档案已更新" : "队员档案已创建");
    await loadAll();
  } catch (error) {
    feedback.textContent = error.message;
  }
}

async function openMemberEditor(memberId) {
  try {
    const member = await api(`/api/team/members/${memberId}`);
    const form = $("#member-form");
    for (const name of ["name", "student_id", "team_group", "status", "color", "cf_handle", "atcoder_handle", "nowcoder_handle", "nowcoder_uid", "oj_username", "note"]) {
      if (form.elements[name]) form.elements[name].value = member[name] ?? "";
    }
    state.editingMemberId = memberId;
    $("#member-dialog-title").textContent = "编辑队员档案";
    closeDialog("profile-dialog");
    openDialog("member-dialog");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function submitContest(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const feedback = $("#contest-form-feedback");
  feedback.textContent = "";
  const data = Object.fromEntries(new FormData(form).entries());
  let results;
  try {
    results = JSON.parse(data.results_json);
    if (!Array.isArray(results)) throw new Error("结果 JSON 必须是数组");
  } catch (error) {
    feedback.textContent = `结果 JSON 无法解析：${error.message}`;
    return;
  }
  const contestTime = data.contest_time ? new Date(data.contest_time).toISOString() : new Date().toISOString();
  try {
    await api("/api/team/contests/import", { method: "POST", body: { platform: data.platform, external_id: data.external_id, name: data.name, contest_time: contestTime, participant_count: Number(data.participant_count || 0), results } });
    closeDialog("contest-dialog");
    form.reset();
    showToast("比赛已导入，拟合曲线已更新");
    await loadAll();
  } catch (error) {
    feedback.textContent = error.message;
  }
}

async function submitRating(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const feedback = $("#rating-form-feedback");
  feedback.textContent = "";
  const data = Object.fromEntries(new FormData(form).entries());
  try {
    await api("/api/team/ratings/import", {
      method: "POST",
      body: {
        member_id: Number(data.member_id),
        platform: data.platform,
        rating: Number(data.rating),
        peak_rating: data.peak_rating ? Number(data.peak_rating) : null,
        rank_title: data.rank_title || "",
        contest_count: Number(data.contest_count || 0),
        rating_change: Number(data.rating_change || 0),
      },
    });
    closeDialog("rating-dialog");
    form.reset();
    showToast("平台 rating 已保存");
    await loadAll();
  } catch (error) {
    feedback.textContent = error.message;
  }
}

async function syncAndRefresh(path, body, scope, button, memberId = null) {
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "同步中…";
  try {
    const before = await api("/api/team/integrations/status");
    const lastId = Math.max(0, ...(before.syncs || []).map((item) => item.id));
    await api(path, { method: "POST", body });
    showToast("正在获取平台数据，完成后自动更新");
    for (let attempt = 0; attempt < 40; attempt += 1) {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      const status = await api("/api/team/integrations/status");
      const completed = (status.syncs || []).find((item) => item.id > lastId && item.scope === scope);
      if (!completed) continue;
      await loadAll();
      if (memberId && $("#profile-dialog").open && state.profileMemberId === String(memberId)) await openProfile(memberId);
      showToast(completed.message, completed.status === "success" ? "normal" : "error");
      return;
    }
    showToast("同步仍在后台进行，可稍后点击刷新查看结果");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
}

async function syncPlatforms() {
  await syncAndRefresh("/api/team/sync/all", { platforms: ["codeforces", "atcoder", "nowcoder"] }, "all", $("#sync-button"));
}

async function submitOJ(event) {
  event.preventDefault();
  const memberId = $("#oj-form-member").value;
  const feedback = $("#oj-form-feedback");
  feedback.textContent = "";
  try {
    const result = await api("/api/team/integrations/oj/sync", { method: "POST", body: memberId ? { member_id: Number(memberId) } : {} });
    closeDialog("oj-dialog");
    showToast(`已从 Sakura OJ 导入 ${result.imported} 条提交`);
    await loadAll();
  } catch (error) {
    feedback.textContent = error.message;
  }
}

function bindEvents() {
  $$(".nav-item").forEach((button) => button.addEventListener("click", () => switchView(button.dataset.view)));
  $$('[data-view-jump]').forEach((button) => button.addEventListener("click", () => switchView(button.dataset.viewJump)));
  $("#mobile-menu").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
  $("#refresh-button").addEventListener("click", loadAll);
  $("#sync-button").addEventListener("click", syncPlatforms);
  $("#quick-add-member").addEventListener("click", () => { state.editingMemberId = null; $("#member-dialog-title").textContent = "添加队员"; openDialog("member-dialog"); });
  $("#add-member-button").addEventListener("click", () => { state.editingMemberId = null; $("#member-dialog-title").textContent = "添加队员"; openDialog("member-dialog"); });
  $("#oj-sync-button").addEventListener("click", () => { populateMemberSelects(); openDialog("oj-dialog"); });
  $("#import-contest-button").addEventListener("click", () => openDialog("contest-dialog"));
  $("#contest-platform-select").addEventListener("change", (event) => { state.contestPlatform = event.target.value; loadContests(); });
  $("#import-rating-button").addEventListener("click", () => { populateMemberSelects(); openDialog("rating-dialog"); });
  $("#export-button").addEventListener("click", () => window.open("/api/team/export?format=json", "_blank"));
  $("#submission-export-button").addEventListener("click", () => window.open("/api/team/export?format=csv", "_blank"));
  $("#trend-range").addEventListener("change", renderOverviewChart);
  $("#refresh-insights").addEventListener("click", () => { renderInsights(state.overview?.insights || []); showToast("观察已刷新"); });
  $("#recompute-button").addEventListener("click", async () => {
    try {
      const result = await api("/api/team/ratings/recompute", { method: "POST" });
      showToast(`已重新计算 ${result.updated_results} 条比赛结果`);
      await loadAll();
    } catch (error) {
      showToast(error.message, "error");
    }
  });
  $("#member-search").addEventListener("input", (event) => { state.memberSearch = event.target.value; renderMembers(); });
  $$("#member-status-tabs button").forEach((button) => button.addEventListener("click", () => { state.memberStatus = button.dataset.status; $$("#member-status-tabs button").forEach((item) => item.classList.toggle("active", item === button)); renderMembers(); }));
  $("#rating-member-select").addEventListener("change", (event) => { state.ratingMember = event.target.value; renderRatings(); });
  $$("#rating-platform-tabs button").forEach((button) => button.addEventListener("click", () => { state.ratingPlatform = button.dataset.platform; $$("#rating-platform-tabs button").forEach((item) => item.classList.toggle("active", item === button)); renderRatings(); }));
  $("#submission-member-select").addEventListener("change", (event) => { state.submissionMember = event.target.value; loadSubmissions(); });
  $$("#submission-verdict-tabs button").forEach((button) => button.addEventListener("click", () => { state.submissionVerdict = button.dataset.verdict; $$("#submission-verdict-tabs button").forEach((item) => item.classList.toggle("active", item === button)); loadSubmissions(); }));
  $("#member-form").addEventListener("submit", submitMember);
  $("#contest-form").addEventListener("submit", submitContest);
  $("#rating-form").addEventListener("submit", submitRating);
  $("#oj-form").addEventListener("submit", submitOJ);
  $$("[data-close-dialog]").forEach((button) => button.addEventListener("click", () => closeDialog(button.dataset.closeDialog)));
  $("#member-table").addEventListener("click", (event) => { const button = event.target.closest("[data-open-profile]"); if (button) openProfile(button.dataset.openProfile); });
  $("#profile-content").addEventListener("click", (event) => {
    const edit = event.target.closest("[data-edit-member]");
    if (edit) openMemberEditor(edit.dataset.editMember);
    const sync = event.target.closest("[data-sync-nowcoder]");
    if (sync) {
      const memberId = sync.dataset.syncNowcoder;
      syncAndRefresh(`/api/team/members/${memberId}/sync`, { platforms: ["nowcoder"] }, `member:${memberId}`, sync, memberId);
    }
  });
  $("#global-search").addEventListener("keydown", (event) => { if (event.key !== "Enter") return; const value = event.target.value.trim(); if (!value) return; state.memberSearch = value; switchView("members"); $("#member-search").value = value; renderMembers(); });
  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, textarea, select")) return;
    const view = { "1": "overview", "2": "members", "3": "ratings", "4": "contests", "5": "submissions" }[event.key];
    if (view) switchView(view);
  });
}

bindEvents();
loadAll();

fetch('/api/auth/me').then(r=>r.ok?r.json():null).then(user=>{
  const link=document.getElementById('studio-link');
  if(user && !['admin','problem_admin'].includes(user.role)) link.hidden=true;
  const chip=document.querySelector('.user-chip');
  if(user && chip) {chip.querySelector('strong').textContent=user.display_name;chip.querySelector('small').textContent=user.role_label;}
});
