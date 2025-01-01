use std::sync::Once;
use tauri_nspanel::ManagerExt;

use crate::app::menubar::utils::{
    setup_menubar_panel_listeners, swizzle_to_menubar_panel, update_menubar_appearance,
};

static INIT: Once = Once::new();

#[tauri::command]
#[specta::specta]
pub fn init_menubar(app_handle: tauri::AppHandle) {
    INIT.call_once(|| {
        // swizzle the webview to the menubar panel
        swizzle_to_menubar_panel(&app_handle);

        // update the menubar appearance
        update_menubar_appearance(&app_handle);

        // setup the listeners for the menubar panel
        setup_menubar_panel_listeners(&app_handle);
    });
}

#[tauri::command]
#[specta::specta]
pub fn show_menubar_panel(app_handle: tauri::AppHandle) {
    let panel = app_handle.get_webview_panel("menubar").unwrap();
    panel.show();
}

#[tauri::command]
#[specta::specta]
pub fn hide_menubar_panel(app_handle: tauri::AppHandle) {
    let panel = app_handle.get_webview_panel("menubar").unwrap();
    if panel.is_visible() {
        panel.order_out(None);
    }
}

#[tauri::command]
#[specta::specta]
pub fn toggle_menubar_panel(app_handle: tauri::AppHandle) {
    let panel = app_handle.get_webview_panel("menubar").unwrap();
    if panel.is_visible() {
        panel.order_out(None);
    } else {
        panel.show();
    }
}

#[tauri::command]
#[specta::specta]
pub fn is_menubar_panel_visible(app_handle: tauri::AppHandle) -> bool {
    let panel = app_handle.get_webview_panel("menubar").unwrap();
    panel.is_visible()
}

#[tauri::command]
#[specta::specta]
pub fn close_menubar_panel(app_handle: tauri::AppHandle) {
    let panel = app_handle.get_webview_panel("menubar").unwrap();
    panel.close();
}
