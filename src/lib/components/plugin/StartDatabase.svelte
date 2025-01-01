<script lang="ts">
	import { userData } from '@/stores/user_database';
	import { userSettings } from '@/stores/user_settings';

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
