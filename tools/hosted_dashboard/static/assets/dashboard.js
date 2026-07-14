/**
 * Hosted governance dashboard UI — viewer Bearer in JS memory only (§HGD.6.7).
 * Do not persist the viewer credential in browser storage APIs.
 */
(function () {
  "use strict";

  /** @type {string|null} */
  var viewerToken = null;

  var authPanel = document.getElementById("auth-panel");
  var tabs = document.getElementById("tabs");
  var content = document.getElementById("content");
  var authStatus = document.getElementById("auth-status");
  var orgOutput = document.getElementById("org-output");
  var orgList = document.getElementById("org-list");
  var repoOutput = document.getElementById("repo-output");

  function api(path) {
    return fetch(path, {
      method: "GET",
      headers: {
        Authorization: "Bearer " + viewerToken,
        Accept: "application/json",
      },
    }).then(function (res) {
      return res.json().then(function (body) {
        return { status: res.status, body: body };
      });
    });
  }

  function showMain() {
    authPanel.hidden = true;
    tabs.hidden = false;
    content.hidden = false;
  }

  document.getElementById("auth-save").addEventListener("click", function () {
    var input = document.getElementById("viewer-input");
    var value = (input && input.value ? input.value : "").trim();
    if (!value) {
      authStatus.textContent = "Token required.";
      return;
    }
    viewerToken = value;
    input.value = "";
    authStatus.textContent = "Connected (token held in memory only).";
    showMain();
    refreshOrg();
  });

  tabs.addEventListener("click", function (ev) {
    var btn = ev.target.closest("button[data-tab]");
    if (!btn) return;
    var name = btn.getAttribute("data-tab");
    tabs.querySelectorAll("button").forEach(function (b) {
      b.classList.toggle("active", b === btn);
    });
    document.querySelectorAll(".tab-panel").forEach(function (panel) {
      panel.classList.toggle("active", panel.id === "tab-" + name);
    });
  });

  function refreshOrg() {
    api("/api/org/summary").then(function (res) {
      orgOutput.textContent = JSON.stringify(res.body, null, 2);
      orgList.innerHTML = "";
      var repos = (res.body.result && res.body.result.repos) || [];
      repos.forEach(function (repo) {
        var li = document.createElement("li");
        li.textContent =
          repo.full_name +
          " — " +
          repo.eligibility +
          (repo.marker_present ? " (marker)" : "");
        li.addEventListener("click", function () {
          document.getElementById("repo-owner").value = repo.owner;
          document.getElementById("repo-name").value = repo.name;
          tabs.querySelector('button[data-tab="repo"]').click();
        });
        orgList.appendChild(li);
      });
    });
  }

  document.getElementById("refresh-org").addEventListener("click", refreshOrg);

  function loadDoc(action) {
    var owner = document.getElementById("repo-owner").value.trim();
    var name = document.getElementById("repo-name").value.trim();
    if (!owner || !name) {
      repoOutput.textContent = "Owner and repo required.";
      return;
    }
    api("/api/repos/" + encodeURIComponent(owner) + "/" + encodeURIComponent(name) + "/" + action).then(
      function (res) {
        repoOutput.textContent = JSON.stringify(res.body, null, 2);
      }
    );
  }

  document.getElementById("load-roadmap").addEventListener("click", function () {
    loadDoc("roadmap");
  });
  document.getElementById("load-handover").addEventListener("click", function () {
    loadDoc("handover");
  });
  document.getElementById("load-gates").addEventListener("click", function () {
    loadDoc("gates");
  });
  document.getElementById("load-marker").addEventListener("click", function () {
    loadDoc("config-marker");
  });
})();
