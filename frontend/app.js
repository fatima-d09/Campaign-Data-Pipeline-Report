function $(id) { return document.getElementById(id); }

function getApiBase() {
  return $("apiBase").value.trim().replace(/\/+$/, "");
}

function fmtMoney(n) {
  if (n === null || n === undefined) return "—";
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);
  } catch {
    return String(n);
  }
}

function setStatus(el, msg) {
  el.textContent = msg || "";
}

async function apiGet(path) {
  const url = `${getApiBase()}${path}`;
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

function renderTop(rows) {
  const tbody = $("topTbody");
  tbody.innerHTML = "";

  rows.forEach((r, idx) => {
    const tr = document.createElement("tr");
    tr.dataset.committeeId = r.committee_id;

    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td><strong>${r.name}</strong><br><span class="muted">${r.committee_id}</span></td>
      <td>${r.party ?? "—"}</td>
      <td>${r.state ?? "—"}</td>
      <td class="num">${fmtMoney(r.receipts)}</td>
      <td class="num">${fmtMoney(r.disbursements)}</td>
      <td class="num">${fmtMoney(r.cash_on_hand_end)}</td>
      <td class="num">${fmtMoney(r.debts_owed_by_committee)}</td>
    `;

    tr.addEventListener("click", () => loadDetail(r.committee_id));
    tbody.appendChild(tr);
  });
}

function renderSearch(rows) {
  const tbody = $("searchTbody");
  tbody.innerHTML = "";

  rows.forEach((r) => {
    const tr = document.createElement("tr");
    tr.dataset.committeeId = r.committee_id;

    tr.innerHTML = `
      <td><strong>${r.name}</strong><br><span class="muted">${r.committee_id}</span></td>
      <td>${r.party ?? "—"}</td>
      <td>${r.committee_type ?? "—"}</td>
      <td>${r.state ?? "—"}</td>
    `;

    tr.addEventListener("click", () => loadDetail(r.committee_id));
    tbody.appendChild(tr);
  });
}

async function loadTop() {
  const cycle = Number($("cycle").value);
  const limit = Number($("limit").value);
  const statusEl = $("topStatus");

  setStatus(statusEl, "Loading top committees...");
  try {
    const data = await apiGet(`/committees/top?cycle=${cycle}&limit=${limit}`);
    renderTop(data.results || []);
    setStatus(statusEl, `Loaded ${data.count ?? 0} committees for cycle ${cycle}.`);
  } catch (err) {
    setStatus(statusEl, `Error: ${err.message}`);
  }
}

async function search() {
  const q = $("searchQ").value.trim();
  const statusEl = $("searchStatus");

  if (q.length < 2) {
    setStatus(statusEl, "Type at least 2 characters.");
    return;
  }

  setStatus(statusEl, "Searching...");
  try {
    const data = await apiGet(`/committees/search?q=${encodeURIComponent(q)}&limit=25`);
    renderSearch(data.results || []);
    setStatus(statusEl, `Found ${data.count ?? 0} result(s) for "${q}".`);
  } catch (err) {
    setStatus(statusEl, `Error: ${err.message}`);
  }
}

async function loadDetail(committeeId) {
  const cycle = Number($("cycle").value);

  $("detailName").textContent = "Loading…";
  $("detailMeta").textContent = committeeId;
  $("detailCycle").textContent = `Cycle: ${cycle}`;
  setStatus($("detailStatus"), "");

  // Reset metrics quickly
  $("mReceipts").textContent = "—";
  $("mDisbursements").textContent = "—";
  $("mCash").textContent = "—";
  $("mDebt").textContent = "—";

  try {
    const data = await apiGet(`/committees/${committeeId}?cycle=${cycle}`);
    if (data.error) {
      $("detailName").textContent = "Not found";
      setStatus($("detailStatus"), data.error);
      return;
    }

    const c = data.committee;
    const t = data.totals;

    $("detailName").textContent = c.name;
    $("detailMeta").textContent = `${c.committee_id} · ${c.party ?? "—"} · ${c.state ?? "—"} · ${c.committee_type ?? "—"}`;
    $("detailCycle").textContent = `Cycle: ${cycle}`;

    if (!t) {
      setStatus($("detailStatus"), "No totals found in DB for this cycle. Try running ingestion for this cycle.");
      return;
    }

    $("mReceipts").textContent = fmtMoney(t.receipts);
    $("mDisbursements").textContent = fmtMoney(t.disbursements);
    $("mCash").textContent = fmtMoney(t.cash_on_hand_end);
    $("mDebt").textContent = fmtMoney(t.debts_owed_by_committee);
    setStatus($("detailStatus"), `Updated: ${t.updated_at ?? "—"}`);

  } catch (err) {
    $("detailName").textContent = "Error";
    setStatus($("detailStatus"), err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  $("loadTopBtn").addEventListener("click", loadTop);
  $("searchBtn").addEventListener("click", search);

  $("searchQ").addEventListener("keydown", (e) => {
    if (e.key === "Enter") search();
  });

  // Auto-load on first visit
  loadTop();
});
