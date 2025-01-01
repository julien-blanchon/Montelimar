use log::{error, info};

use crate::model::ocr::{run_ocr, DecodeMethod};

#[tauri::command]
#[specta::specta]
pub async fn perform_ocr(
    image_path: String,
    detection_model: Option<String>,
    recognition_model: Option<String>,
    alphabet: Option<String>,
    allowed_chars: Option<String>,
) -> Result<String, String> {
    info!("Starting OCR process for image: {}", image_path);

    // Default model URLs
    const DEFAULT_DETECTION_MODEL: &str =
        "https://ocrs-models.s3-accelerate.amazonaws.com/text-detection.rten";
    const DEFAULT_RECOGNITION_MODEL: &str =
        "https://ocrs-models.s3-accelerate.amazonaws.com/text-recognition.rten";

    // Use provided models or defaults
    let detection = detection_model.unwrap_or(DEFAULT_DETECTION_MODEL.to_string());
    let recognition = recognition_model.unwrap_or(DEFAULT_RECOGNITION_MODEL.to_string());

    info!("Using detection model: {}", detection);
    info!("Using recognition model: {}", recognition);

    if let Some(ref alphabet) = alphabet {
        info!("Custom alphabet provided: {}", alphabet);
    }
    if let Some(ref chars) = allowed_chars {
        info!("Allowed characters set: {}", chars);
    }

    info!("Starting OCR processing with greedy decoding method");

    // Run OCR with default greedy decoding
    match run_ocr(
        &image_path,
        &detection,
        &recognition,
        alphabet,
        DecodeMethod::Greedy,
        allowed_chars,
    ) {
        Ok(result) => {
            info!("OCR completed successfully. Result length: {} characters", result.len());
            Ok(result)
        }
        Err(e) => {
            error!("OCR processing failed: {}", e);
            Err(e.to_string())
        }
    }
}
