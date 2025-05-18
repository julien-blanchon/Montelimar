<h1 align="center">
  <img src="./src-tauri/icons/Square310x310Logo.png" alt="Montélimar OCR" width="128" />
  <br>
  Textify and Latexify every part of your screen
  <br>
</h1>

<h3 align="center">
A OCR toolbox integrated in your mac
</h3>


[![Apache 2 License](https://img.shields.io/badge/License-Apache-green.svg)](https://choosealicense.com/licenses/mit/)
[![Tauri](https://img.shields.io/badge/Tauri-v2-blue.svg)](https://tauri.app)
[![Svelte](https://img.shields.io/badge/Svelte-5-orange.svg)](https://svelte.dev)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Rust](https://img.shields.io/badge/Rust-orange.svg)](https://www.rust-lang.org)

## Preview

<video controls width="600" src="https://raw.githubusercontent.com/julien-blanchon/Montelimar/refs/heads/main/static/MontelimarDemo.mp4"></video>


## Features

- 🔍 **Advanced OCR Capabilities**
  - Text extraction from any part of your screen
  - LaTeX equation recognition and conversion with [Nougat model](https://huggingface.co/Norm/nougat-latex-base)
  - Support for multiple [OCRS](https://github.com/robertknight/ocrs/) models and [Nougat](https://huggingface.co/facebook/nougat-base) models.

- ⚡ **Quick Access**
  - Menubar integration for easy access
  - Global keyboard shortcuts for instant capture
  - Custom shortcuts for specific OCR configurations

- 🎨 **User Interface**
  - Clean and modern interface in the menubar
  - Dark and light theme support
  - Hoverlay panel (spotlight style) to choose model to use for OCR

- 🛠️ **Customization**
  - Configurable OCR settings
  - Customizable keyboard shortcuts
  - Auto-start option
  - Sound feedback toggle

- 📋 **Clipboard Integration**
  - Automatic clipboard copying
  - Quick copy buttons for results

- 📝 **History Management**
  - Screenshot history tracking
  - Search through past OCR results
  - Option to disable history for privacy

- 🔒 **Privacy and Security**
  - Local processing of screenshots
  - Optional history disable feature

## Installation

To install Montelimar with Homebrew:
```shell
# First add the homebrew tap
brew tap julien-blanchon/homebrew-tap
# Then install montelimar
brew install --cask montelimar
```

You can also manually download the .dmg in the [Github Release section](https://github.com/julien-blanchon/Montelimar/releases).

## Getting Started

### Prerequisites

- [Bun](https://bun.sh) - Fast all-in-one JavaScript runtime & package manager
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- [Rust](https://rustup.rs/) - For Tauri's backend

### Development Setup

1. Install the project dependencies for javascript
```bash
bun install
```

2. Python Sidecar Setup:
```bash
# Navigate to src-python directory and create a virtual environment
cd src-python
# Create a virtual environment
uv venv
# Activate the virtual environment
source .venv/bin/activate
# Sync the dependencies
uv sync
```

The Python sidecar (`ocr_mlx`) is packaged using box-packager, which:
- Takes the entry point defined in pyproject.toml (`ocr_mlx.endpoint:main`)
- Bundles all dependencies into a single executable
- Places the executable in `src-tauri/binaries` with platform-specific naming
- Uses PyApp to bootstrap the Python environment at runtime

3. Build the Python Sidecar:
```bash
# This command will:
# 1. Package the Python app using box-packager
# 2. Copy the executable to src-tauri/binaries
# 3. Name it appropriately for your platform
bun run python:package:build

# Initialize the packaged environment
bun run python:package:reset
```

4. Start Development Server:
```bash
# This will:
# 1. Start the Svelte dev server
# 2. Launch the Tauri window
# 3. Initialize the Python sidecar for OCR
bun run tauri dev
```

### Building for Production

```bash
# Build the complete application:
# 1. Checks if Python sidecar needs rebuilding
# 2. Rebuilds sidecar if needed
# 3. Builds the Tauri application
bun run tauri build
```

The built application will be available in `src-tauri/target/release`.

### Development Workflow

#### Frontend Development (SvelteKit + Tauri)
- `src/` - SvelteKit frontend code
- `src-tauri/` - Tauri backend code
- Hot reload enabled for both frontend and Rust changes

#### Python Sidecar Development
- `src-python/` - Python OCR service code
- Development mode: `bun run python:package:dev`
- API development:
  ```bash
  # Generate OpenAPI specs from Python service
  bun run python:package:generate-openapi
  
  # Generate TypeScript client from OpenAPI specs
  bun run python:package:generate-client
  ```

#### Asset Generation
- `bun run icon:generate` - Generate app icons from SVG
- `bun run icon:generate-tray` - Generate animated tray icons

## Contributing

Contributions are always welcome!

See `Contributing.md` for ways to get started.

## Roadmap

- [ ] **Enhanced OCR Capabilities**
  - [ ] Support for handwritten text recognition
  - [ ] Table structure recognition and export to Excel/CSV
  - [ ] Chemical formula recognition
  - [ ] Multi-language support with language auto-detection

- [ ] **Support remote OCR endpoint (Mistral ...)**

- [ ] **Unified processing backend**

- [ ] **User Experience**
  - [ ] Interactive tutorial for new users
  - [ ] Customizable OCR region presets

- [ ] **Platform Support**
  - [ ] Windows support
  - [ ] Linux support


## Authors

- [@julienblanchon](https://x.com/JulienBlanchon)

## Related

This project is heavily inspired by the following commercial projects:

- [Mathpix](https://mathpix.com/)
- [TextSniper](https://textsniper.app/)

## Acknowledgements

 - [Tauri v2](https://v2.tauri.app/): A framework for building web based desktop apps using Rust.
 - [tauri-toolkit](https://github.com/ahkohd/tauri-toolkit): A tauri plugin toolkit for menubar apps.
 - [JacobBolda](https://www.youtube.com/@JacobBolda): A youtube channel with a lot of tauri content
 - [MrJakob](https://www.youtube.com/@MrJakob): A youtube channel with a lot of tauri content
 - [OCRS](https://github.com/robertknight/ocrs/tree/main): A lightweight OCR library project.
 - [mlx-nougat](https://github.com/mzbac/mlx-nougat): Nougat implementation for MLX.
 - [nougat](https://github.com/facebookresearch/nougat/): Facebook Nougat OCR.
 - [Fluent Icons](https://github.com/microsoft/fluentui-system-icons): A library of icons for Windows (use for the tray icon)
