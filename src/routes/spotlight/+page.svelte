<script lang="ts">
	import { emit } from '@tauri-apps/api/event';
	import { commands } from '@/tauri/bindings';
	import ExecuteOnEscape from '@/components/plugin/ExecuteOnEscape.svelte';
	import ModelSelection from '@/components/custom/ModelSelection.svelte';
	import InitSystemSettings from '@/components/plugin/InitSystemSettings.svelte';
	import DisableRightClickMenu from '@/components/plugin/DisableRightClickMenu.svelte';
	import { userSettings } from '@/stores/user_settings';
	import StartDatabase from '@/components/plugin/StartDatabase.svelte';
</script>

<DisableRightClickMenu />
<ExecuteOnEscape
	callback={() => {
		commands.hideSpotlightPanel();
	}}
/>
<StartDatabase />
<InitSystemSettings />

<div
	data-tauri-drag-region
	class="flex h-screen w-screen items-center justify-center bg-transparent"
>
	<div data-tauri-drag-region class="flex w-full max-w-3xl items-center justify-center">
		<ModelSelection
			actionFunction={(config) => {
				emit('config-selected', config);
			}}
			configs={$userSettings.value.configs}
		/>
	</div>
</div>
