/** Overseer Kit ok app static UI — in-memory auth only (§Q0.6.2 / §Q4A). */

let sessionCredential = null;
let csrfToken = null;

function setAuthStatus(message, ok) {
  const el = document.getElementById("auth-status");
  el.textContent = message;
  el.className = ok ? "status ok" : "status error";
}

function authHeaders(mutating) {
  const headers = {
    Authorization: `Bearer ${sessionCredential}`,
  };
  if (mutating) {
    headers["X-Overseer-CSRF"] = csrfToken;
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

async function apiFetch(path, { method = "GET", body = null, mutating = false } = {}) {
  const response = await fetch(path, {
    method,
    headers: authHeaders(mutating),
    body: body === null ? undefined : JSON.stringify(body),
  });
  const payload = await response.json();
  return { response, payload };
}

function showJson(targetId, payload) {
  document.getElementById(targetId).textContent = JSON.stringify(payload, null, 2);
}

function requireConfirm(message) {
  return window.confirm(message);
}

function activateTab(tabId) {
  document.querySelectorAll(".tabs button").forEach((b) => b.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
  const button = document.querySelector(`.tabs button[data-tab="${tabId}"]`);
  const panel = document.getElementById(`tab-${tabId}`);
  if (button) button.classList.add("active");
  if (panel) panel.classList.add("active");
}

function flagLabel(value) {
  if (value === true) return "ok";
  if (value === false) return "fail";
  return "n/a";
}

function nested(obj, path) {
  let cur = obj;
  for (const key of path) {
    if (cur === null || cur === undefined || typeof cur !== "object") return undefined;
    cur = cur[key];
  }
  return cur;
}

function humanizeStatus(payload) {
  const result = payload && typeof payload.result === "object" && payload.result !== null
    ? payload.result
    : {};
  const pending = nested(result, ["governance_gates", "pending"]);
  const pendingCount = Array.isArray(pending) ? String(pending.length) : "n/a";
  const rows = [
    { label: "Regime", value: nested(result, ["vcs", "regime"]) ?? "n/a" },
    { label: "Substrate", value: flagLabel(nested(result, ["substrate", "ok"])) },
    { label: "Muse sync", value: flagLabel(nested(result, ["muse_sync", "ok"])) },
    {
      label: "Footprint",
      value: flagLabel(nested(result, ["footprint_self_integrity", "ok"])),
    },
    {
      label: "Exit code",
      value: payload && payload.exit_code !== undefined && payload.exit_code !== null
        ? String(payload.exit_code)
        : "n/a",
    },
    { label: "Pending gates", value: pendingCount },
  ];
  const root = document.getElementById("status-summary");
  root.replaceChildren();
  for (const row of rows) {
    const card = document.createElement("div");
    card.className = "status-card";
    const label = document.createElement("span");
    label.className = "label";
    label.textContent = row.label;
    const value = document.createElement("span");
    value.className = "value";
    value.textContent = String(row.value);
    card.append(label, value);
    root.append(card);
  }
}

document.getElementById("auth-save").addEventListener("click", async () => {
  sessionCredential = document.getElementById("session-input").value.trim();
  csrfToken = document.getElementById("csrf-input").value.trim();
  if (!sessionCredential || !csrfToken) {
    setAuthStatus("Both values are required.", false);
    return;
  }
  try {
    const { response, payload } = await apiFetch("/api/health");
    if (!response.ok || !payload.ok) {
      setAuthStatus("Authentication failed.", false);
      return;
    }
    setAuthStatus("Connected.", true);
    document.getElementById("tabs").hidden = false;
    document.getElementById("content").hidden = false;
    activateTab("overview");
  } catch (err) {
    setAuthStatus(`Connection error: ${err}`, false);
  }
});

document.querySelectorAll(".tabs button").forEach((button) => {
  button.addEventListener("click", () => {
    activateTab(button.dataset.tab);
  });
});

document.getElementById("open-structure").addEventListener("click", () => {
  activateTab("structure");
});

document.getElementById("refresh-status").addEventListener("click", async () => {
  const { payload } = await apiFetch("/api/status");
  humanizeStatus(payload);
  showJson("status-output", payload);
});

document.getElementById("load-roadmap").addEventListener("click", async () => {
  const { payload } = await apiFetch("/api/docs/roadmap");
  showJson("roadmap-output", payload);
});

document.getElementById("load-handover").addEventListener("click", async () => {
  const { payload } = await apiFetch("/api/docs/handover");
  showJson("handover-output", payload);
});

document.getElementById("load-gates").addEventListener("click", async () => {
  const { payload } = await apiFetch("/api/gates");
  showJson("gates-output", payload);
});

document.getElementById("run-freeze").addEventListener("click", async () => {
  const dryRun = document.getElementById("freeze-dry-run").checked;
  if (!dryRun && !requireConfirm("Run freeze review with stamp write? This is irreversible on the feature branch.")) {
    return;
  }
  const path = document.getElementById("freeze-path").value.trim();
  const { payload } = await apiFetch("/api/review/freeze", {
    method: "POST",
    mutating: true,
    body: { path, dry_run: dryRun },
  });
  showJson("freeze-output", payload);
});

document.getElementById("run-sync").addEventListener("click", async () => {
  const write = document.getElementById("sync-write").checked;
  if (write && !requireConfirm("Apply governance-sync writes on the feature branch?")) {
    return;
  }
  const { payload } = await apiFetch("/api/governance-sync", {
    method: "POST",
    mutating: true,
    body: { write },
  });
  showJson("sync-output", payload);
});

document.getElementById("run-honesty").addEventListener("click", async () => {
  const { payload } = await apiFetch("/api/honesty-status", {
    method: "POST",
    mutating: true,
    body: {},
  });
  showJson("honesty-output", payload);
});

document.getElementById("ledger-show").addEventListener("click", async () => {
  const { payload } = await apiFetch("/api/ledger/show");
  showJson("ledger-output", payload);
});

document.getElementById("ledger-verify").addEventListener("click", async () => {
  const { payload } = await apiFetch("/api/ledger/verify", {
    method: "POST",
    mutating: true,
    body: {},
  });
  showJson("ledger-output", payload);
});
