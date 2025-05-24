<script lang="ts">
	import { ocrOcrPost } from '@/python/client/sdk.gen';
	import { fetch as tauriFetch } from '@tauri-apps/plugin-http';
	import { cubicOut, linear } from 'svelte/easing';
	import { slide } from 'svelte/transition';
	import { writeText } from '@tauri-apps/plugin-clipboard-manager';
	import { commands } from '@/tauri/bindings';
	import { userData } from '@/runes/user_database.svelte';
	import { userSettings } from '@/runes/user_settings.svelte';
	import type { Config } from '@/types';
	import Settings from '@/components/Settings.svelte';
	import { sendNotification } from '@tauri-apps/plugin-notification';
	import { convertFileSrc } from '@tauri-apps/api/core';
	import Main from '@/components/Main.svelte';
	import Header from '@/components/Header.svelte';
	import Autostart from '@/components/plugin/Autostart.svelte';
	import PlaySound from '@/components/plugin/PlaySound.svelte';
	import AutoCopyClipboard from '@/components/plugin/AutoCopyClipboard.svelte';
	import ShowMenuBarIcon from '@/components/plugin/ShowMenuBarIcon.svelte';
	import DisableHistory from '@/components/plugin/DisableHistory.svelte';
	import GlobalShortcut from '@/components/plugin/GlobalShortcut.svelte';
	import StartCleanUpShortcut from '@/components/plugin/StartCleanUpShortcut.svelte';
	import StartDatabase from '@/components/plugin/StartDatabase.svelte';
	import InitSystemSettings from '@/components/plugin/InitSystemSettings.svelte';
	import { animatedTray, askUserForConfig, runNougat, runOCR, requestScreenShot } from '@/actions';
	import DisableRightClickMenu from '@/components/plugin/DisableRightClickMenu.svelte';
	import { systemSettings } from '@/runes/system_settings.svelte';
	import InitTauriLog from '@/components/plugin/InitTauriLog.svelte';
	import { TrayIcon } from '@tauri-apps/api/tray';
	import { changeTrayWithEasing } from '@/tray';
	import SetupClient from '@/components/plugin/SetupClient.svelte';
	import ExecuteOnEscape from '@/components/plugin/ExecuteOnEscape.svelte';
	let search = $state('');
	let isProcessing: boolean = $state(false);
	let currentPage: 'main' | 'settings' = $state('main');

	async function runWithTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
		return await Promise.race([
			promise,
			new Promise<never>((_, reject) =>
				setTimeout(() => reject(new Error('Operation timed out')), timeoutMs)
			)
		]);
	}

	const DEFAULT_TIMEOUT = 60_000;

	async function takeScreenshot(config: Config): Promise<string | undefined> {
		isProcessing = true;
		const uuid = crypto.randomUUID();
		const filename = `${systemSettings.appDataDirPath}/${uuid}.png`;
		console.log('filename', filename);
		const start_time = performance.now();
		console.log('takeScreenshot', config);
		if (!userSettings.state.value.disableHistory) {
			userData.state.value = [
				{
					id: uuid,
					image: null,
					content: null,
					date: new Date(),
					duration: null,
					config: config
				},
				...userData.state.value
			];
		}

		try {
			await commands.closeMenubarPanel();

			const base64 = await requestScreenShot(filename, userSettings.state.value.playSound);
			userData.state.value = userData.state.value.map((item) =>
				item.id === uuid ? { ...item, image: convertFileSrc(filename) } : item
			);
			let text: string | undefined;
			if (config.type === 'nougat') {
				text = await runWithTimeout(
					ocrOcrPost({
						body: {
							filename: `file:///${filename}`,
							model: config.nougat_config.hf_model_name,
							temperature: config.nougat_config.temperature,
							top_p: config.nougat_config.top_p,
							repetition_penalty: config.nougat_config.repetition_penalty
						},
						baseUrl: 'http://localhost:7771',
						fetch: tauriFetch
					}).then((res) => res.data),
					DEFAULT_TIMEOUT
				);
			} else if (config.type === 'ocr') {
				text = await runWithTimeout(runOCR(config, filename), DEFAULT_TIMEOUT);
			} else if (config.type === 'llm_endpoint') {
				text = await runWithTimeout(
					fetch('http://localhost:7771/llm/ocr', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json'
						},
						body: JSON.stringify({
							filename: `file:///${filename}`,
							api_key: config.llm_config.api_key,
							model: config.llm_config.model,
							endpoint_url: config.llm_config.endpoint_url,
							max_tokens: config.llm_config.max_tokens,
							temperature: config.llm_config.temperature,
							prompt: config.llm_config.prompt
						})
					}).then((res) => res.text()),
					DEFAULT_TIMEOUT
				);
			} else {
				throw new Error('Invalid method');
			}

			if (!text) {
				throw new Error('No text found');
			}

			animatedTray();
			if (userSettings.state.value.showNotificationOnCapture) {
				sendNotification({ title: 'Montelimar', body: text });
			}
			if (userSettings.state.value.autoCopyToClipboard) {
				writeText(text);
			}

			const end_time = performance.now();
			const duration = end_time - start_time;

			if (!userSettings.state.value.disableHistory) {
				userData.state.value = userData.state.value.map((item) =>
					item.id === uuid ? { ...item, duration: duration, content: text } : item
				);
			}

			return text;
		} catch (error) {
			// sendNotification({
			// 	title: 'Montelimar',
			// 	body: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
			// });
			// Remove the screenshot from the user data
			userData.state.value = userData.state.value.filter((item) => item.id !== uuid);
			console.error(error);
		} finally {
			isProcessing = false;
			// await commands.showMenubarPanel();
		}
	}

	let configSpecificShortcutConfigPair = $derived.by(() => {
		return userSettings.state.value.configs.map((config) => {
			return {
				config: config,
				shortcut: config.shortcutKey
			};
		});
	});
