// use tauri::{App, Manager, WebviewUrl, WebviewWindowBuilder};

// pub fn create_web(app: &mut App) -> tauri::Result<()> {
//     // {
//     //     "title": "spotlight",
//     //     "label": "spotlight",
//     //     "url": "/spotlight",
//     //     "fullscreen": false,
//     //     "height": 150,
//     //     "width": 800,
//     //     "resizable": false,
//     //     "decorations": false,
//     //     "visible": false,
//     //     "transparent": true
//     //   }
//     WebviewWindowBuilder::new(app, "spotlight", tauri::WebviewUrl::App("/spotlight".into()))
//         .title("Spotlight")
//         .resizable(false)
//         .fullscreen(false)
//         .height(150)
//         .width(800)
//         .decorations(false)
//         .visible(false)
//         .transparent(true)
//         .build()?;
//     Ok(())
// }
