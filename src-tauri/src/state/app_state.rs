use std::sync::Mutex;

#[allow(unused)]
pub struct AppState {
    pub app_name: Mutex<String>,
}

impl AppState {
    pub fn new() -> Self {
        Self { app_name: Mutex::new("My Tauri App".to_string()) }
    }
}
