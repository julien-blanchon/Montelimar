<script lang="ts">
	import { userSettings } from '@/runes/user_settings.svelte';
	import { systemSettings } from '@/runes/system_settings.svelte';
	import { requestPermission } from '@tauri-apps/plugin-notification';
	import { cn } from '@/utils';
	import InputShortcut from '@/components/custom/InputShortcut.svelte';
	import { formatShortcut } from '@/shortcut';
	import {
		Bell,
		BellOff,
		Power,
		Volume2,
		Copy,
		Menu,
		Archive,
		Keyboard,
		Settings
	} from 'lucide-svelte';

	async function requestNotificationPermission() {
		try {
			const permission = await requestPermission();
			systemSettings.notificationPermissionGranted = permission === 'granted';
		} catch (error) {
			console.error('Failed to request notification permission:', error);
		}
	}
</script>

<div class="rounded-lg border border-base-300 bg-base-100/50 p-6">
	<div class="mb-6">
		<h2 class="text-xl font-semibold">General Settings</h2>
	</div>

	<div class="space-y-4">
		<!-- Start at Login -->
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="flex h-8 w-8 items-center justify-center rounded-md bg-blue-100 text-blue-600">
					<Power class="h-4 w-4" />
				</div>
				<div>
					<label for="start-at-login" class="text-sm font-medium text-base-content"
						>Start at login</label
					>
					<p class="text-xs text-base-content/60">Automatically start the app when you log in</p>
				</div>
			</div>
			<input
				id="start-at-login"
				type="checkbox"
				bind:checked={userSettings.state.value.startAtLogin}
				class="toggle toggle-primary"
			/>
		</div>

		<!-- Play Sound -->
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div
					class="flex h-8 w-8 items-center justify-center rounded-md bg-green-100 text-green-600"
				>
					<Volume2 class="h-4 w-4" />
				</div>
				<div>
					<label for="play-sound" class="text-sm font-medium text-base-content"
						>Play sound on capture</label
					>
					<p class="text-xs text-base-content/60">Play a sound when capturing screenshots</p>
				</div>
			</div>
			<input
				id="play-sound"
				type="checkbox"
				bind:checked={userSettings.state.value.playSound}
				class="toggle toggle-primary"
			/>
		</div>

		<!-- Auto Copy to Clipboard -->
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div
					class="flex h-8 w-8 items-center justify-center rounded-md bg-purple-100 text-purple-600"
				>
					<Copy class="h-4 w-4" />
				</div>
				<div>
					<label for="auto-copy-clipboard" class="text-sm font-medium text-base-content"
						>Auto copy to clipboard</label
					>
					<p class="text-xs text-base-content/60">Automatically copy results to clipboard</p>
				</div>
			</div>
			<input
				id="auto-copy-clipboard"
				type="checkbox"
				bind:checked={userSettings.state.value.autoCopyToClipboard}
				class="toggle toggle-primary"
			/>
		</div>

		<!-- Show Menu Bar Icon -->
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div
					class="flex h-8 w-8 items-center justify-center rounded-md bg-orange-100 text-orange-600"
				>
					<Menu class="h-4 w-4" />
				</div>
				<div>
					<label for="show-menu-bar-icon" class="text-sm font-medium text-base-content"
						>Show menu bar icon</label
					>
					<p class="text-xs text-base-content/60">Display app icon in the system menu bar</p>
				</div>
			</div>
			<input
				id="show-menu-bar-icon"
				type="checkbox"
				bind:checked={userSettings.state.value.showMenuBarIcon}
				class="toggle toggle-primary"
			/>
		</div>

		<!-- Disable History -->
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="flex h-8 w-8 items-center justify-center rounded-md bg-red-100 text-red-600">
					<Archive class="h-4 w-4" />
				</div>
				<div>
					<label for="disable-history" class="text-sm font-medium text-base-content"
						>Disable history</label
					>
					<p class="text-xs text-base-content/60">Don't save capture history locally</p>
				</div>
			</div>
			<input
				id="disable-history"
				type="checkbox"
				bind:checked={userSettings.state.value.disableHistory}
				class="toggle toggle-primary"
			/>
		</div>

		<!-- Show Notification on Capture -->
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div
					class="flex h-8 w-8 items-center justify-center rounded-md bg-yellow-100 text-yellow-600"
				>
					{#if systemSettings.notificationPermissionGranted}
						<Bell class="h-4 w-4" />
					{:else}
						<BellOff class="h-4 w-4" />
					{/if}
				</div>
				<div>
					<label for="show-notification-capture" class="text-sm font-medium text-base-content"
						>Show notification on capture</label
					>
					<p class="text-xs text-base-content/60">Display notifications when capturing</p>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<input
					id="show-notification-capture"
					type="checkbox"
					bind:checked={userSettings.state.value.showNotificationOnCapture}
					class="toggle toggle-primary"
				/>
				{#if !systemSettings.notificationPermissionGranted}
					<button
						onclick={requestNotificationPermission}
						class="btn btn-outline btn-xs"
						title="Request notification permission"
					>
						<BellOff class="h-3 w-3" />
					</button>
				{/if}
			</div>
		</div>

		<!-- Global Shortcut -->
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div
					class="flex h-8 w-8 items-center justify-center rounded-md bg-indigo-100 text-indigo-600"
				>
					<Keyboard class="h-4 w-4" />
				</div>
				<div>
					<label for="global-shortcut" class="text-sm font-medium text-base-content"
						>Global shortcut</label
					>
					<p class="text-xs text-base-content/60">Keyboard shortcut to trigger capture</p>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<InputShortcut id="global-shortcut" bind:value={userSettings.state.value.globalShortcut} />
			</div>
		</div>
	</div>
</div>
