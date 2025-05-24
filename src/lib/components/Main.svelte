<script lang="ts">
	import { cubicOut } from 'svelte/easing';
	import { ChevronLeft, ChevronRight, ClipboardCopy, Copy, Trash2 } from 'lucide-svelte';
	import { flip } from 'svelte/animate';
	import { fade, scale } from 'svelte/transition';
	import { crossfade } from 'svelte/transition';
	import { writeText } from '@tauri-apps/plugin-clipboard-manager';
	import { cn } from '@/utils';
	import { userData } from '@/runes/user_database.svelte';
	import { animatedTray } from '@/actions';
	import { healthHealth } from '@/python/client/sdk.gen';
	import HuggingfaceHubSelector from './custom/HuggingfaceHubSelector.svelte';
	import { userSettings } from '@/runes/user_settings.svelte';

	interface Props {
		search: string;
	}

	let { search }: Props = $props();

	// Pagination state
	let currentPage: number = $state(1);
	let itemsPerPage: number = $state(4);

	let filteredItems = $derived.by(() => {
		if (search == '') {
			return userData.state.value;
		}
		return userData.state.value.filter((item) =>
			item.content?.toLowerCase().includes(search.toLowerCase())
		);
	});

	let totalPages = $derived(Math.ceil(filteredItems.length / itemsPerPage));

	// Get current page items
	let paginatedItems = $derived(
		filteredItems.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
	);

	// Effect to handle empty pages
	$effect(() => {
		// If current page is empty and there are items in previous pages
		if (paginatedItems.length === 0 && currentPage > 1 && filteredItems.length > 0) {
			// Go to the last page with items
			currentPage = Math.max(1, Math.ceil(filteredItems.length / itemsPerPage));
		}
	});

	// Handle page change
	function goToPage(page: number) {
		if (page >= 1 && page <= totalPages) {
			currentPage = page;
		}
	}

	const [send, receive] = crossfade({
		duration: 200,
		fallback: (n) =>
			fade(n, {
				duration: 200,
				delay: 0
			})
	});
</script>

