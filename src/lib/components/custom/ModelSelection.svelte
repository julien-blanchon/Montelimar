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
			const nextButton = buttons[nextIndex] as HTMLButtonElement;
			nextButton.focus();
			// Scroll into view if needed
			nextButton.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
		} else if (e.key === 'ArrowLeft') {
			const prevIndex = index === 0 ? totalButtons - 1 : index - 1;
			buttons.forEach((btn) => (btn as HTMLButtonElement).blur());
			const prevButton = buttons[prevIndex] as HTMLButtonElement;
			prevButton.focus();
			// Scroll into view if needed
			prevButton.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
		} else if (e.key === 'Enter') {
			(buttons[index] as HTMLButtonElement).click();
		}
	};
</script>

<div class="flex w-full flex-col items-center gap-4" data-tauri-drag-region>
	<h2 class="text-lg font-semibold" data-tauri-drag-region>Select a model</h2>

	<div
		class="scrollbar-thin scrollbar-thumb-base-300 scrollbar-track-transparent flex w-full max-w-full flex-row gap-4 overflow-x-auto px-4 py-2"
		data-tauri-drag-region
		style="scrollbar-width: thin;"
	>
		{#each configs as config, index}
			<div class="flex flex-shrink-0 flex-col items-center gap-5" data-tauri-drag-region>
				<!-- style={`color: ${config.color}; border-color: ${config.color}; background-color: ${config.color}20;`} -->
				<button
					class={cn(
						'model-button',
						'btn btn-outline btn-md min-h-0 w-32 px-4',
						'flex items-center justify-center',
						'border-2 border-[var(--color)]',
						'bg-[var(--color-background)]',
						'focus-visible:bg-[var(--color-background-hover)] focus-visible:outline-[var(--color)]',
						'focus-visible:scale-105 focus-visible:outline-2',
						'hover:border-[var(--color)] hover:bg-[var(--color-background-hover)] hover:text-black',
						'text-sm font-medium text-black'
					)}
					style={`--color: ${config.color}; --color-background: ${config.color}20; --color-background-hover: ${config.color}40`}
					onkeydown={(e) => handleKeyNavigation(e, index, userSettings.state.value.configs.length)}
					onclick={(e) => {
						e.preventDefault();
						actionFunction(config);
					}}
					onfocus={(e) => {
						// Scroll into view when focused
						(e.target as HTMLButtonElement).scrollIntoView({
							behavior: 'smooth',
							block: 'nearest',
							inline: 'center'
						});
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
