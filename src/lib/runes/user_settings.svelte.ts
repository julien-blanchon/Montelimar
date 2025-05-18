import { RuneStore } from '@tauri-store/svelte';
import type { Settings } from "@/types";

export const userSettings = new RuneStore<{ value: Settings }>('settings', {
    value: {
        configs: [
            {
                name: 'ocsr',
                id: 1,
                shortcutKey: null,
                type: 'ocr',
                ocr_config: {
                    detection_model_url: 'https://ocrs-models.s3-accelerate.amazonaws.com/text-detection.rten',
                    recognition_model_url: 'https://ocrs-models.s3-accelerate.amazonaws.com/text-recognition.rten',
                    disableLineBreaks: true,
                },
                color: '#FFF475',
            },
            {
                name: 'Nougat Base',
                id: 3,
                shortcutKey: null,
                type: 'nougat',
                nougat_config: {
                    hf_model_name: 'facebook/nougat-base',
                    temperature: 0,
                    top_p: 0,
                    repetition_penalty: 1,
                },
                color: '#F28B82',
            },
            {
                name: 'Nougat Small',
                id: 2,
                shortcutKey: null,
                type: 'nougat',
                nougat_config: {
                    hf_model_name: 'facebook/nougat-small',
                    temperature: 0,
                    top_p: 0,
                    repetition_penalty: 1,
                },
                color: '#AECBFA',
            },  
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
