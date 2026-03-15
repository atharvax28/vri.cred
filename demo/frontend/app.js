/**
 * VRI Credit Intelligence — Frontend Application
 * ────────────────────────────────────────────────
 * Connects to FastAPI backend (http://localhost:8000)
 * No build step — plain ES6 module.
 */

// Use relative path for API calls (works in development and production)
const API_BASE = typeof window !== 'undefined' && window.location.hostname === 'localhost' 
  ? "http://127.0.0.1:8000"
  : "/api";

// ── State ──
const state = {
  history: [],
  currentResult: null,
  currentReport: null,
  gstinList: [],
};

// ── DOM refs ──
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const dom = {
  // Header
  navBtns: () => $$(".nav-btn"),
  apiStatus: () => $("#api-status"),
  statusDot: () => $("#api-status .status-dot"),
  statusText: () => $("#api-status .status-text"),

  // Views
  views: () => $$(".view"),

  // Input step
  stepInput: () => $("#step-input"),
  stepResults: () => $("#step-results"),
  gstinInput: () => $("#gstin-input"),
  inputIcon: () => $("#input-icon"),
  gstinError: () => $("#gstin-error"),
  btnScore: () => $("#btn-score"),
  btnReport: () => $("#btn-report"),
  gstinChips: () => $("#gstin-chips"),

  // Results step
  btnBack: () => $("#btn-back"),
  resultTitle: () => $("#result-title"),
  resultSubtitle: () => $("#result-subtitle"),
  gaugeFill: () => $("#gauge-fill"),
  gaugeScore: () => $("#gauge-score"),
  riskGrade: () => $("#risk-grade"),
  pdValue: () => $("#pd-value"),
  modelVersion: () => $("#model-version"),
  shapFactors: () => $("#shap-factors"),
  btnGenReport: () => $("#btn-gen-report"),
  btnNewScore: () => $("#btn-new-score"),

  // Report
  reportSection: () => $("#report-section"),
  reportBadge: () => $("#report-badge"),
  reportBody: () => $("#report-body"),
  reportDisclaimer: () => $("#report-disclaimer"),
  resultActions: () => $("#result-actions"),

  // History
  historyGrid: () => $("#history-grid"),
  historyEmpty: () => $("#history-empty"),

  // Toast
  toastContainer: () => $("#toast-container"),
};

// ── GSTIN Validation ──
const GSTIN_REGEX = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]$/;

function validateGSTIN(raw) {
  const val = raw.toUpperCase().trim();
  if (val.length === 0) return { valid: false, error: "" };
  if (val.length < 15) return { valid: false, error: "GSTIN must be 15 characters" };
  if (val.length > 15) return { valid: false, error: "GSTIN too long" };
  if (!GSTIN_REGEX.test(val)) return { valid: false, error: "Invalid GSTIN format" };
  return { valid: true, error: "" };
}

