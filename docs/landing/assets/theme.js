/** Landing theme toggle — preference only (not auth). Default is always dark. */
(function () {
  // v2: ignore legacy stored preference so first paint stays dark by default.
  var KEY = "overseer-landing-theme-v2";
  var root = document.documentElement;

  function preferred() {
    try {
      var stored = localStorage.getItem(KEY);
      // Only honor an explicit user choice; ignore OS prefers-color-scheme.
      if (stored === "light" || stored === "dark") return stored;
    } catch (_e) {
      /* file:// or blocked storage — fall through */
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

  // Apply immediately so first paint is not light on light-preferring OSes.
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
