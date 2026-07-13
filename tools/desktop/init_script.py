"""Packaging-only Tauri initialization script for in-memory session bootstrap."""

from __future__ import annotations

import json


def build_auth_bootstrap_script(*, session_credential: str, csrf_token: str) -> str:
    """Return JS that fills the Q1 auth panel without persisting secrets."""
    session_json = json.dumps(session_credential)
    csrf_json = json.dumps(csrf_token)
    return f"""
(function() {{
  const session = {session_json};
  const csrf = {csrf_json};
  function bootstrap() {{
    const sessionInput = document.getElementById("session-input");
    const csrfInput = document.getElementById("csrf-input");
    const saveButton = document.getElementById("auth-save");
    if (!sessionInput || !csrfInput || !saveButton) {{
      setTimeout(bootstrap, 50);
      return;
    }}
    sessionInput.value = session;
    csrfInput.value = csrf;
    saveButton.click();
  }}
  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", bootstrap);
  }} else {{
    bootstrap();
  }}
}})();
""".strip()
