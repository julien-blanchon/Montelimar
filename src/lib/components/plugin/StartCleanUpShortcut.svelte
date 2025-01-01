<script lang="ts">
	import { unregisterAll } from '@tauri-apps/plugin-global-shortcut';

	$effect(() => {
		async function startCleanUpShortcut() {
			unregisterAll();
		}

		startCleanUpShortcut();
	});
</script>
