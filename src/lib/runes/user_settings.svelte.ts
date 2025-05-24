import { RuneStore } from '@tauri-store/svelte';
import type { Settings } from "@/types";

const DEFAULT_CONFIG: Settings = {
    "autoCopyToClipboard": true,
    "configs": [
        {
            "color": "#3357FF",
            "id": 9,
            "llm_config": {
                "api_key": "sk-...",
                "endpoint_url": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 1000,
                "model": "gpt-4.1-mini",
                "prompt": "You are an OCR model.\nI will give you an image of a document, sign, or printed text.\nYour task is to extract the visible text exactly as it appears in the image.\n- Preserve line breaks and formatting where possible.\n- Do not add or remove any words.\n- Output text only — no explanations, no commentary.\nHere is the image:\n\t",
                "temperature": 0
            },
            "name": "GPT4.1 mini Text",
            "shortcutKey": null,
            "type": "llm_endpoint"
        },
        {
            "color": "#ff4013",
            "id": 8,
            "llm_config": {
                "api_key": "sk-...",
                "endpoint_url": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 1000,
                "model": "gpt-4.1-mini",
                "prompt": "You are a front-end developer.\nI will show you an image of a user interface component (e.g., a button, card, form, navbar, etc.).\nYour task is to generate the equivalent HTML code styled with Tailwind CSS classes.\n- Use semantic HTML where appropriate.\n- Use Tailwind utility classes only (no custom CSS).\nYour output should be a single HTML snippet.\n- Do not include explanations or markdown formatting. Just return the raw HTML.\nHere is the image:",
                "temperature": 0
            },
            "name": "GPT4.1 mini WebUI",
            "shortcutKey": null,
            "type": "llm_endpoint"
        },
        {
            "color": "#d29d00",
            "id": 4,
            "llm_config": {
                "api_key": "sk-...",
                "endpoint_url": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 1000,
                "model": "gpt-4.1-mini",
                "prompt": "You are an OCR model specialized in converting images of mathematical expressions into LaTeX.\n\nI will give you an image containing a single math expression or equation. Your task is to output only the corresponding LaTeX code, wrapped in double dollar signs $$...$$ for display math.\n- Do not include any explanations.\n- Do not add any extra symbols.\n- Output LaTeX only.\n\nHere is the image:",
                "temperature": 0
            },
            "name": "GPT4.1 mini LaTex",
            "shortcutKey": null,
            "type": "llm_endpoint"
        },
        {
            "color": "#3357FF",
            "id": 7,
            "llm_config": {
                "api_key": "",
                "endpoint_url": "http://localhost:1234/v1/chat/completions",
                "max_tokens": 1000,
                "model": "smolvlm-500m-instruct@8bit",
                "prompt": "You are a front-end developer.\nI will show you an image of a user interface component (e.g., a button, card, form, navbar, etc.).\nYour task is to generate the equivalent HTML code styled with Tailwind CSS classes.\n- Use semantic HTML where appropriate.\n- Use Tailwind utility classes only (no custom CSS).\nYour output should be a single HTML snippet.\n- Do not include explanations or markdown formatting. Just return the raw HTML.\nHere is the image:",
                "temperature": 0
            },
            "name": "SmolVLM 500m WebUI",
            "shortcutKey": null,
            "type": "llm_endpoint"
        },
        {
            "color": "#9B33FF",
            "id": 6,
            "llm_config": {
                "api_key": "",
                "endpoint_url": "http://localhost:1234/v1/chat/completions",
                "max_tokens": 1000,
                "model": "smolvlm-500m-instruct@8bit",
                "prompt": "You are an OCR model.\nI will give you an image of a document, sign, or printed text.\nYour task is to extract the visible text exactly as it appears in the image.\n- Preserve line breaks and formatting where possible.\n- Do not add or remove any words.\n- Output text only — no explanations, no commentary.\nHere is the image:",
                "temperature": 0
            },
            "name": "SmolVLM 500m Text",
            "shortcutKey": null,
            "type": "llm_endpoint"
        },
        {
            "color": "#77bb41",
            "id": 5,
            "llm_config": {
                "api_key": "",
                "endpoint_url": "http://localhost:1234/v1/chat/completions",
                "max_tokens": 1000,
                "model": "smolvlm-500m-instruct@8bit",
                "prompt": "You are an OCR model specialized in converting images of mathematical expressions into LaTeX.\n\nI will give you an image containing a single math expression or equation. Your task is to output only the corresponding LaTeX code, wrapped in double dollar signs $$...$$ for display math.\n- Do not include any explanations.\n- Do not add any extra symbols.\n- Output LaTeX only.\n\nHere is the image:",
                "temperature": 0
            },
            "name": "SmolVLM 500m LaTeX",
            "shortcutKey": null,
            "type": "llm_endpoint"
        },
        {
            "color": "#e63b7a",
            "id": 1,
            "name": "OCRS",
            "ocr_config": {
                "detection_model_url": "https://ocrs-models.s3-accelerate.amazonaws.com/text-detection.rten",
                "disableLineBreaks": true,
                "recognition_model_url": "https://ocrs-models.s3-accelerate.amazonaws.com/text-recognition.rten"
            },
            "shortcutKey": null,
            "type": "ocr"
        },
        {
            "color": "#F28B82",
            "id": 3,
            "name": "Nougat Base",
            "nougat_config": {
                "hf_model_name": "facebook/nougat-base",
                "repetition_penalty": 1,
                "temperature": 0,
                "top_p": 0
            },
            "shortcutKey": null,
            "type": "nougat"
        },
        {
            "color": "#3a88fe",
            "id": 2,
            "name": "Nougat Small",
            "nougat_config": {
                "hf_model_name": "facebook/nougat-small",
                "repetition_penalty": 1,
                "temperature": 0,
                "top_p": 0
            },
            "shortcutKey": null,
            "type": "nougat"
        }
    ],
    "disableHistory": false,
    "globalShortcut": {
        "modifiers": [
            "Ctrl"
        ],
        "primaryKey": "t"
    },
    "playSound": true,
    "showMenuBarIcon": true,
    "showNotificationOnCapture": true,
    "startAtLogin": false
}

export const userSettings = new RuneStore<{ value: Settings }>('settings', {
    value: DEFAULT_CONFIG
},
    {
        saveOnChange: true,
        saveStrategy: 'debounce',
        saveInterval: 1000,

    }
);
