<script lang="ts">
	import type { ConfigNougat, ConfigOCR, ConfigLLMEndpoint } from '@/types';
	import { userSettings } from '@/runes/user_settings.svelte';
	import {
		Pencil,
		Trash2,
		Save,
		X,
		Check,
		FileText,
		Camera,
		Brain,
		GripVertical
	} from 'lucide-svelte';
	import { cn } from '@/utils';
	import { dndzone } from 'svelte-dnd-action';
	import InputShortcut from '@/components/custom/InputShortcut.svelte';
	import { formatShortcut } from '@/shortcut';
	import { fade, scale, slide } from 'svelte/transition';

	// State management
	let editingConfig: string | null = $state(null);
	let isAddingNew = $state(false);
	let configType: 'nougat' | 'ocr' | 'llm_endpoint' = $state('nougat');
	let saveConfirmationId: number | null = $state(null);
	let saveConfirmationIndex: number | null = $state(null);

	const DEFAULT_LLM_CONFIG_PROMPT = `
You are an OCR model.
I will give you an image of a document, sign, or printed text.
Your task is to extract the visible text exactly as it appears in the image.
- Preserve line breaks and formatting where possible.
- Do not add or remove any words.
- Output text only — no explanations, no commentary.
Here is the image:
	`;

	// Utility functions
	function getNextId() {
		return Math.max(0, ...userSettings.state.value.configs.map((c) => c.id)) + 1;
	}

	function pickRandomColor() {
		const NICE_COLORS = [
			'#FF5733',
			'#33FF57',
			'#3357FF',
			'#F3FF33',
			'#FF33A1',
			'#33FFF6',
			'#9B33FF',
			'#FF8C33',
			'#33FF9B',
			'#A1FF33'
		];
		return NICE_COLORS[Math.floor(Math.random() * NICE_COLORS.length)];
	}

	// Default configurations
	let newNougatConfig: ConfigNougat = $state({
		id: 0,
		name: '',
		type: 'nougat',
		shortcutKey: null,
		nougat_config: {
			hf_model_name: '',
			temperature: 0.7,
			top_p: 0.9,
			repetition_penalty: 1.9
		},
		color: pickRandomColor()
	});

	let newOCRConfig: ConfigOCR = $state({
		id: 0,
		name: '',
		type: 'ocr',
		shortcutKey: null,
		ocr_config: {
			detection_model_url: '',
			recognition_model_url: '',
			disableLineBreaks: false
		},
		color: pickRandomColor()
	});

	let newLLMConfig: ConfigLLMEndpoint = $state({
		id: 0,
		name: '',
		type: 'llm_endpoint',
		shortcutKey: null,
		llm_config: {
			api_key: '',
			model: 'gpt-4.1-mini',
			endpoint_url: 'https://api.openai.com/v1/chat/completions',
			max_tokens: 1000,
			temperature: 0.0,
			prompt: DEFAULT_LLM_CONFIG_PROMPT
		},
		color: pickRandomColor()
	});

	// Event handlers
	function handleConsider(e: CustomEvent) {
		const { items: newItems } = e.detail;
		userSettings.state.value.configs = newItems;
	}

	function handleFinalize(e: CustomEvent) {
		const { items: newItems } = e.detail;
		userSettings.state.value.configs = newItems;
	}

	function startDrag(e: Event) {
		e.preventDefault();
	}

	function startEditing(configId: string) {
		editingConfig = configId;
	}

	function resetNewConfigs() {
		newNougatConfig = {
			id: 0,
			name: '',
			type: 'nougat',
			shortcutKey: null,
			nougat_config: {
				hf_model_name: '',
				temperature: 0.7,
				top_p: 0.9,
				repetition_penalty: 1.9
			},
			color: pickRandomColor()
		};
		newOCRConfig = {
			id: 0,
			name: '',
			type: 'ocr',
			shortcutKey: null,
			ocr_config: {
				detection_model_url: '',
				recognition_model_url: '',
				disableLineBreaks: false
			},
			color: pickRandomColor()
		};
		newLLMConfig = {
			id: 0,
			name: '',
			type: 'llm_endpoint',
			shortcutKey: null,
			llm_config: {
				api_key: '',
				model: 'gpt-4.1-mini',
				endpoint_url: 'https://api.openai.com/v1/chat/completions',
				max_tokens: 1000,
				temperature: 0.0,
				prompt: DEFAULT_LLM_CONFIG_PROMPT
			},
			color: pickRandomColor()
		};
	}

	function cancelEditing() {
		editingConfig = null;
		isAddingNew = false;
		resetNewConfigs();
	}

	function saveConfig() {
		if (isAddingNew) {
			const config =
				configType === 'nougat'
					? newNougatConfig
					: configType === 'ocr'
						? newOCRConfig
						: newLLMConfig;
			if (config.name) {
				const nextId = getNextId();
				userSettings.state.value.configs = [
					{ ...config, id: nextId },
					...userSettings.state.value.configs
				];
				saveConfirmationId = nextId;
				setTimeout(() => {
					saveConfirmationId = null;
				}, 1500);
			}
		} else if (editingConfig !== null) {
			saveConfirmationIndex = parseInt(editingConfig);
			setTimeout(() => {
				saveConfirmationIndex = null;
			}, 1500);
		}
		cancelEditing();
	}

	function deleteConfig(index: number) {
		userSettings.state.value.configs = userSettings.state.value.configs.filter(
			(_, i) => i !== index
		);
	}

	function startAddingConfig(type: 'nougat' | 'ocr' | 'llm_endpoint') {
		if (!isAddingNew) {
			configType = type;
			isAddingNew = true;
		} else {
			cancelEditing();
		}
	}

	// Common input styles
	const inputStyles = cn(
		'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
		'focus:border-primary/20 focus:bg-base-100',
		'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
		'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
		'w-full'
	);
