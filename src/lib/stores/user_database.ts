import { type UserDatabase } from '@/types';
import { Store } from 'tauri-plugin-svelte';

export const userData = new Store<{ value: UserDatabase[] }>('database',
    {
        value: []
    },
    {
        saveOnChange: true,
        saveStrategy: 'debounce',
        saveInterval: 10,

    }
);