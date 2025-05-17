use tauri_plugin_http::reqwest::Client;
use tauri_plugin_shell::{ShellExt, process::CommandEvent};
use tauri::{State};
use crate::state::AppState;

#[tauri::command]
#[specta::specta]
pub async fn is_sidecar_nougat_running() -> bool {
    let client = Client::new();
    match client.get("http://127.0.0.1:7771/health").send().await {
        Ok(resp) => {
            log::info!("Health check response: {:?}", resp.status());
            resp.status().is_success()
        },
        Err(e) => {
            log::warn!("Health check failed: {}", e);
            false
        }
    }
}


#[tauri::command]
#[specta::specta]
pub async fn launch_sidecar_nougat<'a>(
    handle: tauri::AppHandle,
    state: State<'a, AppState>,
) -> Result<String, String> {
    log::info!("Attempting to launch sidecar: ocr_mlx");

    let sidecar_command = handle.shell().sidecar("ocr_mlx").map_err(|e| {
        log::error!("Failed to get sidecar: {}", e);
        e.to_string()
    })?;

    log::info!("Sidecar command successfully created.");

    let (mut rx, child) = sidecar_command.spawn().map_err(|e| {
        log::error!("Failed to spawn sidecar: {}", e);
        e.to_string()
    })?;
    log::info!("Sidecar process spawned with PID: {:?}", child.pid());

    // ✅ Save child handle in global app state so it can be killed later
    {
        let mut child_lock = state.sidecar_child.lock().unwrap();
        *child_lock = Some(child);
    }

    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    if let Ok(output) = String::from_utf8(line) {
                        log::info!("[ocr_mlx stdout] {}", output.trim());
                    }
                }
                CommandEvent::Stderr(line) => {
                    if let Ok(output) = String::from_utf8(line) {
                        log::error!("[ocr_mlx stderr] {}", output.trim());
                    }
                }
                other => {
                    log::debug!("[ocr_mlx] Other event: {:?}", other);
                }
            }
        }
    });

    Ok("Nougat sidecar started and logging.".to_string())
}