</script>

<div class="rounded-lg border border-base-300 bg-base-100/50 p-6">
	<div class="h-full overflow-y-scroll">
		<div class="mb-6 space-y-4">
			<h2 class="text-xl font-semibold">Installed Models</h2>

			<!-- Add Buttons Section -->
			<div class="space-y-3">
				<p class="text-sm text-base-content/70">Choose a model type to add:</p>
				<div class="grid grid-cols-1 gap-2 p-1 sm:grid-cols-3">
					<!-- Nougat Button -->
					<button
						class={cn(
							'group relative overflow-hidden rounded-lg border-2 p-3 text-left transition-all duration-200',
							'hover:scale-[1.01] hover:shadow-md',
							configType === 'nougat' && isAddingNew
								? 'border-primary bg-primary/10 shadow-sm'
								: 'border-base-300 bg-base-100/80 hover:border-primary/50 hover:bg-base-100',
							'disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-none'
						)}
						onclick={() => startAddingConfig('nougat')}
						disabled={isAddingNew && configType !== 'nougat'}
					>
						<div class="flex items-start gap-2">
							<div
								class={cn(
									'flex h-8 w-8 items-center justify-center rounded-md transition-colors',
									configType === 'nougat' && isAddingNew
										? 'bg-primary/20 text-primary'
										: 'bg-orange-100 text-orange-600 group-hover:bg-orange-200'
								)}
							>
								<FileText class="h-4 w-4" />
							</div>
							<div class="min-w-0 flex-1">
								<h3
									class={cn(
										'text-sm font-semibold transition-colors',
										configType === 'nougat' && isAddingNew
											? 'text-primary'
											: 'text-base-content group-hover:text-primary'
									)}
								>
									Nougat Model
								</h3>
								<p class="mt-0.5 text-xs text-base-content/60">
									Define a new Nougat Model (mostly for PDF and LaTeX content)
								</p>
							</div>
						</div>
						{#if configType === 'nougat' && isAddingNew}
							<div
								class="pointer-events-none absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent"
							></div>
						{/if}
					</button>

					<!-- OCR Button -->
					<button
						class={cn(
							'group relative overflow-hidden rounded-lg border-2 p-3 text-left transition-all duration-200',
							'hover:scale-[1.01] hover:shadow-md',
							configType === 'ocr' && isAddingNew
								? 'border-primary bg-primary/10 shadow-sm'
								: 'border-base-300 bg-base-100/80 hover:border-primary/50 hover:bg-base-100',
							'disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-none'
						)}
						onclick={() => startAddingConfig('ocr')}
						disabled={isAddingNew && configType !== 'ocr'}
					>
						<div class="flex items-start gap-2">
							<div
								class={cn(
									'flex h-8 w-8 items-center justify-center rounded-md transition-colors',
									configType === 'ocr' && isAddingNew
										? 'bg-primary/20 text-primary'
										: 'bg-blue-100 text-blue-600 group-hover:bg-blue-200'
								)}
							>
								<Camera class="h-4 w-4" />
							</div>
							<div class="min-w-0 flex-1">
								<h3
									class={cn(
										'text-sm font-semibold transition-colors',
										configType === 'ocr' && isAddingNew
											? 'text-primary'
											: 'text-base-content group-hover:text-primary'
									)}
								>
									OCRS Model
								</h3>
								<p class="mt-0.5 text-xs text-base-content/60">
									Define a new OCRS Model (mostly for pure text images)
								</p>
							</div>
						</div>
						{#if configType === 'ocr' && isAddingNew}
							<div
								class="pointer-events-none absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent"
							></div>
						{/if}
					</button>

					<!-- LLM Button -->
					<button
						class={cn(
							'group relative overflow-hidden rounded-lg border-2 p-3 text-left transition-all duration-200',
							'hover:scale-[1.01] hover:shadow-md',
							configType === 'llm_endpoint' && isAddingNew
								? 'border-primary bg-primary/10 shadow-sm'
								: 'border-base-300 bg-base-100/80 hover:border-primary/50 hover:bg-base-100',
							'disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-none'
						)}
						onclick={() => startAddingConfig('llm_endpoint')}
						disabled={isAddingNew && configType !== 'llm_endpoint'}
					>
						<div class="flex items-start gap-2">
							<div
								class={cn(
									'flex h-8 w-8 items-center justify-center rounded-md transition-colors',
									configType === 'llm_endpoint' && isAddingNew
										? 'bg-primary/20 text-primary'
										: 'bg-purple-100 text-purple-600 group-hover:bg-purple-200'
								)}
							>
								<Brain class="h-4 w-4" />
							</div>
							<div class="min-w-0 flex-1">
								<h3
									class={cn(
										'text-sm font-semibold transition-colors',
										configType === 'llm_endpoint' && isAddingNew
											? 'text-primary'
											: 'text-base-content group-hover:text-primary'
									)}
								>
									LLM Endpoint
								</h3>
								<p class="mt-0.5 text-xs text-base-content/60">
									Define a new LLM Endpoint (for everything, you can customize the prompt)
								</p>
							</div>
						</div>
						{#if configType === 'llm_endpoint' && isAddingNew}
							<div
								class="pointer-events-none absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent"
							></div>
						{/if}
					</button>
				</div>
			</div>
		</div>

		<!-- Add New Config Form -->
		{#if isAddingNew}
			<div
				class="rounded-lg border border-base-300 bg-base-100/50 p-6"
				in:slide={{ duration: 200 }}
				out:slide={{ duration: 200 }}
			>
				<form
					class="space-y-4"
					onsubmit={(e) => {
						e.preventDefault();
						const form = e.target as HTMLFormElement;
						if (form.checkValidity()) {
							saveConfig();
						}
					}}
				>
					{#if configType === 'nougat'}
						{@render nougatForm(newNougatConfig, true)}
					{:else if configType === 'ocr'}
						{@render ocrForm(newOCRConfig, true)}
					{:else}
						{@render llmForm(newLLMConfig, true)}
					{/if}

					<div class="flex justify-end gap-2">
						<button
							type="button"
							class="inline-flex items-center gap-2 rounded-md border border-base-300 bg-base-200/50 px-3 py-1.5 text-sm font-medium transition-colors hover:bg-base-200"
							onclick={cancelEditing}
						>
							<X class="size-4 text-base-content/70" />
							Cancel
						</button>
						<button
							type="submit"
							class="inline-flex items-center gap-2 rounded-md border border-success/20 bg-success/10 px-3 py-1.5 text-sm font-medium text-success transition-colors hover:bg-success/20"
						>
							<Check class="size-4" />
							Add
						</button>
					</div>
				</form>
			</div>
		{/if}

		<!-- Existing Configs List -->
		<section
			use:dndzone={{
				items: userSettings.state.value.configs,
				flipDurationMs: 200,
				dropTargetStyle: {
					outline: 'none',
					border: 'none'
				}
			}}
			onconsider={handleConsider}
			onfinalize={handleFinalize}
			class="space-y-4 rounded-lg p-2"
		>
			{#each userSettings.state.value.configs as config, index (config.id)}
				<div class="rounded-lg border-[1px] border-base-300">
					{#if editingConfig === index.toString()}
						<div
							class="rounded-lg border border-base-300 bg-base-100/50 p-4"
							in:slide={{ duration: 200 }}
							out:slide={{ duration: 200 }}
						>
							<form
								class="space-y-4"
								onsubmit={(e) => {
									e.preventDefault();
									const form = e.target as HTMLFormElement;
									if (form.checkValidity()) {
										saveConfig();
									}
								}}
							>
								{#if config.type === 'nougat'}
									{@render nougatForm(config, false)}
								{:else if config.type === 'ocr'}
									{@render ocrForm(config, false)}
								{:else}
									{@render llmForm(config, false)}
								{/if}

								<div class="mt-2 flex justify-end gap-2">
									<button
										type="button"
										class="inline-flex items-center gap-2 rounded-md border border-base-300 bg-base-200/50 px-3 py-1.5 text-sm font-medium transition-colors hover:bg-base-200"
										onclick={cancelEditing}
									>
										<X class="size-4 text-base-content/70" />
										Cancel
									</button>
									<button
										type="submit"
										class="inline-flex items-center gap-2 rounded-md border border-success/20 bg-success/10 px-3 py-1.5 text-sm font-medium text-success transition-colors hover:bg-success/20"
									>
										<Save class="size-4" />
										Save
									</button>
								</div>
							</form>
						</div>
					{:else}
						{@render configListItem(config, index)}
					{/if}
				</div>
			{/each}
		</section>
	</div>
</div>

{#snippet configListItem(config: any, index: number)}
	<div
		class={cn(
			'rounded-lg border border-base-300 bg-base-100/50 p-3',
			'flex h-14 items-center justify-between',
			'data-[saving=true]:border-success/20 data-[saving=true]:bg-success/10'
		)}
		data-saving={saveConfirmationId === config.id || saveConfirmationIndex === index}
	>
		<div class="flex w-full items-center gap-3">
			<div
				class="cursor-grab opacity-100"
				tabindex={0}
				role="button"
				aria-label="drag-handle"
				onmousedown={startDrag}
			>
				<GripVertical class="size-4 opacity-50 hover:opacity-100" />
			</div>
			<div class="min-w-0 flex-1">
				<div class="flex items-center gap-2">
					{#key index}
						<div
							class="badge badge-sm bg-base-200 text-center font-mono text-xs"
							style={`color: ${config.color}; border-color: ${config.color}; background-color: ${config.color}20`}
							in:fade={{ duration: 200 }}
						>
							{index + 1}
						</div>
					{/key}
					<h3 class="truncate text-sm font-medium">
						{config.name}
					</h3>
					<!-- Model Type Icon -->
					{#if config.type === 'nougat'}
						<div
							class="flex h-4 w-4 items-center justify-center rounded bg-orange-100 text-orange-600"
						>
							<FileText class="h-2.5 w-2.5" />
						</div>
					{:else if config.type === 'ocr'}
						<div class="flex h-4 w-4 items-center justify-center rounded bg-blue-100 text-blue-600">
							<Camera class="h-2.5 w-2.5" />
						</div>
					{:else if config.type === 'llm_endpoint'}
						<div
							class="flex h-4 w-4 items-center justify-center rounded bg-purple-100 text-purple-600"
						>
							<Brain class="h-2.5 w-2.5" />
						</div>
					{/if}
					<!-- Shortcut info -->
					{#if config.shortcutKey}
						<span class="text-xs text-base-content/60">·</span>
						<kbd class="kbd kbd-sm !p-0.5 !px-1.5 font-sans !text-xs"
							>{formatShortcut(config.shortcutKey)}</kbd
						>
					{:else}
						<span class="text-xs text-base-content/60">· no shortcut</span>
					{/if}
				</div>
			</div>
			<div class="flex gap-2">
				{#if saveConfirmationId === config.id || saveConfirmationIndex === index}
					<span class="inline-flex items-center text-success" out:scale={{ duration: 200 }}>
						<Check class="size-4" />
					</span>
				{:else}
					<button
						class="inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm transition-colors hover:bg-base-200/50"
						onclick={() => startEditing(index.toString())}
						in:scale={{ duration: 200, delay: 200 }}
					>
						<Pencil class="size-4 text-base-content/70" />
					</button>
					<button
						class="inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm text-error transition-colors hover:bg-error/10"
						onclick={() => deleteConfig(index)}
						in:scale={{ duration: 200, delay: 250 }}
					>
						<Trash2 class="size-4" />
					</button>
				{/if}
			</div>
		</div>
	</div>
{/snippet}

{#snippet nougatForm(config: ConfigNougat, isNew: boolean)}
	<div class="flex gap-4">
		<div class="form-control flex-1">
			<label class="label" for={isNew ? 'new-config-name' : 'config-name'}>
				<span class="label-text">Name</span>
			</label>
			<input
				id={isNew ? 'new-config-name' : 'config-name'}
				type="text"
				placeholder="Name"
				class={inputStyles}
				required
				bind:value={config.name}
			/>
		</div>
		<div class="form-control w-24">
			<label class="label" for={isNew ? 'new-config-color' : 'config-color'}>
				<span class="label-text">Color</span>
			</label>
			<input
				id={isNew ? 'new-config-color' : 'config-color'}
				type="color"
				class="h-9 w-full rounded-md border border-base-300 bg-base-200/50 p-1 transition-colors focus:border-primary/20 focus:bg-base-100"
				bind:value={config.color}
			/>
		</div>
	</div>

	<div class="form-control">
		<label class="label" for={isNew ? 'new-config-shortcut' : 'config-shortcut'}>
			<span class="label-text">Shortcut</span>
			<span class="label-text-alt">Press shortcut to trigger this config</span>
		</label>
		<InputShortcut bind:value={config.shortcutKey} />
	</div>

	<div class="form-control">
		<label class="label" for="model-name">
			<span class="label-text">Model Name</span>
			<span class="label-text-alt">Huggingface model path</span>
		</label>
		<input
			id="model-name"
			type="text"
			placeholder="Model Name"
			class={inputStyles}
			required
			pattern="^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$"
			bind:value={config.nougat_config.hf_model_name}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="temperature">
			<span class="label-text">Temperature ({config.nougat_config.temperature})</span>
			<span class="label-text-alt">Controls randomness</span>
		</label>
		<input
			id="temperature"
			type="range"
			min="0"
			max="1"
			step="0.1"
			class="range range-xs"
			bind:value={config.nougat_config.temperature}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="top-p">
			<span class="label-text">Top P ({config.nougat_config.top_p})</span>
			<span class="label-text-alt">Controls diversity</span>
		</label>
		<input
			id="top-p"
			type="range"
			min="0"
			max="1"
			step="0.1"
			class="range range-xs"
			bind:value={config.nougat_config.top_p}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="repetition-penalty">
			<span class="label-text">Repetition Penalty ({config.nougat_config.repetition_penalty})</span>
			<span class="label-text-alt">Prevents repetitive text</span>
		</label>
		<input
			id="repetition-penalty"
			type="range"
			min="1"
			max="2"
			step="0.1"
			class="range range-xs"
			bind:value={config.nougat_config.repetition_penalty}
		/>
	</div>
{/snippet}

{#snippet ocrForm(config: ConfigOCR, isNew: boolean)}
	<div class="flex gap-4">
		<div class="form-control flex-1">
			<label class="label" for={isNew ? 'new-config-name' : 'config-name'}>
				<span class="label-text">Name</span>
			</label>
			<input
				id={isNew ? 'new-config-name' : 'config-name'}
				type="text"
				placeholder="Name"
				class={inputStyles}
				required
				bind:value={config.name}
			/>
		</div>
		<div class="form-control w-24">
			<label class="label" for={isNew ? 'new-config-color' : 'config-color'}>
				<span class="label-text">Color</span>
			</label>
			<input
				id={isNew ? 'new-config-color' : 'config-color'}
				type="color"
				class="h-9 w-full rounded-md border border-base-300 bg-base-200/50 p-1 transition-colors focus:border-primary/20 focus:bg-base-100"
				bind:value={config.color}
			/>
		</div>
	</div>

	<div class="form-control">
		<label class="label" for={isNew ? 'new-config-shortcut' : 'config-shortcut'}>
			<span class="label-text">Shortcut</span>
			<span class="label-text-alt">Press shortcut to trigger this config</span>
		</label>
		<InputShortcut bind:value={config.shortcutKey} />
	</div>

	<div class="form-control">
		<label class="label" for="detection-url">
			<span class="label-text">Detection Model URL</span>
			<span class="label-text-alt">URL to the text detection model</span>
		</label>
		<input
			id="detection-url"
			type="text"
			placeholder="https://..."
			pattern="^https?://.*"
			class={inputStyles}
			required
			bind:value={config.ocr_config.detection_model_url}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="recognition-url">
			<span class="label-text">Recognition Model URL</span>
			<span class="label-text-alt">URL to the text recognition model</span>
		</label>
		<input
			id="recognition-url"
			type="text"
			placeholder="https://..."
			pattern="^https?://.*"
			class={inputStyles}
			required
			bind:value={config.ocr_config.recognition_model_url}
		/>
	</div>

	<div class="form-control">
		<label class="flex items-center justify-between">
			<div>
				<span class="text-base font-medium">Disable Line Breaks</span>
				<p class="text-sm text-base-content/60">Disable line breaks in OCR output</p>
			</div>
			<input
				type="checkbox"
				class="toggle toggle-primary"
				bind:checked={config.ocr_config.disableLineBreaks}
			/>
		</label>
	</div>
{/snippet}

{#snippet llmForm(config: ConfigLLMEndpoint, isNew: boolean)}
	<div class="flex gap-4">
		<div class="form-control flex-1">
			<label class="label" for={isNew ? 'new-config-name' : 'config-name'}>
				<span class="label-text">Name</span>
			</label>
			<input
				id={isNew ? 'new-config-name' : 'config-name'}
				type="text"
				placeholder="Name"
				class={inputStyles}
				required
				bind:value={config.name}
			/>
		</div>
		<div class="form-control w-24">
			<label class="label" for={isNew ? 'new-config-color' : 'config-color'}>
				<span class="label-text">Color</span>
			</label>
			<input
				id={isNew ? 'new-config-color' : 'config-color'}
				type="color"
				class="h-9 w-full rounded-md border border-base-300 bg-base-200/50 p-1 transition-colors focus:border-primary/20 focus:bg-base-100"
				bind:value={config.color}
			/>
		</div>
	</div>

	<div class="form-control">
		<label class="label" for={isNew ? 'new-config-shortcut' : 'config-shortcut'}>
			<span class="label-text">Shortcut</span>
			<span class="label-text-alt">Press shortcut to trigger this config</span>
		</label>
		<InputShortcut bind:value={config.shortcutKey} />
	</div>

	<div class="form-control">
		<label class="label" for="api-key">
			<span class="label-text">API Key</span>
			<span class="label-text-alt">API key for the LLM endpoint (optional)</span>
		</label>
		<input
			id="api-key"
			type="password"
			placeholder="API Key (optional)"
			class={inputStyles}
			bind:value={config.llm_config.api_key}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="model">
			<span class="label-text">Model</span>
			<span class="label-text-alt">Model name for the LLM endpoint</span>
		</label>
		<input
			id="model"
			type="text"
			placeholder="Model"
			class={inputStyles}
			required
			bind:value={config.llm_config.model}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="endpoint-url">
			<span class="label-text">Endpoint URL</span>
			<span class="label-text-alt">URL to the LLM endpoint</span>
		</label>
		<input
			id="endpoint-url"
			type="text"
			placeholder="https://..."
			pattern="^https?://.*"
			class={inputStyles}
			required
			bind:value={config.llm_config.endpoint_url}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="max-tokens">
			<span class="label-text">Max Tokens</span>
			<span class="label-text-alt">Maximum number of tokens to generate</span>
		</label>
		<input
			id="max-tokens"
			type="number"
			min="1"
			max="10000"
			class={inputStyles}
			required
			bind:value={config.llm_config.max_tokens}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="llm-temperature">
			<span class="label-text">Temperature ({config.llm_config.temperature})</span>
			<span class="label-text-alt">Controls randomness</span>
		</label>
		<input
			id="llm-temperature"
			type="range"
			min="0"
			max="1"
			step="0.1"
			class="range range-xs"
			bind:value={config.llm_config.temperature}
		/>
	</div>

	<div class="form-control">
		<label class="label" for="prompt">
			<span class="label-text">Prompt</span>
			<span class="label-text-alt">Prompt for the LLM</span>
		</label>
		<textarea
			id="prompt"
			placeholder="Prompt"
			class={cn(inputStyles, 'h-24 p-2')}
			required
			bind:value={config.llm_config.prompt}
		></textarea>
	</div>
{/snippet}
