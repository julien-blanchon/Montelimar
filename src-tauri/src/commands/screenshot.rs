use std::process::Command;

#[tauri::command]
#[specta::specta]
pub fn take_screenshot(filename: &str) -> Result<String, String> {
    // let mut return_command = Command::create('/usr/sbin/screencapture', ['-i', '-x', filename]);
    // Launch the screencapture command with the given filename
    let return_command =
        Command::new("/usr/sbin/screencapture").arg("-i").arg("-x").arg(filename).spawn();
    // Handle the Result from spawn()
    let child = return_command.map_err(|e| format!("Failed to take screenshot: {}", e))?;

    // Wait for the child process to complete
    let status = child
        .wait_with_output()
        .map_err(|e| format!("Failed to wait for screenshot process: {}", e))?;

    // Check if the process completed successfully
    if !status.status.success() {
        return Err(format!(
            "Screenshot process failed with exit code: {:?}",
            status.status.code()
        ));
    }

    Ok(filename.to_string())
}
