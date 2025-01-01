<script lang="ts">
	import { enable, disable } from '@tauri-apps/plugin-autostart';

	interface Props {
		autostart: boolean;
	}

	let { autostart = $bindable() }: Props = $props();

	$effect(() => {
		if (autostart) {
			enable();
		} else {
			disable();
		}
	});
</script>
