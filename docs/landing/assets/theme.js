/** Landing theme toggle — preference only (not auth). */
(function () {
  var KEY = "overseer-landing-theme";
  var root = document.documentElement;

  function preferred() {
    try {
      var stored = localStorage.getItem(KEY);
      if (stored === "light" || stored === "dark") return stored;
    } catch (_e) {
      /* file:// or blocked storage — fall through */
    }
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
      return "light";
    }
    return "dark";
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    var next = theme === "dark" ? "light" : "dark";
    btn.setAttribute("aria-label", "Switch to " + next + " mode");
    btn.setAttribute("title", next === "light" ? "Light mode" : "Dark mode");
  }

  apply(preferred());

  document.addEventListener("DOMContentLoaded", function () {
    apply(root.getAttribute("data-theme") || preferred());
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var current = root.getAttribute("data-theme") === "light" ? "light" : "dark";
      var next = current === "dark" ? "light" : "dark";
      apply(next);
      try {
        localStorage.setItem(KEY, next);
      } catch (_e) {
        /* ignore */
      }
    });
  });
})();
