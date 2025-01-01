// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(all(not(debug_assertions), target_os = "windows"), windows_subsystem = "windows")]

mod app;
mod commands;
mod model;
mod state;
mod utils;

use app::spotlight::utils::WebviewWindowExt;
use specta_typescript::Typescript;
use tauri::{Listener, Manager};
use tauri_plugin_autostart::MacosLauncher;
use tauri_specta::{collect_commands, Builder};
use window_vibrancy::{apply_vibrancy, NSVisualEffectMaterial};

fn main() {
    let builder = Builder::<tauri::Wry>::new().commands(collect_commands![
        // Menubar
        commands::menubar::init_menubar,
        commands::menubar::show_menubar_panel,
        commands::menubar::hide_menubar_panel,
        commands::menubar::toggle_menubar_panel,
        commands::menubar::is_menubar_panel_visible,
        commands::menubar::close_menubar_panel,
        // Spotlight
        commands::spotlight::init_spotlight,
        commands::spotlight::show_spotlight_panel,
        commands::spotlight::hide_spotlight_panel,
        commands::spotlight::toggle_spotlight_panel,
        commands::spotlight::is_spotlight_panel_visible,
        commands::spotlight::close_spotlight_panel,
        // Screenshot
        commands::screenshot::take_screenshot,
        // OCR
        commands::ocr::perform_ocr,
        // Nougat
        commands::nougat::launch_sidecar_nougat,
        commands::nougat::is_sidecar_nougat_running,
    ]);

    #[cfg(debug_assertions)] // <- Only export on non-release builds
    builder
        .export(Typescript::default(), "../src/lib/tauri/bindings.ts")
        .expect("Failed to export typescript bindings");

    tauri::Builder::default()
        .manage(state::AppState::new())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_svelte::init())
        .plugin(tauri_plugin_autostart::init(MacosLauncher::LaunchAgent, Some(vec![])))
        .plugin(
            tauri_plugin_log::Builder::new()
                .target(tauri_plugin_log::Target::new(tauri_plugin_log::TargetKind::Stdout))
                .target(tauri_plugin_log::Target::new(tauri_plugin_log::TargetKind::LogDir {
                    file_name: Some("logs".to_string()),
                }))
                .level(log::LevelFilter::Info)
                .max_file_size(50_000)
                .build(),
        )
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            let _ = app.get_webview_window("menubar").expect("no menubar window").set_focus();
        }))
        .plugin(tauri_nspanel::init())
        .invoke_handler(builder.invoke_handler())
        .setup(move |app| {
            // Mount events for the app
            builder.mount_events(app);
            // For SQL: https://github.com/Candid-Engineering/books-db/blob/51986180a3d4b6b02b8f31ace24581f8034ab3f7/src-ui/lib/db/index.ts

            // Make the Dock icon invisible
            app.set_activation_policy(tauri::ActivationPolicy::Accessory);

            let app_handle = app.app_handle();

            let _menubar_view = app.get_webview_window("menubar").unwrap();
            let _spotlight_view = app.get_webview_window("spotlight").unwrap();

            #[cfg(target_os = "macos")]
            apply_vibrancy(&_spotlight_view, NSVisualEffectMaterial::HudWindow, None, Some(10.0))
                .expect("Unsupported platform! 'apply_vibrancy' is only supported on macOS");

            #[cfg(target_os = "windows")]
            apply_blur(&_spotlight_view, Some((18, 18, 18, 125)))
                .expect("Unsupported platform! 'apply_blur' is only supported on Windows");

            #[cfg(target_os = "macos")]
            app::menubar::tray::create(app_handle).expect("Failed to create tray");

            let spotlight_panel: tauri_nspanel::objc_id::Id<
                tauri_nspanel::raw_nspanel::RawNSPanel,
                tauri_nspanel::objc_id::Shared,
            > = _spotlight_view.to_spotlight_panel()?;

            app_handle.listen(format!("{}_panel_did_resign_key", "spotlight"), move |_| {
                spotlight_panel.order_out(None);
            });

            let app_handle_clone = app_handle.clone();
            tauri::async_runtime::spawn(async {
                if !commands::nougat::is_sidecar_nougat_running().await {
                    println!("Sidecar not running. Launching...");
                    commands::nougat::launch_sidecar_nougat(app_handle_clone).unwrap();
                } else {
                    println!("Sidecar is already running.");
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
