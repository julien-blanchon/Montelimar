<script lang="ts">
	import { systemSettings } from '@/runes/system_settings.svelte';
	import { isPermissionGranted } from '@tauri-apps/plugin-notification';
	import { appDataDir } from '@tauri-apps/api/path';
	import { commands } from '@/tauri/bindings';

	$effect(() => {
		async function initMenubar() {
			await commands.initMenubar();
			console.log('initMenubar');
		}

		async function initSystemSettings() {
			systemSettings.notificationPermissionGranted = await isPermissionGranted();
		}
		async function initAppDataDirPath() {
			const appDataDirPath = await appDataDir();
			systemSettings.appDataDirPath = appDataDirPath;
		}

		console.log('initSystemSettings');

		initMenubar();
		initSystemSettings();
		initAppDataDirPath();
	});
</script>
