<script lang="ts">
	import { userData } from '@/runes/user_database.svelte';
	import { userSettings } from '@/runes/user_settings.svelte';

	$effect(() => {
		async function startDatabase() {
			await userData.start();
			userData.saveNow();
		}

		async function startSettings() {
			await userSettings.start();
			userSettings.saveNow();
		}

		startDatabase();
		startSettings();

		return () => {
			userData.stop();
			userSettings.stop();
		};
	});
</script>
