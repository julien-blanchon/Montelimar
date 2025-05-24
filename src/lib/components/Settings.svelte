<script lang="ts">
	import { attachLogger } from '@tauri-apps/plugin-log';
	import type { ConfigNougat, ConfigOCR, ConfigLLMEndpoint } from '@/types';
	import { getVersion } from '@tauri-apps/api/app';
	import { userSettings } from '@/runes/user_settings.svelte';
	import { systemSettings } from '@/runes/system_settings.svelte';
	import { requestPermission } from '@tauri-apps/plugin-notification';
	import { onMount } from 'svelte';

	// Import components
	import ModelsList from './settings/ModelsList.svelte';
	import GeneralSettings from './settings/GeneralSettings.svelte';
	import AboutSection from './settings/AboutSection.svelte';
	import LogViewer from './settings/LogViewer.svelte';

	let logs: string[] = $state([]);

	onMount(() => {
		let unlistenPromise = attachLogger(({ level, message }) => {
			logs = [...logs, `[${level}] ${message}`];
			if (logs.length > 500) logs = logs.slice(-500);
		});

		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});
</script>

<div class="h-[640px] w-full space-y-6 overflow-scroll px-4 py-2">
	<ModelsList />
	<GeneralSettings />
	<AboutSection />
	<LogViewer {logs} />
</div>

<style>
	:global(*:focus) {
		outline: none;
	}
</style>
