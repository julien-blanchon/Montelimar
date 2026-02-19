# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Montélimar is a macOS menubar OCR application that captures screen regions and extracts text/LaTeX. It uses a three-tier architecture: Svelte 5 frontend, Rust/Tauri backend, and a Python ML sidecar process.

## Build & Development Commands

**Prerequisites:** Bun, uv, Rust toolchain

```bash
# Install JS dependencies
bun install

# Python sidecar setup (first time)
cd src-python && uv venv && source .venv/bin/activate && uv sync

# Build Python sidecar binary
bun run python:package:build && bun run python:package:reset

# Full development mode (Svelte + Tauri + Python sidecar)
bun run tauri dev

# Run only the Python sidecar standalone
bun run python:package:dev

# Production build (auto-checks if Python sidecar rebuild needed)
bun run tauri build

# Type checking
bun run check

# Lint (Prettier + ESLint)
bun run lint

# Auto-format
bun run format
```

**Code generation (after changing Python API or Rust commands):**
```bash
bun run python:package:generate-openapi    # Python FastAPI → OpenAPI spec
bun run python:package:generate-client     # OpenAPI spec → TypeScript client
```

**Database (Drizzle ORM + SQLite):**
```bash
bun run db:generate    # Generate migrations from schema changes
bun run db:studio      # Open Drizzle Studio UI
```

## Architecture

### Three-Tier System

1. **Frontend (`src/`)** — Svelte 5 + SvelteKit with static adapter
   - Two UI windows: `/routes/menubar/` (persistent tray panel) and `/routes/spotlight/` (overlay for model selection)
   - State management via Svelte Runes in `.svelte.ts` files using class-based state machines
   - Styling: Tailwind CSS + DaisyUI
   - Database: Drizzle ORM over SQLite via `@tauri-apps/plugin-sql`
   - Schema: `Models`, `Images`, `OCRResults` tables in `src/lib/db/schema.ts`

2. **Backend (`src-tauri/`)** — Rust + Tauri 2 (rc)
   - `src/commands/` — Tauri IPC command handlers (screenshot, ocr, nougat, menubar, spotlight)
   - `src/app/menubar/` & `src/app/spotlight/` — Window creation and management (uses macOS private APIs via `cocoa`/`objc` crates)
   - `src/model/ocr/` — Local OCR using the `ocrs` crate (lightweight, runs in Rust)
   - `src/state/` — Shared application state
   - TypeScript bindings auto-generated from Rust via `tauri-specta`

3. **Python ML Service (`src-python/`)** — FastAPI sidecar (`ocr_mlx` package)
   - Runs as a separate HTTP process on localhost (port 7771 default, auto-finds available port)
   - ML models: Nougat (LaTeX OCR), Donut (vision transformer), mBart (translation) — all MLX-optimized for Apple Silicon
   - Endpoints: `/ocr`, `/llm/ocr`, `/health`, `/shutdown`
   - Packaged into a standalone binary via `box-packager` (PyApp bootstrap), placed in `src-tauri/binaries/`

### Communication Flow

Frontend ←(Tauri IPC)→ Rust backend ←(spawns sidecar)→ Python ML service
Frontend ←(HTTP via `@tauri-apps/plugin-http`)→ Python ML service (for OCR requests)

### Key Patterns

- **Sidecar lifecycle:** Tauri manages spawning/killing the Python process; the Python service has `/shutdown` for graceful termination and APScheduler for model cache cleanup
- **Dual OCR paths:** Fast local OCR via Rust `ocrs` crate, and ML-powered OCR (LaTeX/Nougat) via Python sidecar
- **Capability-based security:** Tauri capabilities JSON files in `src-tauri/capabilities/` define which APIs each window can access
- **API contract:** Python Pydantic models → OpenAPI spec → auto-generated TypeScript client in `src/lib/python/client/`
- **Database migrations:** Defined in `src-tauri/migrations/`, executed at runtime by the Tauri SQL plugin

## Code Conventions

- **Svelte:** Use Runes (`$state`, `$derived`, `$effect`, `$props`); component files are lowercase-hyphenated; `.svelte.ts` files for logic/state machines
- **TypeScript:** Strict mode; prefer interfaces over types; avoid enums (use const objects)
- **Rust:** Standard conventions; async with Tokio; error handling via `thiserror`/`anyhow`
- **Python:** PEP 8; functional style; `snake_case`; uses MLX (not PyTorch/JAX) for Apple Silicon acceleration
- **macOS only** currently — uses private Tauri APIs and native macOS integrations (NSPanel, window vibrancy, tray icons)
