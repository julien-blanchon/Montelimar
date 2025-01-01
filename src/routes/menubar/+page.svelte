<script lang="ts">
	import { cubicOut, linear } from 'svelte/easing';
	import { slide } from 'svelte/transition';
	import { writeText } from '@tauri-apps/plugin-clipboard-manager';
	import { commands } from '@/tauri/bindings';
	import { userData } from '@/stores/user_database';
	import { userSettings } from '@/stores/user_settings';
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
	// import ExecuteOnEscape from '@/components/plugin/ExecuteOnEscape.svelte';
	import { systemSettings } from '@/runes/system_settings.svelte';
	import InitTauriLog from '@/components/plugin/InitTauriLog.svelte';
	import SQLiteMigration from '@/components/plugin/SQLiteMigration.svelte';
	import { TrayIcon } from '@tauri-apps/api/tray';
	import { changeTrayWithEasing } from '@/tray';
	import SetupClient from '@/components/plugin/SetupClient.svelte';
	import ExecuteOnEscape from '@/components/plugin/ExecuteOnEscape.svelte';
	let search = $state('');
	let isProcessing: boolean = $state(false);
	let currentPage: 'main' | 'settings' = $state('main');

	async function takeScreenshot(config: Config): Promise<string | undefined> {
		isProcessing = true;
		const uuid = crypto.randomUUID();
		const filename = `${systemSettings.appDataDirPath}/${uuid}.png`;
		const start_time = performance.now();
		console.log('takeScreenshot', config);
		if (!$userSettings.value.disableHistory) {
			userData.set({
				value: [
					{
						id: uuid,
						image: null,
						content: null,
						date: new Date(),
						duration: null,
						config: config
					},
					...$userData.value
				]
			});
		}

		try {
			await commands.closeMenubarPanel();

			const base64 = await requestScreenShot(filename, $userSettings.value.playSound);
			userData.set({
				value: $userData.value.map((item) =>
					item.id === uuid ? { ...item, image: convertFileSrc(filename) } : item
				)
			});

			let text: string;
			if (config.type === 'nougat') {
				text = await runNougat(config, filename);
			} else if (config.type === 'ocr') {
				text = await runOCR(config, filename);
			} else {
				throw new Error('Invalid method');
			}

			animatedTray();
			if ($userSettings.value.showNotificationOnCapture) {
				sendNotification({ title: 'Montelimar', body: text });
			}
			if ($userSettings.value.autoCopyToClipboard) {
				writeText(text);
			}

			const end_time = performance.now();
			const duration = end_time - start_time;

			if (!$userSettings.value.disableHistory) {
				userData.set({
					value: $userData.value.map((item) =>
						item.id === uuid ? { ...item, duration: duration, content: text } : item
					)
				});
			}

			return text;
		} catch (error) {
			sendNotification({
				title: 'Montelimar',
				body: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
			});
			// Remove the screenshot from the user data
			userData.set({ value: $userData.value.filter((item) => item.id !== uuid) });
			console.error(error);
		} finally {
			isProcessing = false;
			// await commands.showMenubarPanel();
		}
	}

	let configSpecificShortcutConfigPair = $derived.by(() => {
		return $userSettings.value.configs.map((config) => {
			return {
				config: config,
				shortcut: config.shortcutKey
			};
		});
	});
</script>

<InitSystemSettings />
<StartDatabase />
<InitTauriLog enabled={false} />
<!-- <SQLiteMigration /> -->
<SetupClient />
<DisableRightClickMenu />

<StartCleanUpShortcut />
<Autostart bind:autostart={$userSettings.value.startAtLogin} />
<PlaySound bind:playSound={$userSettings.value.playSound} />
<AutoCopyClipboard bind:autoCopyClipboard={$userSettings.value.autoCopyToClipboard} />
<ShowMenuBarIcon bind:showMenuBarIcon={$userSettings.value.showMenuBarIcon} />
<DisableHistory bind:disableHistory={$userSettings.value.disableHistory} />
<GlobalShortcut
	bind:globalShortcut={$userSettings.value.globalShortcut}
	callback={async () => {
		const config = await askUserForConfig();
		await takeScreenshot(config);
	}}
/>

{#each configSpecificShortcutConfigPair as pair}
	<GlobalShortcut
		bind:globalShortcut={pair.shortcut}
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