</script>

<InitSystemSettings />
<StartDatabase />
<InitTauriLog enabled={true} />
<!-- <SQLiteMigration /> -->
<SetupClient />
<DisableRightClickMenu />

<StartCleanUpShortcut />
<Autostart bind:autostart={userSettings.state.value.startAtLogin} />
<PlaySound bind:playSound={userSettings.state.value.playSound} />
<AutoCopyClipboard bind:autoCopyClipboard={userSettings.state.value.autoCopyToClipboard} />
<ShowMenuBarIcon bind:showMenuBarIcon={userSettings.state.value.showMenuBarIcon} />
<DisableHistory bind:disableHistory={userSettings.state.value.disableHistory} />
<GlobalShortcut
	bind:globalShortcut={userSettings.state.value.globalShortcut}
	callback={async () => {
		const config = await askUserForConfig();
		await takeScreenshot(config);
	}}
/>

{#each configSpecificShortcutConfigPair as pair}
	<GlobalShortcut
		globalShortcut={pair.shortcut}
		callback={async () => {
			await takeScreenshot(pair.config);
		}}
	/>
{/each}

<div class="mb-[10px] mt-[10px] h-[680px] w-[500px] overflow-hidden rounded-lg">
	<Header
		callback={async () => {
			const config = await askUserForConfig();
			const text = await takeScreenshot(config);
			return text;
		}}
		bind:isProcessing
		bind:currentPage
		bind:search
	/>

	{#if currentPage === 'main'}
		<div class="h-[640px] w-full overflow-hidden bg-transparent">
			<Main {search} />
		</div>
	{:else}
		<div
			in:slide={{ duration: 200, easing: cubicOut, axis: 'y' }}
			out:slide={{ duration: 200, delay: 200, easing: cubicOut, axis: 'y' }}
			class="h-[640px] w-full overflow-hidden bg-transparent"
		>
			<Settings />
		</div>
	{/if}
</div>

<ExecuteOnEscape
	callback={() => {
		commands.hideMenubarPanel();
	}}
/>
