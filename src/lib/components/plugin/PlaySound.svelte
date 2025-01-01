<script lang="ts">
	interface Props {
		playSound: boolean;
	}

	let { playSound = $bindable() }: Props = $props();

	$effect(() => {
		if (playSound) {
			console.log('playSound');
		} else {
			console.log('not playSound');
		}
	});
</script>
