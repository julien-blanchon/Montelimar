// Define valid modifier keys
export type ModifierKey = 'Ctrl' | 'Alt' | 'Shift' | 'Super';

// Define valid primary keys (expandable as needed)
export type PrimaryKey = string; // Or more specific keys like 'A' | 'B' | 'C' | '1' | '2' ...

// Define the structure of a shortcut key binding
export interface ShortcutKey {
    modifiers?: ModifierKey[];
    primaryKey: PrimaryKey;
}


interface NougatInputConfig {
    hf_model_name: string;
    temperature: number;
    top_p: number;
    repetition_penalty: number;
}

interface OCRInputConfig {
    detection_model_url: string;
    recognition_model_url: string;
    disableLineBreaks: boolean;
    alphabet?: string | null;
    allowed_chars?: string | null;
}

export interface ConfigNougat {
    name: string;
    id: number;
    shortcutKey: ShortcutKey | null;
    type: 'nougat';
    nougat_config: NougatInputConfig;
    color: string;
}

export interface ConfigOCR {
    name: string;
    id: number;
    shortcutKey: ShortcutKey | null;
    type: 'ocr';
    ocr_config: OCRInputConfig;
    color: string;
}

export type Config = ConfigNougat | ConfigOCR;


export interface Settings {
    configs: Config[];
    startAtLogin: boolean;
    playSound: boolean;
    autoCopyToClipboard: boolean;
    globalShortcut: ShortcutKey | null;
    showMenuBarIcon: boolean;
    disableHistory: boolean;
    showNotificationOnCapture: boolean;
}


// ...

export interface UserDatabase {
    id: string;
    date: Date;
    image: string | null;
    content: string | null;
    duration: number | null;
    config: Config;
}

// ...
export interface SystemSettings {
    notificationPermissionGranted: boolean;
    appDataDirPath: string;
}