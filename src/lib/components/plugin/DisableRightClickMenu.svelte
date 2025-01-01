<script lang="ts">
	$effect(() => {
		async function disableContextMenu() {
			// Only disable context menu in production
			if (window.location.hostname !== 'tauri.localhost') {
				return;
			}

			document.addEventListener(
				'contextmenu',
				(e) => {
					e.preventDefault();
					return false;
				},
				{ capture: true }
			);

			document.addEventListener(
				'selectstart',
				(e) => {
					e.preventDefault();
					return false;
				},
				{ capture: true }
			);
		}

		disableContextMenu();
	});
</script>
