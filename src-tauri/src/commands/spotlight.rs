use tauri::AppHandle;
use tauri_nspanel::ManagerExt;

#[tauri::command]
#[specta::specta]
pub fn init_spotlight(_app_handle: AppHandle) {
    // Nothing to do here
}

#[tauri::command]
#[specta::specta]
pub fn show_spotlight_panel(app_handle: AppHandle) {
    let panel = app_handle.get_webview_panel("spotlight").unwrap();
    panel.show();
}

#[tauri::command]
#[specta::specta]
pub fn hide_spotlight_panel(app_handle: AppHandle) {
    let panel = app_handle.get_webview_panel("spotlight").unwrap();
    if panel.is_visible() {
        panel.order_out(None);
    }
}

#[tauri::command]
#[specta::specta]
pub fn toggle_spotlight_panel(app_handle: AppHandle) {
    let panel = app_handle.get_webview_panel("spotlight").unwrap();
    if panel.is_visible() {
        panel.order_out(None);
    } else {
        panel.show();
    }
}

#[tauri::command]
#[specta::specta]
pub fn is_spotlight_panel_visible(app_handle: AppHandle) -> bool {
    let panel = app_handle.get_webview_panel("spotlight").unwrap();
    panel.is_visible()
}

#[tauri::command]
#[specta::specta]
pub fn close_spotlight_panel(app_handle: AppHandle) {
    let panel = app_handle.get_webview_panel("spotlight").unwrap();
    panel.close();
}
