<script>
	import { client } from '@/python/client/sdk.gen';
	import { fetch as tauriFetch } from '@tauri-apps/plugin-http';

	$effect(() => {
		client.setConfig({
			baseUrl: 'http://localhost:7771',
			// fetch: fetch
			fetch: tauriFetch
		});
	});
</script>
