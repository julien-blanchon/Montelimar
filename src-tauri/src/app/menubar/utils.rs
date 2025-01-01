use std::ffi::CString;

use cocoa::base::nil;
use objc2_foundation::NSEdgeInsetsZero;
use popover::macos::popover::PopoverConfig;
use tauri::{Emitter, Listener, Manager};
use tauri_nspanel::{
    block::ConcreteBlock,
    cocoa::{
        appkit::{NSMainMenuWindowLevel, NSWindowCollectionBehavior},
        base::id,
        foundation::NSRect,
    },
    objc::{class, msg_send, sel, sel_impl},
    panel_delegate, ManagerExt, WebviewWindowExt,
};

#[allow(non_upper_case_globals)]
const NSWindowStyleMaskNonActivatingPanel: i32 = 1 << 7;

pub fn swizzle_to_menubar_panel(app_handle: &tauri::AppHandle) {
    let panel_delegate = panel_delegate!(SpotlightPanelDelegate { window_did_resign_key });

    let window = app_handle.get_webview_window("menubar").unwrap();

    let panel = window.to_panel().unwrap();

    let handle = window.app_handle().clone();

    panel_delegate.set_listener(Box::new(move |delegate_name: String| {
        if delegate_name.as_str() == "window_did_resign_key" {
            let _ = handle.emit("menubar_panel_did_resign_key", ());
        }
    }));

    panel.set_level(NSMainMenuWindowLevel + 1);

    panel.set_style_mask(NSWindowStyleMaskNonActivatingPanel);

    panel.set_collection_behaviour(
        NSWindowCollectionBehavior::NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehavior::NSWindowCollectionBehaviorStationary
            | NSWindowCollectionBehavior::NSWindowCollectionBehaviorFullScreenAuxiliary,
    );

    panel.set_delegate(panel_delegate);
}

pub fn setup_menubar_panel_listeners(app_handle: &tauri::AppHandle) {
    fn hide_menubar_panel(app_handle: &tauri::AppHandle) {
        if check_menubar_frontmost() {
            return;
        }

        let panel = app_handle.get_webview_panel("menubar").unwrap();

        panel.order_out(None);
    }

    let handle = app_handle.clone();

    app_handle.listen_any("menubar_panel_did_resign_key", move |_| {
        hide_menubar_panel(&handle);
    });

    let handle = app_handle.clone();

    let callback = Box::new(move || {
        hide_menubar_panel(&handle);
    });

    register_workspace_listener(
        "NSWorkspaceDidActivateApplicationNotification".into(),
        callback.clone(),
    );

    register_workspace_listener("NSWorkspaceActiveSpaceDidChangeNotification".into(), callback);
}

pub fn update_menubar_appearance(app_handle: &tauri::AppHandle) {
    let window = app_handle.get_webview_window("menubar").unwrap();

    let background_color: id = unsafe { msg_send![class!(NSColor), windowBackgroundColor] };

    let border_color: id = unsafe { msg_send![class!(NSColor), whiteColor] };
    let border_color: id = unsafe { msg_send![border_color, colorWithAlphaComponent: 0.4] };

    let handle: id = window.ns_window().unwrap() as _;
    let content_frame: NSRect = unsafe { msg_send![handle, frame] };
    let center_x = content_frame.size.width / 2.0;

    let config = PopoverConfig {
        arrow_height: 10.0,
        arrow_position: center_x,
        arrow_width: 20.0,
        background_color,
        border_color,
        border_width: 1.0,
        content_edge_insets: unsafe { NSEdgeInsetsZero },
        corner_radius: 10.0,
        popover_to_status_item_margin: 10.0,
        right_edge_margin: 12.0,
    };

    popover::add_view(&window, Some(config));
}

fn register_workspace_listener(name: String, callback: Box<dyn Fn()>) {
    let workspace: id = unsafe { msg_send![class!(NSWorkspace), sharedWorkspace] };

    let notification_center: id = unsafe { msg_send![workspace, notificationCenter] };

    let block = ConcreteBlock::new(move |_notif: id| {
        callback();
    });

    let block = block.copy();

    let name: id =
        unsafe { msg_send![class!(NSString), stringWithCString: CString::new(name).unwrap()] };

    unsafe {
        let _: () = msg_send![
            notification_center,
            addObserverForName: name object: nil queue: nil usingBlock: block
        ];
    }
}

fn app_pid() -> i32 {
    let process_info: id = unsafe { msg_send![class!(NSProcessInfo), processInfo] };

    let pid: i32 = unsafe { msg_send![process_info, processIdentifier] };

    pid
}

fn get_frontmost_app_pid() -> i32 {
    let workspace: id = unsafe { msg_send![class!(NSWorkspace), sharedWorkspace] };

    let frontmost_application: id = unsafe { msg_send![workspace, frontmostApplication] };

    let pid: i32 = unsafe { msg_send![frontmost_application, processIdentifier] };

    pid
}

fn check_menubar_frontmost() -> bool {
    get_frontmost_app_pid() == app_pid()
}
