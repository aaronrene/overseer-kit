//! Spawn the canonical ``ok app`` process and parse its startup banner.

use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpStream;
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

impl Drop for OkAppChild {
    fn drop(&mut self) {
        self.kill();
    }
}

fn explicit_path(flag: &str) -> Option<PathBuf> {
    let args: Vec<String> = std::env::args().collect();
    let positions: Vec<usize> = args.iter().enumerate().filter(|(_, a)| a.as_str() == flag).map(|(i, _)| i).collect();
    if positions.len() > 1 { panic!("duplicate desktop binding option"); }
    positions.first().map(|i| PathBuf::from(args.get(i + 1).expect("missing desktop binding value")).canonicalize().expect("physical desktop path required"))
}

pub fn resolve_kit_root() -> PathBuf {
    if let Some(root) = explicit_path("--kit-root") { return root; }
    let executable = std::env::current_exe().expect("desktop executable location");
    let resources = executable.parent().expect("executable parent").join("../Resources/kit");
    resources.canonicalize().expect("bundled kit missing; development requires --kit-root")
}

pub fn resolve_repo_root(_kit_root: &Path) -> PathBuf {
    explicit_path("--repo").expect("desktop requires --repo with an explicitly bound checkout")
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
        .stdout(Stdio::null())
        .stderr(Stdio::piped());
    command
}

pub fn spawn_ok_app(kit_root: &Path, repo_root: &Path, port: u16) -> Result<(OkAppChild, StartupBanner), String> {
    let checked = Command::new(kit_root.join("cli/ok"))
        .args(["status", "--json", "--repo"]).arg(repo_root)
        .current_dir(kit_root).output().map_err(|e| e.to_string())?;
    let binding: serde_json::Value = serde_json::from_slice(&checked.stdout)
        .map_err(|_| "desktop could not validate repository/runtime binding".to_string())?;
    if binding["runtime"]["root"].as_str() != kit_root.to_str()
        || binding["repository"]["root"].as_str() != repo_root.to_str()
        || !binding["repository"]["id"].is_string() {
        return Err("desktop preflight binding mismatch".to_string());
    }
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
            if let Err(error) = verify_health(&banner, &binding, port) {
                let _ = child.kill();
                let _ = child.wait();
                return Err(error);
            }
            return Ok((OkAppChild { child }, banner));
        }
        if let Some(status) = child.try_wait().ok().flatten() {
            let tail = lines.join("\n");
            return Err(format!("ok app exited early ({status}): {tail}"));
        }
        thread::sleep(Duration::from_millis(50));
    }

    let _ = child.kill();
    let _ = child.wait();
    Err("timed out waiting for ok app startup banner".to_string())
}

fn verify_health(banner: &StartupBanner, binding: &serde_json::Value, port: u16) -> Result<(), String> {
    if banner.url != format!("http://127.0.0.1:{port}/")
        || banner.session_credential.contains(['\r', '\n']) {
        return Err("desktop startup endpoint mismatch".into());
    }
    let mut stream = TcpStream::connect(("127.0.0.1", port)).map_err(|e| e.to_string())?;
    stream.set_read_timeout(Some(Duration::from_secs(15))).map_err(|e| e.to_string())?;
    write!(stream, "GET /api/health HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nAuthorization: Bearer {}\r\nConnection: close\r\n\r\n", banner.session_credential).map_err(|e| e.to_string())?;
    let mut response = String::new();
    stream.take(131072).read_to_string(&mut response).map_err(|e| e.to_string())?;
    let (headers, body) = response.split_once("\r\n\r\n").ok_or("invalid health response")?;
    let value: serde_json::Value = serde_json::from_str(body).map_err(|e| e.to_string())?;
    if !headers.lines().next().unwrap_or("").contains(" 200 ") || value["ok"] != true
        || value["result"]["repo_root"] != binding["repository"]["root"]
        || value["result"]["repo_id"] != binding["repository"]["id"]
        || value["result"]["runtime"] != binding["runtime"] {
        return Err("desktop health identity mismatch".into());
    }
    Ok(())
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
