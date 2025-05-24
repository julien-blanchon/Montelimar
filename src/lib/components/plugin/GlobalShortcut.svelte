<script lang="ts">
	import type { ShortcutKey } from '@/types';
	import { isRegistered, register, unregister } from '@tauri-apps/plugin-global-shortcut';
	import { recordingState } from '@/runes/recordingState.svelte';

	interface Props {
		globalShortcut: ShortcutKey | null;
		callback: () => Promise<void>;
	}

	let { globalShortcut = $bindable(), callback = $bindable() }: Props = $props();

	const registrationDatabase: Record<string, boolean> = {};

	$effect(() => {
		async function setGlobalShortcut() {
			if (globalShortcut) {
				// Unregister all shortcuts before registering a new one
				for (const shortcut in registrationDatabase) {
					await unregister(shortcut);
					delete registrationDatabase[shortcut];
				}

				// Convert the shortcut in the tauri format
				const shortcut =
					globalShortcut.modifiers?.join('+') + '+' + globalShortcut.primaryKey.toUpperCase();

				const isShortkeyAlreadyRegistered = await isRegistered(shortcut);

				if (!isShortkeyAlreadyRegistered) {
					await register(shortcut, (event) => {
						if (event.state === 'Pressed') {
							console.log('Shortcut triggered', event);
							if (recordingState.isRecording) {
								recordingState.isRecording = false;
								return;
							}
							callback();
						}
					});
					registrationDatabase[shortcut] = true;
				}
			} else {
				// Unregister all shortcuts
				for (const shortcut in registrationDatabase) {
					await unregister(shortcut);
					delete registrationDatabase[shortcut];
				}
			}
		}
		setGlobalShortcut();

		return () => {
			for (const shortcut in registrationDatabase) {
				unregister(shortcut);
				console.log('unmount, unregister', shortcut);
				delete registrationDatabase[shortcut];
			}
		};
	});
</script>
