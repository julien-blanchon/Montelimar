<script lang="ts">
	import { attachConsole } from '@tauri-apps/plugin-log';

	interface Props {
		enabled: boolean;
	}

	let { enabled = $bindable(true) }: Props = $props();

	let detach: (() => void) | undefined;

	$effect(() => {
		if (!enabled) return;

		let cancelled = false;

		(async () => {
			detach?.();
			const maybeDetach = await attachConsole();

			if (!cancelled) {
				detach = maybeDetach;
			}
		})();

		// Cleanup on dependency change or destroy
		return () => {
			cancelled = true;
			detach?.();
		};
	});
</script>