<div class="h-[640px] w-full px-4 py-2">
	<!-- <button
		onclick={async () => {
			// const x = await healthHealthGet()
			const x = await healthHealthGet<true>();
			console.log('done');
			console.log(x.data);
		}}
	>
		Click
	</button> -->

	<!-- <HuggingfaceHubSelector huggingface_model_path="Nougat" /> -->

	<section class="h-[520px] w-full">
		<!-- Number of snips and pagination -->
		<div
			class="grid h-[20px] w-full grid-cols-3 items-center justify-between px-4 text-sm text-base-content"
		>
			<div class="col-span-1 flex h-full items-center justify-start">
				{#if totalPages > 1}
					<span class="inline-flex h-full gap-1">
						Page
						{#key currentPage}
							<p in:scale={{ duration: 200, easing: cubicOut }}>{currentPage}</p>
						{/key}
						of
						{#key totalPages}
							<p in:scale={{ duration: 200, easing: cubicOut }}>{totalPages}</p>
						{/key}
					</span>
				{/if}
			</div>
			<div class="col-span-1 flex h-full items-center justify-center">
				<span class="inline-flex h-full gap-1">
					{#if filteredItems.length > 0}
						{#key filteredItems.length}
							<p in:scale={{ duration: 200, easing: cubicOut }}>{filteredItems.length}</p>
						{/key}
						{#if filteredItems.length !== 1}
							<p in:scale={{ duration: 200, easing: cubicOut }}>snips</p>
						{:else}
							<p in:scale={{ duration: 200, easing: cubicOut }}>snip</p>
						{/if}
					{/if}
				</span>
			</div>
			<!-- Pagination -->
			<div class="col-span-1 flex h-full items-center justify-end">
				{#if totalPages > 1}
					<div class="join" transition:scale={{ duration: 200, easing: cubicOut }}>
						<button
							class="btn btn-square join-item no-animation btn-xs !border-base-content/40 focus:outline-none"
							disabled={currentPage === 1}
							onclick={() => goToPage(currentPage - 1)}
							tabindex={-1}
						>
							<ChevronLeft size={16} />
						</button>
						<button
							class="btn btn-square join-item no-animation btn-xs !border-base-content/40 focus:outline-none"
							disabled={currentPage === totalPages}
							onclick={() => goToPage(currentPage + 1)}
							tabindex={-1}
						>
							<ChevronRight size={16} />
						</button>
					</div>
				{/if}
			</div>
		</div>
		<div class="mt-4 flex h-[475px] w-full items-center justify-center">
			{#if filteredItems.length > 0}
				<!-- Snips -->
				<div class="grid h-full w-full grid-cols-2 gap-2 overflow-hidden">
					{#key currentPage}
						{#each paginatedItems as item, i (item.id)}
							{@const currentConfig = userSettings.state.value.configs.find(
								(config) => config.id === item.config.id
							)}
							{@const currentConfigColor = currentConfig?.color || item.config.color}
							{@const currentConfigName = currentConfig?.name || item.config.name}
							<div
								class="group h-[230px] w-[230px] overflow-hidden rounded-2xl border-[1px] border-base-content/40"
								animate:flip={{ duration: 300 }}
								in:receive|local={{ key: item }}
								out:send|local={{ key: item }}
							>
								<!-- If not hover -->
								<div
									class="relative flex h-full w-full flex-col overflow-hidden group-hover:hidden"
									transition:fade={{ duration: 200 }}
								>
									<!-- Image Text on top center with-->
									<div class="absolute left-0 right-0 top-0 z-20 m-auto h-full text-center text-sm">
										{#if item.content}
											<div class="mb-2 h-full w-full overflow-hidden rounded-md bg-base-100/70 p-2">
												<div
													class="pointer-events-none absolute inset-0 bg-gradient-to-t from-base-100 from-10% to-transparent"
												></div>
												<p class="text-wrap text-xs text-base-content">
													{item.content?.slice(0, 300)}
												</p>
											</div>
										{:else}
											<div class="flex w-full flex-col gap-1 p-4">
												<div class="skeleton h-4 w-full bg-black/20"></div>
												<div class="skeleton h-4 w-2/3 bg-black/20"></div>
												<div class="skeleton h-4 w-4/5 bg-black/20"></div>
												<div class="skeleton h-4 w-1/2 bg-black/20"></div>
												<div class="skeleton h-4 w-full bg-black/20"></div>
												<div class="skeleton h-4 w-1/3 bg-black/20"></div>
												<div class="skeleton h-4 w-2/3 bg-black/20"></div>
												<div class="skeleton h-4 w-4/5 bg-black/20"></div>
												<div class="skeleton h-4 w-1/2 bg-black/20"></div>
											</div>
										{/if}
									</div>

									<!-- Image or Skeleton (blurry overlay) -->
									<div class="z-0 flex h-full w-full items-center justify-center blur-[0.8px]">
										{#if item.image}
											<img
												src={item.image}
												alt={item.id}
												class="h-full w-full rounded-md object-scale-down"
											/>
										{:else}
											<div class="flex w-full flex-col gap-4 p-4">
												<div class="skeleton h-44 w-full bg-blue-100/50"></div>
											</div>
										{/if}
									</div>
									<!-- Tag with the config model name on bottom center -->
									<span
										class={cn(
											'badge badge-outline',
											'absolute bottom-0 left-0 right-0 z-20 m-auto mb-2'
										)}
										style={`color: ${currentConfigColor}; border-color: ${currentConfigColor}`}
									>
										{currentConfigName}
									</span>
								</div>
								<!-- If hover -->
								<div class="hidden h-full w-full items-center justify-center group-hover:flex">
									{#if item.content && item.content !== ''}
										<div class="flex h-full w-full flex-col divide-y-2 divide-base-content/40">
											<button
												onclick={() => {
													if (item.content) {
														animatedTray();
														writeText(item.content);
													}
												}}
												class="group/copy flex h-1/2 w-full items-center justify-center gap-2 rounded-t-md bg-blue-500/10 p-2 transition-colors hover:bg-blue-500/20 active:bg-blue-500/40"
											>
												<Copy class="size-5 text-blue-500" />
											</button>
											<button
												onclick={() => {
													// Remove the item from the database
													userData.state.value = userData.state.value.filter(
														(i) => i.id !== item.id
													);
												}}
												class="group/delete flex h-1/2 w-full items-center justify-center gap-2 rounded-b-md bg-red-500/10 p-2 transition-colors hover:bg-red-500/20 active:bg-red-500/40"
											>
												<Trash2 class="size-5 text-red-500 " />
											</button>
										</div>
									{:else}
										<div class="flex h-full w-full flex-col">
											<button
												onclick={() => {
													// Remove the item from the database
													userData.state.value = userData.state.value.filter(
														(i) => i.id !== item.id
													);
												}}
												class="group/delete flex h-full w-full items-center justify-center gap-2 rounded-b-md bg-red-500/10 p-2 transition-colors hover:bg-red-500/20 active:bg-red-500/40"
											>
												<Trash2 class="size-5 text-red-500 " />
											</button>
										</div>
									{/if}
								</div>
							</div>
						{/each}
					{/key}
				</div>
			{:else if userData.state.value.length === 0}
				<!-- No items found -->
				<div class="mt-4 flex h-32 w-full items-center justify-center rounded-lg">
					<p class="text-base-content/70">Your future snips will appear here.</p>
				</div>
			{:else}
				<!-- No items found -->
				<div class="mt-4 flex h-32 w-full items-center justify-center rounded-lg">
					<p class="text-base-content/70">No items found</p>
				</div>
			{/if}
		</div>
	</section>
</div>
