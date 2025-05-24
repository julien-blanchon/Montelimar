<script lang="ts">
	import { getVersion } from '@tauri-apps/api/app';
	import { onMount } from 'svelte';
	import { ExternalLink } from 'lucide-svelte';
	import LogosTauriIcon from '@/components/icon/logos--tauri.svg.svelte';
	import LogosSvelteIcon from '@/components/icon/logos--svelte-icon.svg.svelte';
	import LogosRustIcon from '@/components/icon/logos--rust.svg.svelte';
	import LogosTailwindcssIcon from '@/components/icon/logos--tailwindcss-icon.svg.svelte';
	import LogosMicrosoftIcon from '@/components/icon/logos--microsoft-icon.svg.svelte';

	let appVersion = $state('');

	onMount(async () => {
		try {
			appVersion = await getVersion();
		} catch (error) {
			console.error('Failed to get app version:', error);
			appVersion = 'Unknown';
		}
	});
</script>

<div class="rounded-lg border border-base-300 bg-base-100/50 p-6">
	<div class="mb-6">
		<h2 class="text-xl font-semibold">About</h2>
	</div>

	<div class="space-y-3">
		<!-- App Info -->
		<div class="space-y-3 rounded-lg bg-base-200/50 p-4">
			<div class="flex items-center gap-3">
				<div class="flex h-32 w-32 items-center justify-center overflow-hidden rounded-lg">
					<img src="/big_logo.png" alt="Montelimar Logo" class="h-full w-full object-contain" />
				</div>
				<div>
					<h3 class="font-semibold text-base-content">Montelimar</h3>
					<p class="text-sm text-base-content/60">Version {appVersion}</p>
				</div>
			</div>

			<p class="text-sm text-base-content/60">
				A powerful OCR and document processing application with AI capabilities.
			</p>
		</div>

		<!-- Credits -->
		<div class="space-y-3">
			<h3 class="text-lg font-medium text-base-content">Credits</h3>
			<div class="space-y-2">
				<p class="text-sm font-medium">Built with</p>
				<div class="flex flex-wrap gap-2">
					<a
						href="https://tauri.app"
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
					>
						<LogosTauriIcon class="size-4" />
						Tauri
					</a>
					<a
						href="https://svelte.dev"
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
					>
						<LogosSvelteIcon class="size-4" />
						Svelte
					</a>
					<a
						href="https://www.rust-lang.org"
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
					>
						<LogosRustIcon class="size-4" />
						Rust
					</a>
					<a
						href="https://tailwindcss.com"
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
					>
						<LogosTailwindcssIcon class="size-4" />
						Tailwind CSS
					</a>
					<a
						href="https://github.com/microsoft/fluentui-system-icons/"
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
					>
						<LogosMicrosoftIcon class="size-4" />
						Fluent Icons
					</a>
				</div>
			</div>
		</div>
	</div>
</div>
