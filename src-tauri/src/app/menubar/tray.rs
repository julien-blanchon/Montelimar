use tauri::{
    image::Image,
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIcon, TrayIconBuilder, TrayIconEvent},
    AppHandle, LogicalPosition, LogicalSize, Manager,
};
use tauri_nspanel::{
    cocoa::{base::id, foundation::NSRect},
    objc::{msg_send, runtime::NO, sel, sel_impl},
    ManagerExt,
};

pub fn create(app_handle: &AppHandle) -> tauri::Result<TrayIcon> {
    // println!("Creating tray icon...");
    let icon = Image::from_bytes(include_bytes!("../../../icons/tray.png"))?;
    // println!("Tray icon loaded successfully.");

    // Example 1
    // let menu = Menu::new();
    // let menu_item2 = MenuItem::new("Menu item #2", false, None);
    // let submenu = Submenu::with_items("Submenu Outer", true,&[
    // &MenuItem::new("Menu item #1", true, Some(Accelerator::new(Some(Modifiers::ALT), Code::KeyD))),
    // &PredefinedMenuItem::separator(),
    // &menu_item2,
    // &MenuItem::new("Menu item #3", true, None),
    // &PredefinedMenuItem::separator(),
    // &Submenu::with_items("Submenu Inner", true,&[
    //     &MenuItem::new("Submenu item #1", true, None),
    //     &PredefinedMenuItem::separator(),
    //     &menu_item2,
    // ])
    // ]);

    //     Context menus (Popup menus)
    // You can also use a [Menu] or a [Submenu] show a context menu.

    // // --snip--
    // let position = muda::PhysicalPosition { x: 100., y: 120. };
    // #[cfg(target_os = "windows")]
    // unsafe { menu.show_context_menu_for_hwnd(window.hwnd() as isize, Some(position.into())) };
    // #[cfg(target_os = "linux")]
    // menu.show_context_menu_for_gtk_window(&gtk_window, Some(position.into()));
    // #[cfg(target_os = "macos")]
    // unsafe { menu.show_context_menu_for_nsview(nsview, Some(position.into())) };

    let quit_i = MenuItem::with_id(app_handle, "quit", "Quit", true, None::<&str>)?;
    let menu = Menu::with_items(app_handle, &[&quit_i])?;

    TrayIconBuilder::with_id("tray")
        .icon(icon)
        .tooltip("MenuBar")
        // .title("MenuBar")
        .icon_as_template(true)
        .menu(&menu)
        .menu_on_left_click(false)
        .on_menu_event(move |app, event| match event.id.as_ref() {
            "quit" => {
                app.exit(0);
            }
            // @TODO: Add and handle more menu entries, like play, pause, open, ...
            _ => {}
        })
        .on_tray_icon_event(|tray, event| {
            // println!("Tray icon event received: {:?}", event);
            let app_handle = tray.app_handle();

            match event {
                TrayIconEvent::Click { button_state, rect, button, .. } => {
                    // println!("Click event detected. Button state: {:?}", button_state);
                    if button_state == MouseButtonState::Up && button == MouseButton::Left {
                        // println!("Button state is UP. Processing...");
                        let panel = app_handle.get_webview_panel("menubar").unwrap();
                        // println!("Retrieved webview panel: {:?}", panel);

                        if panel.is_visible() {
                            // println!("Panel is visible. Hiding panel...");
                            panel.order_out(None);
                            return;
                        }

                        // println!("Panel is not visible. Showing panel...");
                        let monitor_with_cursor = monitor::get_monitor_with_cursor().unwrap();
                        // println!("Monitor with cursor: {:?}", monitor_with_cursor);

                        let scale_factor = monitor_with_cursor.scale_factor();
                        // println!("Scale factor: {}", scale_factor);

                        position_panel_at_menubar_icon(
                            app_handle,
                            rect.position.to_logical(scale_factor),
                            rect.size.to_logical(scale_factor),
                            5.0,
                        );
                        // println!("Positioned panel at menubar icon.");

                        let window = app_handle.get_webview_window("menubar").unwrap();
                        // println!("Retrieved webview window: {:?}", window);

                        let window_monitor = window.current_monitor().unwrap().unwrap();
                        // println!("Window monitor: {:?}", window_monitor);

                        let is_window_in_monitor_with_cursor: bool =
                            window_monitor.position().x as f64 == monitor_with_cursor.position().x;
                        // println!(
                        //     "Is window in monitor with cursor: {}",
                        //     is_window_in_monitor_with_cursor
                        // );

                        if is_window_in_monitor_with_cursor {
                            // println!("Showing panel...");
                            panel.show();
                        }
                    }
                }
                _ => {}
            }
        })
        .build(app_handle)
}

fn position_panel_at_menubar_icon(
    app_handle: &tauri::AppHandle,
    icon_position: LogicalPosition<f64>,
    icon_size: LogicalSize<f64>,
    padding_top: f64,
) {
    let window = app_handle.get_webview_window("menubar").unwrap();

    let monitor = monitor::get_monitor_with_cursor().unwrap();

    let scale_factor = monitor.scale_factor();

    let monitor_pos = monitor.position().to_logical::<f64>(scale_factor);

    let monitor_size = monitor.size().to_logical::<f64>(scale_factor);

    let menubar_height = menubar::get_menubar().height();

    let handle: id = window.ns_window().unwrap() as _;

    let mut win_frame: NSRect = unsafe { msg_send![handle, frame] };

    win_frame.origin.y =
        (monitor_pos.y + monitor_size.height) - menubar_height - win_frame.size.height;

    win_frame.origin.y -= padding_top * scale_factor;

    win_frame.origin.x = icon_position.x + icon_size.width / 2.0 - win_frame.size.width / 2.0;

    let _: () = unsafe { msg_send![handle, setFrame: win_frame display: NO] };

    // let _: () = unsafe { msg_send![handle, setHasShadow: YES] };
}
