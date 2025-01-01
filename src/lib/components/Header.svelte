<script lang="ts">
	import { cn } from '@/utils';
	import { ScanText, Search, Settings } from 'lucide-svelte';

	interface Props {
		callback: () => Promise<string | undefined>;
		isProcessing: boolean;
		currentPage: 'main' | 'settings';
		search: string;
	}

	let {
		callback,
		isProcessing = $bindable(),
		currentPage = $bindable(),
		search = $bindable()
	}: Props = $props();
</script>

<div
	class="top-0 z-50 flex h-[40px] w-full items-center justify-between space-x-2 divide-x divide-base-content/40 border-b border-base-content/40 px-2 py-2"
>
	<!-- (align) Left side -->
	<div class="flex h-full justify-start pr-2">
		<button
			class={cn(
				'h-full text-base-content outline-none ring-0',
				'hover:text-blue-500 focus:ring-0 disabled:cursor-not-allowed',
				'disabled:opacity-20 disabled:hover:text-base-content',
				'flex items-center justify-center',
				'disabled:hover:text-base-content data-[active=true]:animate-spin data-[active=true]:text-blue-500'
			)}
			data-active={isProcessing}
			disabled={isProcessing || currentPage === 'settings'}
			onclick={async () => {
				await callback();
			}}
		>
			<!-- <Icon
				icon="fluent:screenshot-24-regular"
				height={24}
				onclick={async () => {
					// Hide the menubar panel
					// await commands.closeMenubarPanel();
					// Take the screenshot
					await callback();
					// Show the menubar panel
					// await commands.showMenubarPanel();
				}}
			/> -->
			<ScanText class="size-5 text-base-content/70" height={24} />
		</button>
	</div>

	<!-- (align) Center side -->
	<div class="flex h-full w-full flex-1 items-center justify-center">
		<!-- Search Bar -->
		<div class="relative flex w-56 text-sm text-base-content">
			<label
				for="search"
				class="sr-only text-sm font-medium leading-none peer-disabled:cursor-not-allowed"
				>Search</label
			>
			<input
				class={cn(
					'border-1 peer flex h-7 w-full rounded-full border border-base-content bg-transparent pl-8 text-base shadow-none transition-colors duration-100',
					'placeholder:text-opacity-85 hover:border-blue-500 hover:ring-offset-0',
					'hover:placeholder:text-blue-500/50',
					'focus-visible:border-blue-500 focus-visible:bg-blue-500/20 focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0',
					'focus-visible:placeholder:text-blue-500/50 disabled:cursor-not-allowed disabled:opacity-20 disabled:hover:border-base-content',
					'disabled:placeholder:text-base-content'
				)}
				id="search"
				placeholder="Search"
				disabled={currentPage === 'settings'}
				bind:value={search}
			/>
			<!-- <Icon
				icon="fluent:search-24-regular"
				class={cn(
					'pointer-events-none absolute left-2 top-1/2 size-5 -translate-y-1/2 select-none text-base-content opacity-50',
					'peer-hover:text-blue-500 peer-focus-visible:text-blue-500',
					'peer-disabled:opacity-20 peer-disabled:peer-hover:text-base-content peer-disabled:peer-focus-visible:text-base-content'
				)}
			></Icon> -->
			<Search
				class={cn(
					'pointer-events-none absolute left-2 top-1/2 size-4 -translate-y-1/2 select-none text-base-content opacity-50',
					'peer-hover:text-blue-500 peer-focus-visible:text-blue-500',
					'peer-disabled:opacity-20 peer-disabled:peer-hover:text-base-content peer-disabled:peer-focus-visible:text-base-content'
				)}
				height={24}
			/>
		</div>
	</div>

	<!-- (align) Right side -->
	<div class="flex h-full justify-end pl-2">
		<button
			class={cn(
				'group h-full text-base-content outline-none ring-0 transition-all duration-100 ease-out',
				'hover:text-blue-500 focus:ring-0 disabled:opacity-50',
				'data-[active=true]:rotate-90 data-[active=true]:text-blue-800'
			)}
			data-active={currentPage === 'settings'}
			onclick={() => {
				currentPage = currentPage === 'settings' ? 'main' : 'settings';
			}}
		>
			<!-- <Icon
				icon="fluent:settings-24-regular"
				height={24}
				class="glow-radius-lg group-data-[active=true]:glow-blue-500"
			></Icon> -->
			<Settings
				class="size-5 text-base-content/70 group-data-[active=true]:glow-blue-500"
				height={24}
			/>
		</button>
	</div>
</div>
