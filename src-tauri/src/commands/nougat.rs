use tauri_plugin_http::reqwest::Client;
use tauri_plugin_shell::ShellExt;

#[tauri::command]
#[specta::specta]
pub fn launch_sidecar_nougat(handle: tauri::AppHandle) -> Result<String, String> {
    let sidecar_command: tauri_plugin_shell::process::Command =
        handle.shell().sidecar("ocr_mlx").unwrap();
    // let (mut rx, mut _child) = sidecar_command.spawn().expect("Failed to spawn sidecar");
    let (_rx, _child) = sidecar_command.spawn().expect("Failed to spawn sidecar");

    Ok("Nougat started".to_string())
}

#[tauri::command]
#[specta::specta]
pub fn is_sidecar_nougat_running() -> bool {
    // client.get("http://127.0.0.1:7771/health")
    let client = Client::new();
    let response = tokio::runtime::Runtime::new()
        .unwrap()
        .block_on(client.get("http://127.0.0.1:7771/health").send());
    response.is_ok()
}
