import { Store } from "tauri-plugin-svelte";
import type { Settings } from "@/types";

export const userSettings = new Store<{ value: Settings }>('settings', {
    value: {
        configs: [
            {
                name: 'nougat-large',
                id: 1,
                shortcutKey: null,
                type: 'nougat',
                nougat_config: {
                    hf_model_name: 'nougat-large',
                    temperature: 0.7,
                    top_p: 0.9,
                    repetition_penalty: 1.1,
                },
                color: '#0000FF',
            },
            {
                name: 'nougat-small',
                id: 2,
                shortcutKey: null,
                type: 'nougat',
                nougat_config: {
                    hf_model_name: 'nougat-small',
                    temperature: 0.7,
                    top_p: 0.9,
                    repetition_penalty: 1.1,
                },
                color: '#FF0000',
            },
            {
                name: 'ocr',
                id: 3,
                shortcutKey: null,
                type: 'ocr',
                ocr_config: {
                    detection_model_url: 'https://ocrs-models.s3-accelerate.amazonaws.com/text-detection.rten',
                    recognition_model_url: 'https://ocrs-models.s3-accelerate.amazonaws.com/text-recognition.rten',
                    disableLineBreaks: true,
                },
                color: '#0000FF',
            }
        ],
        startAtLogin: false,
        playSound: true,
        autoCopyToClipboard: true,
        showMenuBarIcon: true,
        globalShortcut: null,
        disableHistory: false,
        showNotificationOnCapture: true,
    }
},
    {
        saveOnChange: true,
        saveStrategy: 'debounce',
        saveInterval: 1000,

    }
);