// ── API Calls ──
async function apiCall(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error ${res.status}`);
  }
  return res.json();
}

async function checkHealth() {
  try {
    const data = await apiCall("/health");
    dom.statusDot().className = "status-dot status-dot--ok";
    dom.statusText().textContent = data.model_ready ? "Model ready" : "Degraded";
    return true;
  } catch {
    dom.statusDot().className = "status-dot status-dot--error";
    dom.statusText().textContent = "Offline";
    return false;
  }
}

async function fetchGSTINs() {
  try {
    const data = await apiCall("/v1/gstins");
    state.gstinList = data.gstins;
    renderGSTINChips(data.gstins);
  } catch {
    // non-critical
  }
}

async function scoreGSTIN(gstin) {
  return apiCall("/v1/score", {
    method: "POST",
    body: JSON.stringify({ gstin }),
  });
}

async function generateReport(gstin) {
  return apiCall("/v1/report", {
    method: "POST",
    body: JSON.stringify({ gstin }),
  });
}

// ── Risk / Grade helpers ──
const GRADE_PROFILES = {
  AAA: { cls: "good", label: "Prime" },
  AA: { cls: "good", label: "Excellent" },
  A: { cls: "good", label: "Good" },
  BBB: { cls: "mid", label: "Adequate" },
  BB: { cls: "mid", label: "Fair" },
  B: { cls: "bad", label: "Speculative" },
  CCC: { cls: "bad", label: "Vulnerable" },
  CC: { cls: "bad", label: "High Risk" },
  C: { cls: "bad", label: "Very High Risk" },
  D: { cls: "bad", label: "Default" },
};

function gradeInfo(grade) {
  return GRADE_PROFILES[grade] || { cls: "mid", label: grade };
}

function getScoreColor(score) {
  if (score >= 700) return "good";
  if (score >= 450) return "mid";
  return "bad";
}

// ── Rendering ──
function renderGSTINChips(gstins) {
  const container = dom.gstinChips();
  if (!container) return;

  // Map demo GSTINs to risk profiles for color coding
  const PROFILES = [
    { dot: "healthy" },
    { dot: "stressed" },
    { dot: "borderline" },
    { dot: "growing" },
    { dot: "suspended" },
  ];

  container.innerHTML = gstins
    .map((g, i) => {
      const profile = PROFILES[i % PROFILES.length];
      return `<button class="chip" data-gstin="${g}">
                <span class="chip__dot chip__dot--${profile.dot}"></span>
                ${g}
              </button>`;
    })
    .join("");

  container.querySelectorAll(".chip").forEach((chip) =>
    chip.addEventListener("click", () => {
      dom.gstinInput().value = chip.dataset.gstin;
      dom.gstinInput().dispatchEvent(new Event("input"));
    })
  );
}

function setGaugeValue(score, maxScore = 1000) {
  const circumference = 2 * Math.PI * 85; // r=85
  const pct = Math.min(score / maxScore, 1);
  const offset = circumference * (1 - pct);

  // Add SVG gradient if not present
  const svg = $(".gauge__svg");
  if (!svg.querySelector("#gaugeGrad")) {
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    const colorCls = getScoreColor(score);
    const colors =
      colorCls === "good"
        ? ["#34d399", "#38bdf8"]
        : colorCls === "mid"
        ? ["#fbbf24", "#fb923c"]
        : ["#f43f5e", "#e879f9"];

    defs.innerHTML = `<linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${colors[0]}"/>
      <stop offset="100%" stop-color="${colors[1]}"/>
    </linearGradient>`;
    svg.insertBefore(defs, svg.firstChild);
  }

  // Animate
  requestAnimationFrame(() => {
    dom.gaugeFill().style.strokeDashoffset = offset;
  });

  // Animate number
  animateScore(dom.gaugeScore(), 0, score, 1200);
}

function animateScore(el, from, to, duration) {
  const start = performance.now();
  function frame(now) {
    const elapsed = now - start;
    const t = Math.min(elapsed / duration, 1);
    // ease-out quad
    const eased = 1 - (1 - t) * (1 - t);
    el.textContent = Math.round(from + (to - from) * eased);
    if (t < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function renderScoringResult(data) {
  state.currentResult = data;

  // Title
  dom.resultTitle().textContent = data.trade_name || data.legal_name;
  dom.resultSubtitle().textContent = data.gstin;

  // Gauge
  const colorCls = getScoreColor(data.vri_score);
  dom.gaugeScore().className = `gauge__score color-${colorCls}`;
  setGaugeValue(data.vri_score);

  // Grade
  const gi = gradeInfo(data.risk_grade);
  dom.riskGrade().textContent = data.risk_grade;
  dom.riskGrade().className = `meta-value meta-value--grade bg-${gi.cls}`;

  // PD
  dom.pdValue().textContent = (data.probability_of_default * 100).toFixed(2) + "%";
  dom.pdValue().className = `meta-value color-${getScoreColor(1000 - data.probability_of_default * 1000)}`;

  // Model
  dom.modelVersion().textContent = data.model_version;

  // SHAP
  renderSHAPFactors(data.shap_factors || []);

  // Add to history
  addToHistory(data);
}

function renderSHAPFactors(factors) {
  const container = dom.shapFactors();
  if (!container) return;

  const sorted = [...factors].sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value));
  const maxAbs = Math.max(...sorted.map((f) => Math.abs(f.shap_value)), 0.01);

  container.innerHTML = sorted
    .map((f, i) => {
      const dir = f.direction === "positive" ? "positive" : "negative";
      const barPct = Math.round((Math.abs(f.shap_value) / maxAbs) * 100);
      return `<div class="shap-factor" style="animation-delay: ${i * 0.05}s">
                <span class="shap-factor__name">${escapeHTML(f.display_name)}</span>
                <div class="shap-factor__bar-wrap">
                  <div class="shap-factor__bar shap-factor__bar--${dir}" style="width: ${barPct}%"></div>
                </div>
                <span class="shap-factor__value shap-factor__value--${dir}">
                  ${f.shap_value >= 0 ? "+" : ""}${f.shap_value.toFixed(3)}
                </span>
              </div>`;
    })
    .join("");
}

function renderReport(data) {
  state.currentReport = data;

  const sections = [
    { key: "executive_summary", title: "Executive Summary", highlight: false },
    { key: "business_overview", title: "Business Overview", highlight: false },
    { key: "financial_analysis", title: "Financial Analysis", highlight: false },
    { key: "risk_factors", title: "Risk Factors", highlight: false },
    { key: "strengths", title: "Strengths", highlight: false },
    { key: "recommendation", title: "Recommendation", highlight: true },
  ];

  const body = dom.reportBody();
  body.innerHTML = sections
    .filter((s) => data[s.key])
    .map(
      (s, i) =>
        `<div class="report-block ${s.highlight ? "report-block--recommendation" : ""}" style="animation-delay: ${i * 0.08}s">
          <div class="report-block__title">${s.title}</div>
          <div class="report-block__text">${escapeHTML(data[s.key])}</div>
        </div>`
    )
    .join("");

  // Disclaimer
  if (data.disclaimer) {
    dom.reportDisclaimer().textContent = data.disclaimer;
    dom.reportDisclaimer().style.display = "block";
  }

  // Badge
  dom.reportBadge().textContent = data.model_version || "Generated";

  dom.reportSection().style.display = "block";
  dom.reportSection().scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── History ──
function addToHistory(result) {
  // avoid duplicates by gstin
  state.history = state.history.filter((h) => h.gstin !== result.gstin);
  state.history.unshift({
    gstin: result.gstin,
    legal_name: result.legal_name,
    trade_name: result.trade_name,
    vri_score: result.vri_score,
    risk_grade: result.risk_grade,
    probability_of_default: result.probability_of_default,
    timestamp: new Date().toLocaleTimeString(),
  });
  renderHistory();
}

function renderHistory() {
  const grid = dom.historyGrid();
  const empty = dom.historyEmpty();

  if (state.history.length === 0) {
    if (empty) empty.style.display = "flex";
    return;
  }

  if (empty) empty.style.display = "none";

  // Remove old cards
  grid.querySelectorAll(".history-card").forEach((c) => c.remove());

  state.history.forEach((h, i) => {
    const gi = gradeInfo(h.risk_grade);
    const colorCls = getScoreColor(h.vri_score);
    const card = document.createElement("div");
    card.className = "history-card";
    card.style.animationDelay = `${i * 0.05}s`;
    card.innerHTML = `
      <div class="history-card__header">
        <div>
          <div class="history-card__name">${escapeHTML(h.trade_name || h.legal_name)}</div>
          <div class="history-card__gstin">${h.gstin}</div>
        </div>
        <div>
          <span class="history-card__score color-${colorCls}">${h.vri_score}</span>
          <span class="history-card__grade bg-${gi.cls}">${h.risk_grade}</span>
        </div>
      </div>
      <div class="history-card__meta">
        <span>PD: ${(h.probability_of_default * 100).toFixed(1)}%</span>
        <span>${h.timestamp}</span>
      </div>
    `;
    card.addEventListener("click", () => {
      // Switch to score view and re-use the stored result
      switchView("score-view");
      showResultsStep();
      // Re-render from history data (limited info)
      dom.resultTitle().textContent = h.trade_name || h.legal_name;
      dom.resultSubtitle().textContent = h.gstin;
      dom.gaugeScore().className = `gauge__score color-${colorCls}`;
      setGaugeValue(h.vri_score);

      const rgi = gradeInfo(h.risk_grade);
      dom.riskGrade().textContent = h.risk_grade;
      dom.riskGrade().className = `meta-value meta-value--grade bg-${rgi.cls}`;
      dom.pdValue().textContent = (h.probability_of_default * 100).toFixed(2) + "%";
    });
    grid.appendChild(card);
  });
}

// ── UI Navigation ──
function switchView(viewId) {
  dom.views().forEach((v) => v.classList.remove("view--active"));
  const target = $(`#${viewId}`);
  if (target) target.classList.add("view--active");

  dom.navBtns().forEach((btn) => {
    btn.classList.toggle("nav-btn--active", btn.dataset.view === viewId);
  });
}

