<script lang="ts">
	import { listModels } from '@huggingface/hub';
	import { fetch as tauriFetch } from '@tauri-apps/plugin-http';

	interface Props {
		huggingface_model_path: string;
	}
	const { huggingface_model_path = $bindable() }: Props = $props();

	const models: string[] = $state([]);
</script>

<button
	onclick={async () => {
		for await (const model of listModels({
			fetch: tauriFetch,
			limit: 10,
			search: {
				query: 'Nougat'
			}
		})) {
			models.push(model.name);
		}

		console.log(models);
	}}
>
	Load Models
</button>

<div>
	<h2>Huggingface Hubs</h2>
</div>
