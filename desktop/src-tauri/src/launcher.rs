//! Spawn the canonical ``ok app`` process and parse its startup banner.

use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::mpsc;
use std::thread;
use std::time::{Duration, Instant};

const CANONICAL_LAUNCHER: &str = "ok";
const CANONICAL_SUBCOMMAND: &str = "app";
const DEFAULT_PORT: u16 = 8765;
const DEFAULT_BIND: &str = "127.0.0.1";
const STARTUP_TIMEOUT: Duration = Duration::from_secs(30);

#[derive(Debug, Clone)]
pub struct StartupBanner {
    pub url: String,
    pub session_credential: String,
    pub csrf_token: String,
}

pub struct OkAppChild {
    child: Child,
}

impl OkAppChild {
    pub fn kill(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

pub fn resolve_kit_root() -> PathBuf {
    if let Ok(root) = std::env::var("OVERSEER_KIT_ROOT") {
        return PathBuf::from(root);
    }

    if let Ok(resource_dir) = std::env::var("TAURI_RESOURCE_DIR") {
        let bundled = PathBuf::from(resource_dir).join("kit");
        if bundled.join("cli").join(CANONICAL_LAUNCHER).is_file() {
            return bundled;
        }
    }

    if let Ok(cwd) = std::env::current_dir() {
        for ancestor in cwd.ancestors() {
            let shim = ancestor.join("cli").join(CANONICAL_LAUNCHER);
            if shim.is_file() {
                return ancestor.to_path_buf();
            }
        }
    }

    PathBuf::from(".")
}

pub fn resolve_repo_root(kit_root: &Path) -> PathBuf {
    if let Ok(root) = std::env::var("OVERSEER_REPO_ROOT") {
        return PathBuf::from(root);
    }
    kit_root.to_path_buf()
}

pub fn build_ok_app_command(kit_root: &Path, repo_root: &Path, port: u16) -> Command {
    let ok_shim = kit_root.join("cli").join(CANONICAL_LAUNCHER);
    let mut command = Command::new(ok_shim);
    command
        .arg(CANONICAL_SUBCOMMAND)
        .arg("--repo")
        .arg(repo_root)
        .arg("--port")
        .arg(port.to_string())
        .arg("--bind")
        .arg(DEFAULT_BIND)
        .current_dir(kit_root)
        .env("PYTHONPATH", kit_root)
        .stdout(Stdio::null())
        .stderr(Stdio::piped());
    command
}

pub fn spawn_ok_app(kit_root: &Path, repo_root: &Path, port: u16) -> Result<(OkAppChild, StartupBanner), String> {
    let mut child = build_ok_app_command(kit_root, repo_root, port)
        .spawn()
        .map_err(|err| format!("failed to spawn ok app: {err}"))?;

    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| "ok app stderr pipe missing".to_string())?;

    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        let reader = BufReader::new(stderr);
        for line in reader.lines().map_while(Result::ok) {
            if tx.send(line).is_err() {
                break;
            }
        }
    });

    let deadline = Instant::now() + STARTUP_TIMEOUT;
    let mut lines: Vec<String> = Vec::new();
    while Instant::now() < deadline {
        while let Ok(line) = rx.try_recv() {
            lines.push(line);
        }
        if let Some(banner) = parse_startup_stderr(&lines) {
            return Ok((OkAppChild { child }, banner));
        }
        if let Some(status) = child.try_wait().ok().flatten() {
            let tail = lines.join("\n");
            return Err(format!("ok app exited early ({status}): {tail}"));
        }
        thread::sleep(Duration::from_millis(50));
    }

    let _ = child.kill();
    Err("timed out waiting for ok app startup banner".to_string())
}

pub fn parse_startup_stderr(lines: &[String]) -> Option<StartupBanner> {
    let mut url: Option<String> = None;
    let mut session: Option<String> = None;
    let mut csrf: Option<String> = None;

    for line in lines {
        if let Some(rest) = line.strip_prefix("url: ") {
            url = Some(rest.trim().to_string());
        } else if let Some(rest) = line.strip_prefix("session_credential: ") {
            session = Some(rest.trim().to_string());
        } else if let Some(rest) = line.strip_prefix("csrf_token: ") {
            csrf = Some(rest.trim().to_string());
        }
    }

    Some(StartupBanner {
        url: url?,
        session_credential: session?,
        csrf_token: csrf?,
    })
}

pub fn build_auth_bootstrap_script(banner: &StartupBanner) -> String {
    let session = serde_json::to_string(&banner.session_credential).unwrap_or_else(|_| "\"\"".to_string());
    let csrf = serde_json::to_string(&banner.csrf_token).unwrap_or_else(|_| "\"\"".to_string());
    format!(
        r#"
(function() {{
  const session = {session};
  const csrf = {csrf};
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
"#
    )
}

pub fn default_port() -> u16 {
    DEFAULT_PORT
}
