<script lang="ts">
	interface Props {
		callback: () => void;
	}

	let { callback }: Props = $props();

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			callback();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />
