import { once } from "@tauri-apps/api/event";
import { commands } from "./tauri/bindings";
import type { Config, ConfigNougat, ConfigOCR } from "./types";
import { Command } from "@tauri-apps/plugin-shell";
import { BaseDirectory, readFile } from "@tauri-apps/plugin-fs";
import { TrayIcon } from "@tauri-apps/api/tray";
import { changeTrayWithEasing } from "./tray";
import { linear } from "svelte/easing";

function arrayBufferToBase64(img: Uint8Array) {
    return btoa(new Uint8Array(img).reduce((data, byte) => data + String.fromCharCode(byte), ''));
}


export async function askUserForConfig(): Promise<Config> {
    try {
        // Show the spotlight panel
        await commands.showSpotlightPanel();

        // Listen for the 'config-selected' event once
        const selectedConfig = await new Promise((resolve, reject) => {
            once('config-selected', (event) => {
                if (event && event.payload) {
                    resolve(event.payload); // Resolve with the selected configuration
                } else {
                    reject(new Error('No configuration selected.'));
                }
            }).catch(reject);
        });

        // Hide the spotlight panel after receiving the selection
        await commands.hideSpotlightPanel();

        return selectedConfig as Config;
    } catch (error) {
        // Hide the spotlight in case of an error as well
        await commands.hideSpotlightPanel();
        throw error;
    }
}

export async function requestScreenShot(filename: string, playSound: boolean): Promise<string> {
    const args = ['-i', '-r', '-t', 'png', filename];
    if (!playSound) {
        args.unshift('-x');
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { code: exitCode } = await Command.create('/usr/sbin/screencapture', args).execute();
    
    // if (exitCode !== 0) {
    //     throw new Error('Failed to take screenshot');
    // }

    const contents = await readFile(filename, {
        baseDir: BaseDirectory.AppData
    });
    const base64 = arrayBufferToBase64(contents);
    return base64;
}

export async function runNougat(config: ConfigNougat, filename: string): Promise<string> {
    const response = await fetch('http://127.0.0.1:7771/ocr', {
        method: 'POST',
        headers: {
            accept: 'text/plain',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filename: `file://${filename}`,
            model: config.nougat_config.hf_model_name,
            temperature: config.nougat_config.temperature,
            top_p: config.nougat_config.top_p,
            repetition_penalty: config.nougat_config.repetition_penalty
        })
    });
    return await response.text();
}

export async function runOCR(config: ConfigOCR, image_path: string): Promise<string> {
    console.log(config);
    const response = await commands.performOcr(
        image_path,
        config.ocr_config.detection_model_url,
        config.ocr_config.recognition_model_url,
        config.ocr_config.alphabet || null,
        config.ocr_config.allowed_chars || null
    );
    if (response.status !== 'ok') {
        throw new Error('Failed to perform OCR');
    }

    if (config.ocr_config.disableLineBreaks) {
        return response.data.replace(/\n/g, ' ');
    }

    return response.data;
}

export async function animatedTray() {
    const tray = await TrayIcon.getById('tray');
    if (tray) {
        await changeTrayWithEasing(8, 300, linear, (frameIndex) => {
            tray.setIcon(`icons/frames/${frameIndex.toString().padStart(2, '0')}_tray.png`);
            tray.setIconAsTemplate(true);
        });
        await tray.setIcon(`icons/tray.png`);
        await tray.setIconAsTemplate(true);
    }
}
