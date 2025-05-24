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
    Escape: '⎋',
    Space: '␣'
} as const;

// Map of key codes to their display names
const KEY_DISPLAY_MAP: Record<string, string> = {
    ' ': 'Space',
    'ArrowUp': '↑',
    'ArrowDown': '↓',
    'ArrowLeft': '←',
    'ArrowRight': '→',
    'Enter': '↩',
    'Backspace': '⌫',
    'Delete': '⌦',
    'Tab': '⇥',
    'Escape': '⎋',
    'CapsLock': 'Caps Lock',
    'PageUp': 'Page Up',
    'PageDown': 'Page Down',
    'Home': 'Home',
    'End': 'End',
    'Insert': 'Insert',
    'PrintScreen': 'Print Screen',
    'ScrollLock': 'Scroll Lock',
    'Pause': 'Pause',
    'ContextMenu': 'Menu'
};

// Function keys
for (let i = 1; i <= 12; i++) {
    KEY_DISPLAY_MAP[`F${i}`] = `F${i}`;
}

// Numpad keys
for (let i = 0; i <= 9; i++) {
    KEY_DISPLAY_MAP[`Numpad${i}`] = `Num ${i}`;
}

export function formatKey(key: string): string {
    if (key in MAC_SYMBOLS) {
        return MAC_SYMBOLS[key as keyof typeof MAC_SYMBOLS];
    }
    
    if (key in KEY_DISPLAY_MAP) {
        return KEY_DISPLAY_MAP[key];
    }
    
    // For single characters, return uppercase
    if (key.length === 1) {
        return key.toUpperCase();
    }
    
    return key;
}

export function formatShortcut(shortcut: ShortcutKey | null): string {
    if (!shortcut) return '';
    const SEPARATOR = '+';
    return [...(shortcut.modifiers || []).map(formatKey), formatKey(shortcut.primaryKey)].join(SEPARATOR);
}

export function formatRealTimeShortcut(modifiers: Set<string>, currentKey: string | null): string {
    if (!currentKey && modifiers.size === 0) return '';
    
    const SEPARATOR = '+';
    const modifierArray = Array.from(modifiers).sort((a, b) => {
        // Sort modifiers in a consistent order
        const order = ['Ctrl', 'Alt', 'Shift', 'Super'];
        return order.indexOf(a) - order.indexOf(b);
    });
    
    const parts = modifierArray.map(formatKey);
    if (currentKey) {
        parts.push(formatKey(currentKey));
    }
    
    return parts.join(SEPARATOR);
}

// Get the actual key without modifier interference
export function getActualKey(event: KeyboardEvent): string {
    // Use event.code for physical key position, but fall back to event.key for special keys
    const code = event.code;
    
    // Handle special keys that don't have a code or need special handling
    if (event.key === 'Enter' || event.key === 'Escape' || event.key === 'Tab' || 
        event.key === 'Backspace' || event.key === 'Delete' || event.key === ' ' ||
        event.key.startsWith('Arrow') || event.key.startsWith('F') ||
        event.key === 'Home' || event.key === 'End' || event.key === 'PageUp' || 
        event.key === 'PageDown' || event.key === 'Insert') {
        return event.key;
    }
    
    // For letter keys, extract the letter from the code
    if (code.startsWith('Key')) {
        return code.slice(3); // Remove 'Key' prefix, e.g., 'KeyA' -> 'A'
    }
    
    // For digit keys
    if (code.startsWith('Digit')) {
        return code.slice(5); // Remove 'Digit' prefix, e.g., 'Digit1' -> '1'
    }
    
    // For numpad keys
    if (code.startsWith('Numpad')) {
        return code; // Keep as is, e.g., 'Numpad1'
    }
    
    // For other keys, use the key value but handle special cases
    switch (code) {
        case 'Minus': return '-';
        case 'Equal': return '=';
        case 'BracketLeft': return '[';
        case 'BracketRight': return ']';
        case 'Backslash': return '\\';
        case 'Semicolon': return ';';
        case 'Quote': return "'";
        case 'Comma': return ',';
        case 'Period': return '.';
        case 'Slash': return '/';
        case 'Backquote': return '`';
        default: return event.key;
    }
} 