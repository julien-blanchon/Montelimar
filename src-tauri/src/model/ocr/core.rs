use anyhow::{Context, Result};
use log::{debug, info};
use ocrs::{DecodeMethod, ImageSource, OcrEngine, OcrEngineParams, TextLine};

use anyhow::anyhow;
use rten::Model;
use std::{fs, path::Path, path::PathBuf};
use url::Url;

fn cache_dir() -> Result<PathBuf, anyhow::Error> {
    let mut cache_dir: PathBuf =
        home::home_dir().ok_or(anyhow!("Failed to determine home directory"))?;
    cache_dir.push(".cache");
    cache_dir.push("ocrs");

    fs::create_dir_all(&cache_dir)?;

    Ok(cache_dir)
}

/// Extract the last path segment from a URL.
///
/// eg. "https://models.com/text-detection.rten" => "text-detection.rten".
#[allow(rustdoc::bare_urls)]
fn filename_from_url(url: &str) -> Option<String> {
    let parsed = Url::parse(url).ok()?;
    let path = Path::new(parsed.path());
    path.file_name().and_then(|f| f.to_str()).map(|s| s.to_string())
}

/// Download a file from `url` to a local cache, if not already fetched, and
/// return the path to the local file.
fn download_file(url: &str, filename: Option<&str>) -> Result<PathBuf, anyhow::Error> {
    let cache_dir = cache_dir()?;
    let filename = match filename {
        Some(fname) => fname.to_string(),
        None => filename_from_url(url).ok_or(anyhow!("Could not get destination filename"))?,
    };
    let file_path = cache_dir.join(filename);
    if file_path.exists() {
        return Ok(file_path);
    }

    eprintln!("Downloading {}...", url);

    let mut reader = ureq::get(url).call()?.into_reader();
    let mut body = Vec::new();
    reader.read_to_end(&mut body)?;

    fs::write(&file_path, &body)?;

    Ok(file_path)
}

/// Load a model from a given source.
///
/// If the source is a URL, the model will be downloaded and cached locally if
/// needed.
pub fn load_model(url: &str) -> Result<Model, anyhow::Error> {
    let model_path = download_file(url, None)?;
    let model = Model::load_file(model_path)?;
    Ok(model)
}

fn format_text_output(text_lines: &[Option<TextLine>]) -> String {
    let lines: Vec<String> = text_lines.iter().flatten().map(|line| line.to_string()).collect();
    lines.join("\n")
}

pub fn run_ocr(
    image_path: &str,
    detection_model: &str,
    recognition_model: &str,
    alphabet: Option<String>,
    decode_method: DecodeMethod,
    allowed_chars: Option<String>,
) -> Result<String> {
    info!("[Models] Loading detection and recognition models...");
    let detection_model = load_model(detection_model).context("Failed to load detection model")?;
    info!("[Models] ✓ Detection model loaded successfully");

    let recognition_model =
        load_model(recognition_model).context("Failed to load recognition model")?;
    info!("[Models] ✓ Recognition model loaded successfully");

    info!("\n[Engine] Initializing OCR engine...");
    #[allow(clippy::needless_update)]
    let engine = OcrEngine::new(OcrEngineParams {
        detection_model: Some(detection_model),
        recognition_model: Some(recognition_model),
        debug: false,
        alphabet,
        decode_method,
        allowed_chars,
        ..Default::default()
    })?;
    info!("[Engine] ✓ OCR engine initialized successfully");

    info!("\n[Image] Loading and preprocessing image...");
    let img = image::open(image_path).context("Failed to load image")?;
    let img = img.into_rgb8();
    debug!("[Image] Image dimensions: {}x{}", img.width(), img.height());

    let img_source = ImageSource::from_bytes(img.as_raw(), img.dimensions())?;
    let ocr_input = engine.prepare_input(img_source)?;
    info!("[Image] ✓ Image preprocessed successfully");

    info!("\n[Detection] Detecting words and lines...");
    let word_rects = engine.detect_words(&ocr_input)?;
    debug!("[Detection] Found {} word rectangles", word_rects.len());

    let line_rects = engine.find_text_lines(&ocr_input, &word_rects);
    debug!("[Detection] Grouped into {} text lines", line_rects.len());

    info!("\n[Recognition] Recognizing text from lines...");
    let line_texts = engine.recognize_text(&ocr_input, &line_rects)?;
    info!("[Recognition] ✓ Text recognition completed");

    info!("\n=== Recognized Text Results ===");
    let mut valid_lines = 0;
    for line in line_texts.iter().flatten().filter(|l| l.to_string().len() > 1) {
        valid_lines += 1;
        info!("Line {}: \"{}\"", valid_lines, line);
    }
    println!("{}", format_text_output(&line_texts));

    Ok(format_text_output(&line_texts))
}
