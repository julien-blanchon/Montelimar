<script>
	import { client } from '@/python/client/sdk.gen';
	import { fetch as tauriFetch } from '@tauri-apps/plugin-http';

	$effect(() => {
		client.setConfig({
			baseUrl: 'http://127.0.0.1:7771',
			// fetch: fetch
			fetch: tauriFetch
		});
	});
</script>
