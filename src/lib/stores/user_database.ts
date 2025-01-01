import { type UserDatabase } from '@/types';
import { Store } from 'tauri-plugin-svelte';

export const userData = new Store<{ value: UserDatabase[] }>('database',
    {
        value: [
            {
                id: '1',
                image:
                    'https://media0.giphy.com/media/yIxNOXEMpqkqA/200.gif?cid=6c09b952kzal3cdi3dwlbrr9bn50fu2xa2gus9l3sqcw0xpa&ep=v1_gifs_search&rid=200.gif&ct=g',
                content: 'Bla',
                date: new Date(),
                duration: 100,
                config: {
                    name: 'nougat-large',
                    type: 'nougat' as const,
                    nougat_config: {
                        hf_model_name: 'nougat-large',
                        temperature: 0.7,
                        top_p: 0.9,
                        repetition_penalty: 1.1,
                    },
                    shortcutKey: null,
                    color: '#0000FF',
                    id: 1
                }
            },
            {
                id: '2',
                image:
                    'https://segmentation-test-palaz.s3.eu-north-1.amazonaws.com/rooms/13437982-7a0b-40a2-80a5-a815bdd397f4/irradiance.png',
                content: 'Hello Here 2',
                date: new Date(),
                duration: 100,
                config: {
                    name: 'nougat-large',
                    type: 'nougat',
                    nougat_config: {
                        hf_model_name: 'nougat-large',
                        temperature: 0.7,
                        top_p: 0.9,
                        repetition_penalty: 1.1,
                    },
                    color: '#0000FF',
                    shortcutKey: null,
                    id: 2
                }
            },
            {
                id: '3',
                image:
                    'https://media0.giphy.com/media/yIxNOXEMpqkqA/200.gif?cid=6c09b952kzal3cdi3dwlbrr9bn50fu2xa2gus9l3sqcw0xpa&ep=v1_gifs_search&rid=200.gif&ct=g',
                content: 'IUdisuhidsu',
                date: new Date(),
                duration: 100,
                config: {
                    name: 'nougat-large',
                    type: 'nougat',
                    nougat_config: {
                        hf_model_name: 'nougat-large',
                        temperature: 0.7,
                        top_p: 0.9,
                        repetition_penalty: 1.1,
                    },
                    shortcutKey: null,
                    color: '#0000FF',
                    id: 3
                }
            },
            {
                id: '4',
                image: '',
                content: '',
                date: new Date(),
                duration: 100,
                config: {
                    name: 'ocr',
                    type: 'ocr',
                    ocr_config: {
                        detection_model_url: 'https://ocrs-models.s3-accelerate.amazonaws.com/text-detection.rten',
                        recognition_model_url: 'https://ocrs-models.s3-accelerate.amazonaws.com/text-recognition.rten',
                        disableLineBreaks: true,
                    },
                    shortcutKey: null,
                    color: '#0000FF',
                    id: 4
                }
            }
        ]
    },
    {
        saveOnChange: true,
        saveStrategy: 'debounce',
        saveInterval: 10,

    }
);