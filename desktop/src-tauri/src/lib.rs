mod launcher;

use std::sync::Mutex;

use tauri::{Manager, RunEvent, WebviewUrl};

struct AppState {
    child: Mutex<Option<launcher::OkAppChild>>,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let kit_root = launcher::resolve_kit_root();
    let repo_root = launcher::resolve_repo_root(&kit_root);
    let port = launcher::default_port();

    let (child, banner) = match launcher::spawn_ok_app(&kit_root, &repo_root, port) {
        Ok(result) => result,
        Err(err) => {
            eprintln!("desktop launcher error: {err}");
            std::process::exit(2);
        }
    };

    let init_script = launcher::build_auth_bootstrap_script(&banner);
    let external_url = match banner.url.parse() {
        Ok(url) => url,
        Err(err) => {
            eprintln!("invalid ok app url {}: {err}", banner.url);
            std::process::exit(2);
        }
    };

    let app = tauri::Builder::default()
        .manage(AppState {
            child: Mutex::new(Some(child)),
        })
        .setup(move |app| {
            let _window = tauri::WebviewWindowBuilder::new(
                app,
                "main",
                WebviewUrl::External(external_url),
            )
            .title("Overseer Kit")
            .inner_size(1200.0, 800.0)
            .initialization_script(&init_script)
            .build()?;
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(|app_handle, event| {
        if let RunEvent::Exit = event {
            if let Some(state) = app_handle.try_state::<AppState>() {
                if let Ok(mut guard) = state.child.lock() {
                    if let Some(mut child) = guard.take() {
                        child.kill();
                    }
                }
            }
        }
    });
}
