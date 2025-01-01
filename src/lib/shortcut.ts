import type { ShortcutKey } from '@/types';

const MAC_SYMBOLS = {
    Ctrl: '⌃',
    Alt: '⌥',
    Meta: '⌘',
    Super: '⌘',
    Shift: '⇧',
    Enter: '↩',
    Backspace: '⌫',
    Delete: '⌦',
    ArrowUp: '↑',
    ArrowDown: '↓',
    ArrowLeft: '←',
    ArrowRight: '→',
    Tab: '⇥',
    Escape: '⎋'
} as const;

export function formatKey(key: string): string {
    if (key in MAC_SYMBOLS) {
        return MAC_SYMBOLS[key as keyof typeof MAC_SYMBOLS];
    }
    return key.toUpperCase();
}

export function formatShortcut(shortcut: ShortcutKey | null): string {
    if (!shortcut) return '';
    const SEPARATOR = '+';
    return [...(shortcut.modifiers || []).map(formatKey), formatKey(shortcut.primaryKey)].join(SEPARATOR);
} 