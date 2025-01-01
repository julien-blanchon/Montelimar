<script lang="ts">
	interface Props {
		disableHistory: boolean;
	}

	let { disableHistory = $bindable() }: Props = $props();

	$effect(() => {
		if (disableHistory) {
			console.log('disableHistory');
		} else {
			console.log('not disableHistory');
		}
	});
</script>