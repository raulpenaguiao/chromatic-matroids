"use strict";

// CM_BASE is injected by the template (e.g. "/chromatic-matroids")

// ── Local store (localStorage-backed, per-browser) ────────────────────────────
const LocalStore = {
  _KEY: "cm_matroids",
  _cache: null,

  _load() {
    if (!this._cache) {
      const raw = localStorage.getItem(this._KEY);
      this._cache = raw ? JSON.parse(raw) : { matroids: [], nextId: 1 };
    }
    return this._cache;
  },

  _save() { localStorage.setItem(this._KEY, JSON.stringify(this._cache)); },

  getAll() { return this._load().matroids; },
  get(id)  { return this._load().matroids.find(m => m.id === id) ?? null; },

  add(data) {
    const d = this._load();
    const entry = { ...data, id: d.nextId++ };
    d.matroids.push(entry);
    this._save();
    return entry;
  },

  addMany(arr) {
    const d = this._load();
    const entries = arr.map(m => ({ ...m, id: d.nextId++ }));
    d.matroids.push(...entries);
    this._save();
    return entries;
  },

  remove(id) {
    const d = this._load();
    d.matroids = d.matroids.filter(m => m.id !== id);
    this._save();
  },

  replaceAll(matroids) {
    const d = this._load();
    d.matroids = matroids;
    this._save();
  },

  update(id, changes) {
    const m = this._load().matroids.find(m => m.id === id);
    if (m) { Object.assign(m, changes); this._save(); }
  },
};

// ── State ─────────────────────────────────────────────────────────────────────
const state = { selected: new Set() };
let graphEditor = null;
let _busy = false;

// Wrap any async handler: shows cursor, disables compute toolbar, animates btn.
async function _withBusy(btn, fn) {
  if (_busy) return;
  _busy = true;
  document.body.classList.add("busy");
  document.querySelectorAll(".toolbar button").forEach(b => { b.disabled = true; });
  if (btn) { btn.disabled = true; btn.dataset.origText = btn.textContent; btn.textContent += "…"; }
  try { await fn(); }
  finally {
    _busy = false;
    document.body.classList.remove("busy");
    document.querySelectorAll(".toolbar button").forEach(b => { b.disabled = false; });
    if (btn) { btn.disabled = false; btn.textContent = btn.dataset.origText; }
  }
}

// ── API helper ────────────────────────────────────────────────────────────────
async function apiPost(path, body) {
  const r = await fetch(CM_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`Server error ${r.status}`);
  const text = await r.text();
  try { return JSON.parse(text); }
  catch { throw new Error(`Unexpected response: ${text.slice(0, 120)}`); }
}

