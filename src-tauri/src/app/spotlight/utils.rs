use tauri::{Emitter, Manager, Runtime, WebviewWindow};
use tauri_nspanel::{
    cocoa::{
        appkit::{NSMainMenuWindowLevel, NSView, NSWindowCollectionBehavior},
        base::{id, YES},
        foundation::{NSPoint, NSRect},
    },
    objc::{msg_send, sel, sel_impl},
    panel_delegate, Panel, WebviewWindowExt as PanelWebviewWindowExt,
};
use thiserror::Error;

type TauriError = tauri::Error;

#[derive(Error, Debug)]
enum Error {
    #[error("Unable to convert window to panel")]
    Panel,
    #[error("Monitor with cursor not found")]
    MonitorNotFound,
}

pub trait WebviewWindowExt {
    fn to_spotlight_panel(&self) -> tauri::Result<Panel>;

    fn center_at_cursor_monitor(&self) -> tauri::Result<()>;
}

impl<R: Runtime> WebviewWindowExt for WebviewWindow<R> {
    fn to_spotlight_panel(&self) -> tauri::Result<Panel> {
        println!("Converting window to spotlight panel");

        // Convert window to panel
        let panel = self.to_panel().map_err(|_| TauriError::Anyhow(Error::Panel.into()))?;

        // Set panel level
        panel.set_level(NSMainMenuWindowLevel + 1);

        println!("Panel level set to ");

        // Allows the panel to display on the same space as the full screen window
        panel.set_collection_behaviour(
            NSWindowCollectionBehavior::NSWindowCollectionBehaviorFullScreenAuxiliary,
        );

        println!("Panel collection behaviour set to ");

        #[allow(non_upper_case_globals)]
        const NSWindowStyleMaskNonActivatingPanel: i32 = 1 << 7;

        // Ensures the panel cannot activate the App
        panel.set_style_mask(NSWindowStyleMaskNonActivatingPanel);

        println!("Panel style mask set to ");

        // Set up a delegate to handle key window events for the panel
        //
        // This delegate listens for two specific events:
        // 1. When the panel becomes the key window
        // 2. When the panel resigns as the key window
        //
        // For each event, it emits a corresponding custom event to the app,
        // allowing other parts of the application to react to these panel state changes.

        let panel_delegate = panel_delegate!(SpotlightPanelDelegate {
            window_did_resign_key,
            window_did_become_key
        });

        println!("Panel delegate set");

        let app_handle = self.app_handle().clone();

        let label = self.label().to_string();

        println!("Panel label set to ");

        panel_delegate.set_listener(Box::new(move |delegate_name: String| {
            match delegate_name.as_str() {
                "window_did_become_key" => {
                    let _ = app_handle.emit(format!("{}_panel_did_become_key", label).as_str(), ());
                }
                "window_did_resign_key" => {
                    let _ = app_handle.emit(format!("{}_panel_did_resign_key", label).as_str(), ());
                }
                _ => (),
            }
        }));

        panel.set_delegate(panel_delegate);

        println!("Panel delegate set");

        Ok(panel)
    }

    fn center_at_cursor_monitor(&self) -> tauri::Result<()> {
        let monitor = monitor::get_monitor_with_cursor()
            .ok_or(TauriError::Anyhow(Error::MonitorNotFound.into()))?;

        let monitor_scale_factor = monitor.scale_factor();

        let monitor_size = monitor.size().to_logical::<f64>(monitor_scale_factor);

        let monitor_position = monitor.position().to_logical::<f64>(monitor_scale_factor);

        let window_handle: id = self.ns_window().unwrap() as _;

        let window_frame: NSRect = unsafe { window_handle.frame() };

        println!("Window frame: ");

        let rect = NSRect {
            origin: NSPoint {
                x: (monitor_position.x + (monitor_size.width / 2.0))
                    - (window_frame.size.width / 2.0),
                y: (monitor_position.y + (monitor_size.height / 2.0))
                    - (window_frame.size.height / 2.0),
            },
            size: window_frame.size,
        };

        println!("Setting window frame to ");

        let _: () = unsafe { msg_send![window_handle, setFrame: rect display: YES] };

        Ok(())
    }
}
