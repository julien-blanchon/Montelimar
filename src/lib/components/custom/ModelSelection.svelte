<script lang="ts">
	import { type Config } from '@/types';
	import { userSettings } from '@/runes/user_settings.svelte';
	import { cn } from '@/utils';

	interface Props {
		actionFunction: (config: Config) => void;
		configs: Config[];
	}
	let { actionFunction, configs = $bindable() }: Props = $props();

	// Add keyboard event listener for number keys
	$effect(() => {
		const handleKeyPress = (e: KeyboardEvent) => {
			const key = parseInt(e.key);
			if (!isNaN(key) && key > 0 && key <= configs.length) {
				const buttons = document.querySelectorAll('.model-button');
				const button = buttons[key - 1] as HTMLButtonElement;
				button.click();
			}
		};

		window.addEventListener('keydown', handleKeyPress);
		return () => window.removeEventListener('keydown', handleKeyPress);
	});

	const handleKeyNavigation = (e: KeyboardEvent, index: number, totalButtons: number) => {
		const buttons = document.querySelectorAll('.model-button');
		if (e.key === 'ArrowRight') {
			const nextIndex = (index + 1) % totalButtons;
			buttons.forEach((btn) => (btn as HTMLButtonElement).blur());
			(buttons[nextIndex] as HTMLButtonElement).focus();
		} else if (e.key === 'ArrowLeft') {
			const prevIndex = index === 0 ? totalButtons - 1 : index - 1;
			buttons.forEach((btn) => (btn as HTMLButtonElement).blur());
			(buttons[prevIndex] as HTMLButtonElement).focus();
		} else if (e.key === 'Enter') {
			(buttons[index] as HTMLButtonElement).click();
		}
	};
</script>

<div class="flex flex-col items-center gap-4" data-tauri-drag-region>
	<h2 class="text-lg font-semibold" data-tauri-drag-region>Select a model</h2>

	<div class="flex flex-row gap-4" data-tauri-drag-region>
		{#each configs as config, index}
			<div class="flex flex-col items-center gap-5" data-tauri-drag-region>
				<!-- style={`color: ${config.color}; border-color: ${config.color}; background-color: ${config.color}20;`} -->
				<button
					class={cn(
						'model-button',
						'btn btn-outline btn-md min-h-0 w-32 px-4',
						'flex items-center justify-center',
						'border-2 border-[var(--color)]',
						'bg-[var(--color-background)]',
						'focus-visible:bg-[var(--color-background-hover)] focus-visible:outline-[var(--color)]',
						'focus-visible:scale-105 focus-visible:text-white focus-visible:outline-2',
						'hover:border-[var(--color-background)] hover:bg-[var(--color-background-hover)] hover:text-white',
						'text-sm font-medium'
					)}
					style={`--color: ${config.color}; --color-background: ${config.color}20; --color-background-hover: ${config.color}60`}
					onkeydown={(e) => handleKeyNavigation(e, index, userSettings.state.value.configs.length)}
					onclick={(e) => {
						e.preventDefault();
						actionFunction(config);
					}}
					onfocus={(e) => {
						// pass
					}}
					onmouseover={(e) => {
						// Remove focus from all other buttons before focusing this one
						const buttons = document.querySelectorAll('.model-button');
						buttons.forEach((btn) => (btn as HTMLButtonElement).blur());
						(e.target as HTMLButtonElement).focus();
					}}
				>
					{config.name.slice(0, 20)}
				</button>
				<span class="text-xs text-base-content/90">
					Press <kbd
						class="kbd kbd-sm px-2"
						style={`color: ${config.color}; border-color: ${config.color}`}>{index + 1}</kbd
					> to select
				</span>
			</div>
		{/each}
	</div>
</div>
