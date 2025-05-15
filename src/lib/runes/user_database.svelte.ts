import { type UserDatabase } from '@/types';
import { RuneStore } from '@tauri-store/svelte';

export const userData = new RuneStore<{ value: UserDatabase[] }>('database',
    {
        value: []
    },
    {
        saveOnChange: true,
        saveStrategy: 'debounce',
        saveInterval: 10,

    }
);