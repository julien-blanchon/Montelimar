<script lang="ts">
	interface Props {
		showMenuBarIcon: boolean;
	}

	let { showMenuBarIcon = $bindable() }: Props = $props();

	$effect(() => {
		if (showMenuBarIcon) {
			console.log('showMenuBarIcon');
		} else {
			console.log('not showMenuBarIcon');
		}
	});
</script>