function showInputStep() {
  dom.stepInput().classList.add("step--active");
  dom.stepResults().classList.remove("step--active");
  dom.reportSection().style.display = "none";
}

function showResultsStep() {
  dom.stepInput().classList.remove("step--active");
  dom.stepResults().classList.add("step--active");
}

// ── Button loading state ──
function setLoading(btn, loading) {
  if (loading) {
    btn.classList.add("btn--loading");
    btn.disabled = true;
  } else {
    btn.classList.remove("btn--loading");
    btn.disabled = false;
  }
}

// ── Toast ──
function toast(message, type = "info") {
  const container = dom.toastContainer();
  const el = document.createElement("div");
  el.className = `toast toast--${type}`;
  el.textContent = message;
  container.appendChild(el);

  setTimeout(() => {
    el.classList.add("toast--exit");
    setTimeout(() => el.remove(), 300);
  }, 4000);
}

// ── Utility ──
function escapeHTML(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ── Event Wiring ──
function init() {
  // Check health
  checkHealth();
  setInterval(checkHealth, 30000);

  // Fetch demo GSTINs
  fetchGSTINs();

  // Nav
  dom.navBtns().forEach((btn) =>
    btn.addEventListener("click", () => switchView(btn.dataset.view))
  );

  // GSTIN input
  const input = dom.gstinInput();
  input.addEventListener("input", () => {
    const val = input.value.toUpperCase();
    input.value = val;
    const { valid, error } = validateGSTIN(val);

    dom.gstinError().textContent = error;
    input.classList.remove("input-field--valid", "input-field--invalid");

    if (val.length === 15) {
      input.classList.add(valid ? "input-field--valid" : "input-field--invalid");
    }

    dom.btnScore().disabled = !valid;
    dom.btnReport().disabled = !valid;
  });

  // Score button
  dom.btnScore().addEventListener("click", async () => {
    const gstin = input.value.toUpperCase().trim();
    if (!validateGSTIN(gstin).valid) return;

    setLoading(dom.btnScore(), true);
    try {
      const res = await scoreGSTIN(gstin);
      showResultsStep();
      renderScoringResult(res);
      toast("Credit analysis complete", "success");
    } catch (err) {
      toast(err.message || "Scoring failed", "error");
    } finally {
      setLoading(dom.btnScore(), false);
    }
  });

  // Report from input view
  dom.btnReport().addEventListener("click", async () => {
    const gstin = input.value.toUpperCase().trim();
    if (!validateGSTIN(gstin).valid) return;

    setLoading(dom.btnReport(), true);
    try {
      // Score first
      const scoreRes = await scoreGSTIN(gstin);
      showResultsStep();
      renderScoringResult(scoreRes);

      // Then generate report
      const reportRes = await generateReport(gstin);
      renderReport(reportRes);
      toast("Full credit memo generated", "success");
    } catch (err) {
      toast(err.message || "Report generation failed", "error");
    } finally {
      setLoading(dom.btnReport(), false);
    }
  });

  // Generate report from results view
  dom.btnGenReport().addEventListener("click", async () => {
    if (!state.currentResult) return;

    setLoading(dom.btnGenReport(), true);
    try {
      const res = await generateReport(state.currentResult.gstin);
      renderReport(res);
      toast("Credit memo generated", "success");
    } catch (err) {
      toast(err.message || "Report generation failed", "error");
    } finally {
      setLoading(dom.btnGenReport(), false);
    }
  });

  // Back button
  dom.btnBack().addEventListener("click", () => {
    showInputStep();
    dom.reportSection().style.display = "none";

    // Reset gauge
    dom.gaugeFill().style.strokeDashoffset = 534;
    dom.gaugeScore().textContent = "--";
  });

  // New analysis button
  dom.btnNewScore().addEventListener("click", () => {
    showInputStep();
    dom.reportSection().style.display = "none";
    dom.gaugeFill().style.strokeDashoffset = 534;
    dom.gaugeScore().textContent = "--";
    input.value = "";
    input.classList.remove("input-field--valid", "input-field--invalid");
    dom.btnScore().disabled = true;
    dom.btnReport().disabled = true;
    dom.gstinError().textContent = "";
    input.focus();
  });

  // Enter key
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !dom.btnScore().disabled) {
      dom.btnScore().click();
    }
  });

  // Render history
  renderHistory();
}

// ── Start ──
document.addEventListener("DOMContentLoaded", init);
