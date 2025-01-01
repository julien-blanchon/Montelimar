<script lang="ts">
	import { migrate } from '@/db/migrate';

	$effect(() => {
		async function initMigrations() {
			await migrate();
		}
		initMigrations();
	});
</script>
