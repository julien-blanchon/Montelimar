<script lang="ts">
	interface Props {
		autoCopyClipboard: boolean;
	}

	let { autoCopyClipboard = $bindable() }: Props = $props();

	$effect(() => {
		if (autoCopyClipboard) {
			console.log('autoCopyClipboard');
		} else {
			console.log('not autoCopyClipboard');
		}
	});
</script>