// ── Render ────────────────────────────────────────────────────────────────────
function renderMatroids() {
  const matroids = LocalStore.getAll();
  const list = document.getElementById("matroid-list");

  // keep select-all checkbox in sync
  const cb = document.getElementById("select-all-cb");
  if (cb) {
    const n = matroids.length;
    const sel = matroids.filter(m => state.selected.has(m.id)).length;
    cb.checked = n > 0 && sel === n;
    cb.indeterminate = sel > 0 && sel < n;
  }

  if (!matroids.length) {
    list.innerHTML = '<p style="color:var(--text-muted);padding:12px;font-style:italic">No matroids yet.</p>';
    return;
  }
  list.innerHTML = matroids.map(m => `
    <div class="matroid-card ${state.selected.has(m.id) ? "selected" : ""}" id="card-${m.id}">
      <div class="card-top">
        <input type="checkbox" ${state.selected.has(m.id) ? "checked" : ""}
          onchange="App.toggleSelect(${m.id}, this.checked)">
        <div class="card-label" title="${esc(m.label)}" ondblclick="App.startRename(${m.id}, this)">${esc(m.label)}</div>
      </div>
      <div class="card-meta">n=${m.n} &nbsp; rank=${m.rank} &nbsp; bases=${m.num_bases}</div>
      <div class="card-actions">
        <button class="btn-sm btn-op" onclick="App.inspectBases(${m.id})">Inspect bases</button>
        <button class="btn-sm btn-op" onclick="App.showDeleteElems(${m.id})">Delete elems</button>
        <button class="btn-sm btn-op" onclick="App.showContract(${m.id})">Contract</button>
        <button class="btn-sm btn-op" onclick="App.showDirectSum(${m.id})">⊕ Direct sum</button>
        <button class="btn-sm btn-danger" onclick="App.removeMatroid(${m.id})">✕</button>
      </div>
    </div>`).join("");
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Results ───────────────────────────────────────────────────────────────────
function showResults(html) {
  const el = document.getElementById("results-content");
  el.className = "";
  el.innerHTML = html;
}

function showError(msg) {
  showResults(`<div class="result-block"><div class="result-error">${esc(msg)}</div></div>`);
}

function fmtCoeffs(coeffs, notation) {
  const entries = Object.entries(coeffs).filter(([, v]) => v !== 0);
  if (!entries.length) return "<em>0</em>";
  return entries.map(([key, val], i) => {
    const sign   = val < 0 ? (i === 0 ? "−" : " − ") : (i === 0 ? "" : " + ");
    const absVal = Math.abs(val);
    const coeff  = absVal === 1 ? "" : `${absVal} `;
    return `${sign}${coeff}${notation}<sub>${esc(key)}</sub>`;
  }).join("");
}

// ── App ───────────────────────────────────────────────────────────────────────
const App = {

  toggleSelect(id, checked) {
    if (checked) state.selected.add(id); else state.selected.delete(id);
    renderMatroids();
  },

  toggleSelectAll(checked) {
    if (checked) LocalStore.getAll().forEach(m => state.selected.add(m.id));
    else state.selected.clear();
    renderMatroids();
  },

  clearResults() {
    const el = document.getElementById("results-content");
    el.className = "results-placeholder";
    el.textContent = "Select matroids and click an operation above.";
  },

  removeMatroid(id) {
    LocalStore.remove(id);
    state.selected.delete(id);
    renderMatroids();
  },

  clearSelected() {
    const ids = [...state.selected];
    if (!ids.length) return alert("No matroids selected.");
    if (!confirm(`Remove ${ids.length} selected matroid${ids.length > 1 ? "s" : ""}?`)) return;
    ids.forEach(id => LocalStore.remove(id));
    state.selected.clear();
    renderMatroids();
  },

  clearAll() {
    const n = LocalStore.getAll().length;
    if (!n) return;
    if (!confirm(`Remove all ${n} matroid${n > 1 ? "s" : ""}?`)) return;
    LocalStore.replaceAll([]);
    state.selected.clear();
    renderMatroids();
  },

  // ── Inspect bases (local — no server call) ─────────────────────────────
  inspectBases(id) {
    const m = LocalStore.get(id);
    if (!m) return;
    document.getElementById("modal-bases-title").textContent =
      `Bases of ${m.label}  (${m.bases.length} total)`;
    document.getElementById("modal-bases-content").innerHTML =
      m.bases.map((b, i) =>
        `<div class="basis-row">${i + 1}. {${b.join(", ")}}</div>`
      ).join("");
    Modal.show("modal-bases");
  },

  // ── Rename label (double-click on card-label) ─────────────────────────
  startRename(id, el) {
    const m = LocalStore.get(id);
    if (!m) return;
    const input = document.createElement("input");
    input.className = "card-label-input";
    input.value = m.label;
    let done = false;
    const commit = () => {
      if (done) return;
      done = true;
      const v = input.value.trim();
      if (v) LocalStore.update(id, { label: v });
      renderMatroids();
    };
    input.addEventListener("blur", commit);
    input.addEventListener("keydown", e => {
      if (e.key === "Enter") { e.preventDefault(); commit(); }
      if (e.key === "Escape") { done = true; renderMatroids(); }
    });
    el.replaceWith(input);
    input.focus(); input.select();
  },

  // ── Export list to JSON ───────────────────────────────────────────────
  exportJSON() {
    const data = LocalStore.getAll();
    if (!data.length) return alert("No matroids to export.");
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "matroids.json"; a.click();
    URL.revokeObjectURL(url);
  },

  // ── Clear isomorphic duplicates ────────────────────────────────────────
  async clearIsomorphic() {
    const all = LocalStore.getAll();
    if (!all.length) return;
    const btn = document.getElementById("dedupe-btn");
    if (btn) { btn.disabled = true; btn.textContent = "Clearing…"; }
    try {
      const deduped = await apiPost("/api/ops/deduplicate", all);
      const keptIds = new Set(deduped.map(m => m.id));
      LocalStore.replaceAll(LocalStore.getAll().filter(m => keptIds.has(m.id)));
      state.selected = new Set([...state.selected].filter(id => keptIds.has(id)));
      const removed = all.length - deduped.length;
      renderMatroids();
      if (removed) alert(`Removed ${removed} isomorphic duplicate${removed > 1 ? "s" : ""}.`);
      else alert("No duplicates found.");
    } catch(e) { alert(e.message); }
    finally { if (btn) { btn.disabled = false; btn.textContent = "Clear duplicates"; } }
  },

  // ── Add ────────────────────────────────────────────────────────────────
  async addUniform() {
    const n = parseInt(document.getElementById("u-n").value);
    const r = parseInt(document.getElementById("u-r").value);
    try {
      const data = await apiPost("/api/create/uniform", { n, r });
      if (data.error) return alert("Error: " + data.error);
      LocalStore.add(data); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  async addNested() {
    const n    = parseInt(document.getElementById("ne-n").value);
    const rank = parseInt(document.getElementById("ne-rank").value);
    const parts = document.getElementById("ne-layers").value.trim().split("\n")
      .map(l => l.split(",").map(s => parseInt(s.trim())).filter(x => !isNaN(x)))
      .filter(p => p.length > 0);
    const rank_bounds = document.getElementById("ne-ranks").value.trim()
      .split(",").map(s => parseInt(s.trim())).filter(x => !isNaN(x));
    if (!parts.length) return alert("Enter at least one layer.");
    try {
      const data = await apiPost("/api/create/nested", { n, rank, parts, rank_bounds });
      if (data.error) return alert("Error: " + data.error);
      LocalStore.add(data); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  async addAllLooplessNested() {
    const n = parseInt(document.getElementById("ne-n").value);
    try {
      const list = await apiPost("/api/create/loopless_nested", { n });
      if (!Array.isArray(list)) return alert(list.error || "Unexpected response.");
      if (!list.length) return alert("No loopless nested matroids for n=" + n);
      LocalStore.addMany(list); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  async addAllLooplessNestedByRank() {
    const n    = parseInt(document.getElementById("ne-n").value);
    const rank = parseInt(document.getElementById("ne-rank").value);
    try {
      const list = await apiPost("/api/create/loopless_nested_by_rank", { n, rank });
      if (!Array.isArray(list)) return alert(list.error || "Unexpected response.");
      if (!list.length) return alert(`No loopless nested matroids for n=${n}, rank=${rank}.`);
      LocalStore.addMany(list); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  async addSchubertByRank() {
    const n    = parseInt(document.getElementById("sc-n").value);
    const rank = parseInt(document.getElementById("sc-rank").value);
    try {
      const list = await apiPost("/api/create/schubert_by_rank", { n, rank });
      if (!Array.isArray(list)) return alert(list.error || "Unexpected response.");
      if (!list.length) return alert(`No Schubert matroids for n=${n}, rank=${rank}.`);
      LocalStore.addMany(list); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  async addFromMatrix() {
    const label  = document.getElementById("mat-label").value.trim() || "M";
    const matrix = document.getElementById("mat-input").value;
    try {
      const result = await apiPost("/api/create/matrix", { label, matrix });
      if (result.error) return alert("Error: " + result.error);
      LocalStore.add(result); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  clearGraph() { if (graphEditor) graphEditor.clear(); },

  async addGraphic() {
    if (!graphEditor) return alert("Graph editor not ready.");
    const data = graphEditor.getData();
    if (!data.vertices.length) return alert("Draw at least one vertex.");
    try {
      const result = await apiPost("/api/create/graphic", data);
      if (result.error) return alert("Error: " + result.error);
      LocalStore.add(result); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  async addCustom() {
    const label = document.getElementById("c-label").value.trim() || "M";
    const ground_set = document.getElementById("c-ground").value
      .split(",").map(s => parseInt(s.trim())).filter(n => !isNaN(n));
    const bases = document.getElementById("c-bases").value.trim().split("\n")
      .map(l => l.split(",").map(s => parseInt(s.trim())).filter(n => !isNaN(n)))
      .filter(b => b.length > 0);
    try {
      const result = await apiPost("/api/create/from_bases", { label, ground_set, bases });
      if (result.error) return alert("Error: " + result.error);
      LocalStore.add(result); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  // ── Modify — each op offers "add as new" or "replace current" ──────────
  showDeleteElems(id) {
    const m = LocalStore.get(id);
    if (!m) return;
    document.getElementById("modal-elements-title").textContent = `Delete elements from ${m.label}`;
    document.getElementById("modal-elements-hint").textContent =
      "Selected elements are removed (restriction to complement).";
    _buildElementCheckboxes(m.ground_set);
    document.getElementById("modal-elements-btn-new").onclick     = () => App._applyOp("delete", id, false);
    document.getElementById("modal-elements-btn-replace").onclick = () => App._applyOp("delete", id, true);
    Modal.show("modal-elements");
  },

  showContract(id) {
    const m = LocalStore.get(id);
    if (!m) return;
    document.getElementById("modal-elements-title").textContent = `Contract elements in ${m.label}`;
    document.getElementById("modal-elements-hint").textContent = "Selected elements are contracted.";
    _buildElementCheckboxes(m.ground_set);
    document.getElementById("modal-elements-btn-new").onclick     = () => App._applyOp("contract", id, false);
    document.getElementById("modal-elements-btn-replace").onclick = () => App._applyOp("contract", id, true);
    Modal.show("modal-elements");
  },

  async _applyOp(kind, id, replace) {
    const m = LocalStore.get(id);
    if (!m) return;
    const elements = _getCheckedElements();
    if (!elements.length) return alert("Select at least one element.");
    const path = kind === "delete" ? "/api/ops/delete_elements" : "/api/ops/contract";
    try {
      const result = await apiPost(path, {
        ground_set: m.ground_set, bases: m.bases, label: m.label, elements,
      });
      if (result.error) return alert("Error: " + result.error);
      if (replace) { LocalStore.remove(id); state.selected.delete(id); }
      LocalStore.add(result);
      Modal.close("modal-elements");
      renderMatroids();
    } catch(e) { alert(e.message); }
  },

  // Direct sum includes self in list
  showDirectSum(id) {
    const m = LocalStore.get(id);
    if (!m) return;
    document.getElementById("modal-ds-title").textContent = `Direct sum with ${m.label}`;
    const all = LocalStore.getAll();
    document.getElementById("modal-ds-list").innerHTML =
      all.length
        ? all.map((other, i) => `
            <label>
              <input type="radio" name="ds-other" value="${other.id}" ${i === 0 ? "checked" : ""}>
              <span><b>${esc(other.label)}</b> &nbsp;<span style="color:var(--text-muted)">n=${other.n} rank=${other.rank}</span></span>
            </label>`).join("")
        : "<p style='color:var(--text-muted)'>No matroids.</p>";
    document.getElementById("modal-ds-btn").onclick = () => App._applyDirectSum(id);
    Modal.show("modal-directsum");
  },

  async _applyDirectSum(id) {
    const m1 = LocalStore.get(id);
    const radio = document.querySelector("input[name='ds-other']:checked");
    if (!radio) return alert("Select a matroid.");
    const m2 = LocalStore.get(parseInt(radio.value));
    if (!m1 || !m2) return alert("Matroid not found.");
    try {
      const result = await apiPost("/api/ops/direct_sum", {
        m1: { ground_set: m1.ground_set, bases: m1.bases, label: m1.label },
        m2: { ground_set: m2.ground_set, bases: m2.bases, label: m2.label },
      });
      if (result.error) return alert("Error: " + result.error);
      LocalStore.add(result); Modal.close("modal-directsum"); renderMatroids();
    } catch(e) { alert(e.message); }
  },

  // ── Compute ────────────────────────────────────────────────────────────
  async computeQSym(btn) {
    await _withBusy(btn, async () => {
      const items = [...state.selected].map(id => LocalStore.get(id)).filter(Boolean);
      if (!items.length) return alert("Select at least one matroid.");
      try {
        const results = await apiPost("/api/compute/qsym", items);
        showResults(results.map(r => r.error
          ? `<div class="result-block"><div class="result-title">${esc(r.label)}</div><div class="result-error">${esc(r.error)}</div></div>`
          : `<div class="result-block">
               <div class="result-title">QSym of ${esc(r.label)}</div>
               <div class="result-formula">${fmtCoeffs(r.coefficients, "M")}</div>
             </div>`
        ).join(""));
      } catch(e) { showError(e.message); }
    });
  },

  async computeWQSym(btn) {
    await _withBusy(btn, async () => {
      const items = [...state.selected].map(id => LocalStore.get(id)).filter(Boolean);
      if (!items.length) return alert("Select at least one matroid.");
      try {
        const results = await apiPost("/api/compute/wqsym", items);
        showResults(results.map(r => r.error
          ? `<div class="result-block"><div class="result-title">${esc(r.label)}</div><div class="result-error">${esc(r.error)}</div></div>`
          : `<div class="result-block">
               <div class="result-title">WQSym of ${esc(r.label)}</div>
               <div class="result-formula">${fmtCoeffs(r.coefficients, "M")}</div>
             </div>`
        ).join(""));
      } catch(e) { showError(e.message); }
    });
  },

  async computeZRank(btn) {
    await _withBusy(btn, async () => {
      const items = [...state.selected].map(id => LocalStore.get(id)).filter(Boolean);
      if (!items.length) return alert("Select at least one matroid.");
      try {
        const r = await apiPost("/api/compute/zrank", items);
        if (r.error) return showError(r.error);
        const labels = r.labels.map(l => `<code>${esc(l)}</code>`).join(", ");
        showResults(`<div class="result-block">
          <div class="result-title">Span dimension</div>
          <div class="result-rank">${r.rank}</div>
          <div class="result-rank-meta">${r.rows} matroids × ${r.cols} basis elements &nbsp;·&nbsp; ${labels}</div>
        </div>`);
      } catch(e) { showError(e.message); }
    });
  },

  async computeZIndex(btn) {
    await _withBusy(btn, async () => {
      const items = [...state.selected].map(id => LocalStore.get(id)).filter(Boolean);
      if (!items.length) return alert("Select at least one matroid.");
      try {
        const r = await apiPost("/api/compute/zindex", items);
        if (r.error) return showError(r.error);
        const labels = r.labels.map(l => `<code>${esc(l)}</code>`).join(", ");
        const nontrivial = r.factors.filter(d => d > 1);
        const factorsStr = r.factors.length
          ? r.factors.join(" | ")
          : "—";
        const saturated = r.index === 1
          ? `<span style="color:var(--success)">saturated</span>`
          : `<span style="color:var(--danger)">not saturated</span>`;
        showResults(`<div class="result-block">
          <div class="result-title">Z-index of WQSym span &nbsp;·&nbsp; ${saturated}</div>
          <div class="result-rank">${r.index}</div>
          <div class="result-rank-meta">
            Invariant factors: ${factorsStr}<br>
            ${r.rows} matroids × ${r.cols} basis elements &nbsp;·&nbsp; ${labels}
          </div>
        </div>`);
      } catch(e) { showError(e.message); }
    });
  },

  async addAllSchubert() {
    const n = parseInt(document.getElementById("sc-n").value);
    try {
      const list = await apiPost("/api/create/schubert", { n });
      if (!Array.isArray(list)) return alert(list.error || "Unexpected response.");
      if (!list.length) return alert(`No Schubert matroids for n=${n}.`);
      LocalStore.addMany(list); Modal.close("modal-add"); renderMatroids();
    } catch(e) { alert(e.message); }
  },
};

// ── Element checkbox helpers ──────────────────────────────────────────────────
function _buildElementCheckboxes(groundSet) {
  document.getElementById("modal-elements-boxes").innerHTML =
    groundSet.map(e => `<label><input type="checkbox" value="${e}"> ${e}</label>`).join("");
}
function _getCheckedElements() {
  return [...document.querySelectorAll("#modal-elements-boxes input:checked")]
    .map(cb => parseInt(cb.value));
}

// ── Modal helpers ─────────────────────────────────────────────────────────────
const Modal = {
  show(id) { document.getElementById(id).classList.remove("hidden"); },
  close(id) { document.getElementById(id).classList.add("hidden"); },
  showAdd() {
    Modal.show("modal-add");
    if (!graphEditor) {
      graphEditor = new GraphEditor(document.getElementById("graph-canvas"));
    } else {
      graphEditor._resize();
    }
  },
};

// close modals on backdrop click or Escape
document.querySelectorAll(".modal-backdrop").forEach(el => {
  el.addEventListener("click", e => { if (e.target === el) el.classList.add("hidden"); });
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-backdrop:not(.hidden)")
      .forEach(el => el.classList.add("hidden"));
  }
});

// tab switching
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    const name = tab.dataset.tab;
    tab.closest(".modal").querySelectorAll(".tab")
      .forEach(t => t.classList.toggle("active", t === tab));
    tab.closest(".modal").querySelectorAll(".tab-content")
      .forEach(tc => tc.classList.toggle("hidden", tc.id !== `tab-${name}`));
    if (name === "graphic" && graphEditor) graphEditor._resize();
  });
});

// ── Main tab switching ────────────────────────────────────────────────────────
function switchMainTab(name) {
  document.querySelectorAll(".main-tab-btn").forEach(b =>
    b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".main-tab-content").forEach(c =>
    c.classList.toggle("hidden", c.id !== `main-tab-${name}`));
}

// ── Matrix Explorer ───────────────────────────────────────────────────────────
const MatrixExplorer = {
  _last: null,         // { row_labels, col_labels, matrix, span_dim, _mode }
  _rowOrder: [],       // _rowOrder[displayPos] = originalDataIndex
  _colOrder: [],
  _hiddenRows: new Set(),
  _hiddenCols: new Set(),
  _dragSrc: null,      // { type: 'row'|'col', dataIdx }
  _dragEndedAt: 0,     // timestamp of last dragend (to suppress spurious click)

  onModeChange() {
    const mode = document.querySelector("input[name='mx-mode']:checked").value;
    document.getElementById("mx-cols-nc-group").classList.toggle("hidden", mode !== "noncommutative");
    document.getElementById("mx-cols-c-group").classList.toggle("hidden", mode !== "commutative");
  },

  async compute(btn) {
    if (_busy) return;
    const n    = parseInt(document.getElementById("mx-n").value);
    const rval = document.getElementById("mx-rank").value.trim();
    const rank = rval === "" ? null : parseInt(rval);
    const mode           = document.querySelector("input[name='mx-mode']:checked").value;
    const matroid_family = document.querySelector("input[name='mx-family']:checked").value;
    const col_set        = mode === "commutative"
      ? "all_compositions"
      : document.querySelector("input[name='mx-colset']:checked").value;

    _busy = true;
    document.body.classList.add("busy");
    btn.disabled = true;
    const origText = btn.textContent;
    btn.textContent = "Computing…";

    try {
      const result = await apiPost("/api/matrix/compute", { n, rank, mode, matroid_family, col_set });
      if (result.error) {
        document.getElementById("mx-content").innerHTML =
          `<div class="result-error">${esc(result.error)}</div>`;
        return;
      }
      MatrixExplorer.render(result, mode);
    } catch(e) {
      document.getElementById("mx-content").innerHTML =
        `<div class="result-error">${esc(e.message)}</div>`;
    } finally {
      _busy = false;
      document.body.classList.remove("busy");
      btn.disabled = false;
      btn.textContent = origText;
    }
  },

  render(data, mode) {
    this._last = { ...data, _mode: mode };
    this._rowOrder = data.row_labels.map((_, i) => i);
    this._colOrder = data.col_labels.map((_, i) => i);
    this._hiddenRows = new Set();
    this._hiddenCols = new Set();
    this._rerender();
  },

  _rerender() {
    if (!this._last) return;
    const { row_labels, col_labels, matrix, span_dim, _mode } = this._last;
    const el   = document.getElementById("mx-content");
    const kind = _mode === "commutative" ? "compositions" : "set compositions";

    const visR = this._rowOrder.filter(i => !this._hiddenRows.has(i));
    const visC = this._colOrder.filter(j => !this._hiddenCols.has(j));
    const hasHidden = this._hiddenRows.size > 0 || this._hiddenCols.size > 0;

    const cc = v => v === 0 ? "mx-cell-zero" : v > 0 ? "mx-cell-pos" : "mx-cell-neg";

    const thead = `<thead><tr>
      <th class="mx-corner"></th>
      ${visC.map(j => `
        <th class="mx-col-hdr" draggable="true"
            ondragstart="MatrixExplorer._onDragStart(event,'col',${j})"
            ondragend="MatrixExplorer._onDragEnd(event)"
            ondragover="MatrixExplorer._onDragOver(event,'col',${j})"
            ondragleave="MatrixExplorer._onDragLeave(event)"
            ondrop="MatrixExplorer._onDrop(event,'col',${j})"
            onclick="MatrixExplorer._onColHdrClick(${j})"
            title="Click to hide · Drag to reorder">
          <div><span>${esc(col_labels[j])}</span></div>
        </th>`).join("")}
    </tr></thead>`;

    const tbody = `<tbody>${visR.map(i => `
      <tr ondragover="MatrixExplorer._onDragOver(event,'row',${i})"
          ondragleave="MatrixExplorer._onDragLeave(event)"
          ondrop="MatrixExplorer._onDrop(event,'row',${i})">
        <th class="mx-row-hdr" draggable="true"
            ondragstart="MatrixExplorer._onDragStart(event,'row',${i})"
            ondragend="MatrixExplorer._onDragEnd(event)"
            onclick="MatrixExplorer._onRowHdrClick(${i})"
            title="Click to hide · Drag to reorder">
          ${esc(row_labels[i])}
        </th>
        ${visC.map(j => {
          const v = matrix[i][j];
          return `<td class="mx-cell ${cc(v)}">${v !== 0 ? v : ""}</td>`;
        }).join("")}
      </tr>`).join("")}
    </tbody>`;

    const hiddenBtn = hasHidden
      ? `<button class="btn-sm btn-secondary" onclick="MatrixExplorer.resetVisibility()">
           Show hidden (${this._hiddenRows.size}r + ${this._hiddenCols.size}c)
         </button>`
      : "";

    el.innerHTML = `
      <div class="mx-stats">
        <span>${visR.length} × ${visC.length} ${kind}</span>
        <span class="mx-stat-dim has-tooltip"
          data-tooltip="Dimension of the span of the terms over ℚ&#10;(rank of the coefficient matrix)">
          Span dimension: <strong>${span_dim}</strong>
        </span>
        <span class="mx-stats-actions">
          ${hiddenBtn}
          <button class="btn-sm btn-secondary mx-latex-btn" onclick="MatrixExplorer.exportLatex()">Export LaTeX</button>
        </span>
      </div>
      <div class="mx-table-wrap">
        <table class="mx-table">${thead}${tbody}</table>
      </div>`;
  },

  // ── Visibility ──────────────────────────────────────────────────────────────
  _onRowHdrClick(i) {
    if (Date.now() - this._dragEndedAt < 300) return;
    this._hiddenRows.add(i);
    this._rerender();
  },

  _onColHdrClick(j) {
    if (Date.now() - this._dragEndedAt < 300) return;
    this._hiddenCols.add(j);
    this._rerender();
  },

  resetVisibility() {
    this._hiddenRows.clear();
    this._hiddenCols.clear();
    this._rerender();
  },

  // ── Drag-and-drop ──────────────────────────────────────────────────────────
  _onDragStart(event, type, dataIdx) {
    this._dragSrc = { type, dataIdx };
    event.dataTransfer.effectAllowed = "move";
    event.stopPropagation();
  },

  _onDragEnd(event) {
    this._dragEndedAt = Date.now();
    this._dragSrc = null;
    document.querySelectorAll(".mx-table .drag-over")
      .forEach(el => el.classList.remove("drag-over"));
  },

  _onDragOver(event, type, dataIdx) {
    if (!this._dragSrc || this._dragSrc.type !== type) return;
    if (this._dragSrc.dataIdx === dataIdx) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
    event.currentTarget.classList.add("drag-over");
  },

  _onDragLeave(event) {
    if (!event.currentTarget.contains(event.relatedTarget)) {
      event.currentTarget.classList.remove("drag-over");
    }
  },

  _onDrop(event, type, dataIdx) {
    event.preventDefault();
    if (!this._dragSrc || this._dragSrc.type !== type) return;
    event.currentTarget.classList.remove("drag-over");
    const from = this._dragSrc.dataIdx;
    const to   = dataIdx;
    this._dragSrc = null;
    if (from === to) return;
    const order = type === "row" ? this._rowOrder : this._colOrder;
    const fi = order.indexOf(from), ti = order.indexOf(to);
    if (fi === -1 || ti === -1) return;
    order.splice(fi, 1);
    order.splice(ti, 0, from);
    this._rerender();
  },

  // ── LaTeX export ────────────────────────────────────────────────────────────
  exportLatex() {
    if (!this._last) return;
    const { row_labels, col_labels, matrix, span_dim } = this._last;
    const visR = this._rowOrder.filter(i => !this._hiddenRows.has(i));
    const visC = this._colOrder.filter(j => !this._hiddenCols.has(j));

    const lesc = s => s
      .replace(/\\/g, "\\textbackslash ")
      .replace(/\{/g, "\\{").replace(/\}/g, "\\}")
      .replace(/_/g, "\\_").replace(/\^/g, "\\^{}")
      .replace(/&/g, "\\&").replace(/#/g, "\\#")
      .replace(/%/g, "\\%").replace(/\$/g, "\\$");

    const colSpec   = "l|" + "c".repeat(visC.length);
    const headerRow = visC.map(j => `\\rotatebox{90}{\\texttt{${lesc(col_labels[j])}}}`).join(" & ");
    const dataRows  = visR.map(i => {
      const cells = visC.map(j => String(matrix[i][j])).join(" & ");
      return `\\texttt{${lesc(row_labels[i])}} & ${cells} \\\\`;
    }).join("\n");

    const latex =
`% Generated by Chromatic Matroids Explorer
% Span dimension: ${span_dim}
\\begin{tabular}{${colSpec}}
\\hline
 & ${headerRow} \\\\
\\hline
${dataRows}
\\hline
\\end{tabular}`;

    navigator.clipboard.writeText(latex).then(() => {
      const btn = document.querySelector(".mx-latex-btn");
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = "Copied!";
        btn.style.color = "var(--success)";
        setTimeout(() => { btn.textContent = orig; btn.style.color = ""; }, 1500);
      }
    }).catch(() => {
      const a = Object.assign(document.createElement("a"), {
        href: URL.createObjectURL(new Blob([latex], { type: "text/plain" })),
        download: "matrix.tex",
      });
      a.click();
    });
  },
};

// ── Sidebar collapse ──────────────────────────────────────────────────────────
function toggleSidebar(panelId, btnId) {
  const panel = document.getElementById(panelId);
  const btn   = document.getElementById(btnId);
  const collapsed = panel.classList.toggle('collapsed');
  btn.innerHTML  = collapsed ? '&#8250;' : '&#8249;';
  btn.title      = collapsed ? 'Expand panel' : 'Collapse panel';
}

// On small screens, start with sidebars collapsed
document.addEventListener('DOMContentLoaded', () => {
  if (window.innerWidth <= 640) {
    ['matroids-sidebar', 'mx-sidebar'].forEach(id => {
      const panel = document.getElementById(id);
      const btn   = document.getElementById(id + '-toggle');
      if (panel && btn) {
        panel.classList.add('collapsed');
        btn.innerHTML = '&#8250;';
        btn.title     = 'Expand panel';
      }
    });
  }
});

// ── Bootstrap ─────────────────────────────────────────────────────────────────
renderMatroids();
