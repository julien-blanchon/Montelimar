# ocr_mlx — Nougat OCR Python Sidecar

**MLX package for support of the Nougat OCR model.**  
Provides a FastAPI-based HTTP endpoint and CLI for high-performance OCR using Facebook's Nougat models, with support for local, remote, and base64-encoded images.

---

## Features

- **HTTP API**: FastAPI server for OCR requests (image/PDF to text).
- **CLI**: Command-line interface for batch or scripted OCR.
- **Model Caching**: Efficient in-memory model cache with auto-reset.
- **Flexible Input**: Accepts file paths, URLs, and base64-encoded images.
- **Configurable**: Supports model selection and decoding parameters.
- **Health Check**: `/health` endpoint for liveness/readiness probes.

---

## Requirements

- Python 3.12+
- MLX (`mlx`), FastAPI, HuggingFace Transformers, Pillow, Typer, APScheduler, and other dependencies (see [pyproject.toml](./pyproject.toml)).

Install dependencies (recommended: use a virtual environment):

```bash
cd src-python
uv venv
source .venv/bin/activate
uv sync
```

---

## Usage

### 1. HTTP API

Start the server:

```bash
python -m ocr_mlx.endpoint
# or, if installed as a script:
ocr_mlx
```

The server will auto-select a free port (default: 127.0.0.1:7771).

#### Endpoints

- **POST `/ocr`**  
  Perform OCR on an image or PDF.

  **Request (application/json):**
  ```json
  {
    "filename": "file:///path/to/image.png",
    "model": "facebook/nougat-small",
    "temperature": 0.0,
    "top_p": 0.0,
    "repetition_penalty": null
  }
  ```
  - `filename`: File path (`file://`), URL (`http(s)://`), or base64 data URI (`data:image/png;base64,...`)
  - `model`: Model name or path (default: `facebook/nougat-small`)
  - `temperature`, `top_p`, `repetition_penalty`: Decoding parameters

  **Response (text/plain):**
  ```
  <recognized text>
  ```

- **GET `/health`**  
  Returns `"OK!!!"` if the service is running.

#### Example (using `curl`):

```bash
curl -X POST http://127.0.0.1:7771/ocr \
  -H "Content-Type: application/json" \
  -d '{"filename":"file:///path/to/image.png"}'
```

### 2. Command-Line Interface

Run OCR from the command line:

```bash
python -m ocr_mlx.cli --input file:///path/to/image.png --model facebook/nougat-small
```

**Options:**
- `--input`: Path/URL to image, could be a base64
- `--model`: Model name or path (default: `facebook/nougat-small`)
- `--output`: Output file for recognized text
- `--temperature`, `--top_p`, `--repetition_penalty`: Decoding parameters

---

## Project Structure

```
src-python/
  ├── pyproject.toml         # Project metadata and dependencies
  ├── openapi.json           # OpenAPI schema for the HTTP API
  ├── src/
  │   └── ocr_mlx/
  │        ├── endpoint.py   # FastAPI server (main entry point)
  │        ├── cli.py        # Command-line interface
  │        ├── model/        # Model definitions
  │        ├── inference/    # Inference logic
  │        ├── quantize/     # Quantization utilities
  │        └── utils/        # Helper functions (e.g., image loading)
  └── README.md              # (You are here)
```

---

## Development

- **Model cache**: Automatically resets after 10 seconds of inactivity.
- **API docs**: OpenAPI schema available at `/openapi.json` (see `openapi.json`).
- **Packaging**: Uses [hatch](https://hatch.pypa.io/) for builds; see `pyproject.toml`.
- **Dev dependencies**: See `[dependency-groups]` in `pyproject.toml`.

---

## References

- [Nougat Model (Facebook)](https://huggingface.co/facebook/nougat-small)
- [MLX](https://github.com/ml-explore/mlx)
- [FastAPI](https://fastapi.tiangolo.com/)

---
