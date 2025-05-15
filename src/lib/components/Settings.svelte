<script lang="ts">
	import { attachLogger } from '@tauri-apps/plugin-log';
	import type { ConfigNougat, ConfigOCR } from '@/types';
	import { getVersion } from '@tauri-apps/api/app';
	import { userSettings } from '@/runes/user_settings.svelte';
	import {
		Pencil,
		Trash2,
		Save,
		X,
		Check,
		FileText,
		Camera,
		GripVertical,
		Power,
		Volume2,
		Clipboard,
		MenuSquare,
		History,
		Keyboard,
		Bell
	} from 'lucide-svelte';
	import LogosMicrosoftIcon from './icon/logos--microsoft-icon.svg.svelte';
	import LogosTauriIcon from './icon/logos--tauri.svg.svelte';
	import LogosSvelteIcon from './icon/logos--svelte-icon.svg.svelte';
	import LogosRustIcon from './icon/logos--rust.svg.svelte';
	import LogosTailwindcssIcon from './icon/logos--tailwindcss-icon.svg.svelte';
	import { cn } from '@/utils';
	import { dndzone } from 'svelte-dnd-action';
	import InputShortcut from '@/components/custom/InputShortcut.svelte';
	import { formatShortcut } from '@/shortcut';
	import { fade, scale, slide } from 'svelte/transition';
	import { requestPermission } from '@tauri-apps/plugin-notification';
	import { systemSettings } from '@/runes/system_settings.svelte';
	import Confetti from './custom/Confetti.svelte';
	import ToggleConfetti from './custom/ToggleConfetti.svelte';
	import { listen } from '@tauri-apps/api/event';
	import { onMount } from 'svelte';

	let editingConfig: string | null = $state(null);
	let isAddingNew = $state(false);
	let isNougatConfig = $state(true);
	let saveConfirmationId: number | null = $state(null);
	let saveConfirmationIndex: number | null = $state(null);
	let logs: string[] = $state([]);

	function getNextId() {
		return Math.max(0, ...userSettings.state.value.configs.map((c) => c.id)) + 1;
	}

	function pickRandomColor() {
		const NICE_COLORS = [
			'#FF5733', // Vibrant Red-Orange
			'#33FF57', // Fresh Green
			'#3357FF', // Bold Blue
			'#F3FF33', // Bright Yellow
			'#FF33A1', // Pink
			'#33FFF6', // Aqua
			'#9B33FF', // Purple
			'#FF8C33', // Warm Orange
			'#33FF9B', // Mint Green
			'#A1FF33' // Lime
		];
		return NICE_COLORS[Math.floor(Math.random() * NICE_COLORS.length)];
	}

	let newNougatConfig: ConfigNougat = $state({
		id: 0,
		name: '',
		type: 'nougat',
		shortcutKey: null,
		nougat_config: {
			hf_model_name: '',
			temperature: 0.7,
			top_p: 0.9,
			repetition_penalty: 1.1
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

	function handleConsider(e: CustomEvent) {
		const {
			items: newItems,
			info: { source, trigger }
		} = e.detail;
		userSettings.state.value.configs = newItems;
	}

	function handleFinalize(e: CustomEvent) {
		const {
			items: newItems,
			info: { source }
		} = e.detail;
		userSettings.state.value.configs = newItems;
	}

	function startDrag(e: Event) {
		e.preventDefault();
	}

	function onDragEnd() {
		// TODO: Implement
	}

	function startEditing(configId: string) {
		editingConfig = configId;
	}

	function cancelEditing() {
		editingConfig = null;
		isAddingNew = false;
		newNougatConfig = {
			id: 0,
			name: '',
			type: 'nougat',
			shortcutKey: null,
			nougat_config: {
				hf_model_name: '',
				temperature: 0.7,
				top_p: 0.9,
				repetition_penalty: 1.1
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
	}

	function saveConfig() {
		if (isAddingNew) {
			const config = isNougatConfig ? newNougatConfig : newOCRConfig;
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

	let rating = $state(3);

	$effect(() => {
		let unlistenPromise = attachLogger(({ level, message }) => {
			logs = [...logs, `[${level}] ${message}`];
			if (logs.length > 500) logs = logs.slice(-500);
		});

		// Clean up listener on unmount
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});
</script>

<div class="h-[640px] w-full space-y-6 overflow-scroll px-4 py-2">
	<!-- Models List -->
	<div class="rounded-lg border border-base-300 bg-base-100/50 p-6">
		<div class="h-full overflow-y-scroll">
			<div class="mb-2 flex items-center justify-between">
				<h2 class="text-xl font-semibold">Installed Models</h2>
				<div class="flex gap-2">
					<button
						class={cn(
							'group',
							'inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
							'border border-base-300 bg-base-200/50 hover:bg-base-300/80',
							'disabled:cursor-not-allowed disabled:opacity-50',
							'data-[active=true]:border-primary/20 data-[active=true]:bg-primary/10 data-[active=true]:text-primary'
						)}
						data-active={isNougatConfig && isAddingNew}
						onclick={() => {
							if (!isAddingNew) {
								isNougatConfig = true;
								isAddingNew = true;
							} else {
								cancelEditing();
							}
						}}
						disabled={isAddingNew && !isNougatConfig}
					>
						<FileText class="size-4 text-base-content/70 group-data-[active=true]:text-primary" />
						Add Nougat
					</button>
					<button
						class={cn(
							'group',
							'inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
							'border border-base-300 bg-base-200/50 hover:bg-base-300/80',
							'disabled:cursor-not-allowed disabled:opacity-50',
							'data-[active=true]:border-primary/20 data-[active=true]:bg-primary/10 data-[active=true]:text-primary'
						)}
						data-active={!isNougatConfig && isAddingNew}
						onclick={() => {
							if (!isAddingNew) {
								isNougatConfig = false;
								isAddingNew = true;
							} else {
								cancelEditing();
							}
						}}
						disabled={isAddingNew && isNougatConfig}
					>
						<Camera class="size-4 text-base-content/70 group-data-[active=true]:text-primary" />
						Add OCRs
					</button>
				</div>
			</div>

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
							const form = document.querySelector('form');
							if (form?.checkValidity()) {
								saveConfig();
							}
						}}
					>
						{#if isNougatConfig}
							<div class="flex gap-4">
								<div class="form-control flex-1">
									<label class="label" for="new-config-name">
										<span class="label-text">Name</span>
									</label>
									<input
										id="new-config-name"
										type="text"
										placeholder="Name"
										class={cn(
											'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
											'focus:border-primary/20 focus:bg-base-100',
											'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
											'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
											'w-full'
										)}
										required
										bind:value={newNougatConfig.name}
									/>
								</div>
								<div class="form-control w-24">
									<label class="label" for="new-config-color">
										<span class="label-text">Color</span>
									</label>
									<input
										id="new-config-color"
										type="color"
										class="h-9 w-full rounded-md border border-base-300 bg-base-200/50 p-1 transition-colors focus:border-primary/20 focus:bg-base-100"
										bind:value={newNougatConfig.color}
									/>
								</div>
							</div>

							<!-- Shortcut Key -->
							<div class="form-control">
								<label class="label" for="new-config-shortcut">
									<span class="label-text">Shortcut</span>
									<span class="label-text-alt">Press shortcut to trigger this config</span>
								</label>
								<InputShortcut bind:value={newNougatConfig.shortcutKey} />
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
									class={cn(
										'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
										'focus:border-primary/20 focus:bg-base-100',
										'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
										'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
										'w-full'
									)}
									required
									pattern="^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$"
									bind:value={newNougatConfig.nougat_config.hf_model_name}
								/>
							</div>
							<div class="form-control">
								<label class="label" for="new-temperature">
									<span class="label-text"
										>Temperature ({newNougatConfig.nougat_config.temperature})</span
									>
									<span class="label-text-alt">Controls randomness</span>
								</label>
								<input
									id="new-temperature"
									type="range"
									min="0"
									max="1"
									step="0.1"
									class="range range-xs"
									bind:value={newNougatConfig.nougat_config.temperature}
								/>
							</div>
							<div class="form-control">
								<label class="label" for="new-top-p">
									<span class="label-text">Top P ({newNougatConfig.nougat_config.top_p})</span>
									<span class="label-text-alt">Controls diversity</span>
								</label>
								<input
									id="new-top-p"
									type="range"
									min="0"
									max="1"
									step="0.1"
									class="range range-xs"
									bind:value={newNougatConfig.nougat_config.top_p}
								/>
							</div>
							<div class="form-control">
								<label class="label" for="new-repetition-penalty">
									<span class="label-text">
										Repetition Penalty ({newNougatConfig.nougat_config.repetition_penalty})
									</span>
									<span class="label-text-alt">Prevents repetitive text</span>
								</label>
								<input
									id="new-repetition-penalty"
									type="range"
									min="1"
									max="2"
									step="0.1"
									class="range range-xs"
									bind:value={newNougatConfig.nougat_config.repetition_penalty}
								/>
							</div>
						{:else}
							<div class="flex gap-4">
								<div class="form-control flex-1">
									<label class="label" for="new-config-name">
										<span class="label-text">Name</span>
									</label>
									<input
										id="new-config-name"
										type="text"
										placeholder="Name"
										class={cn(
											'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
											'focus:border-primary/20 focus:bg-base-100',
											'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
											'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
											'w-full'
										)}
										required
										bind:value={newOCRConfig.name}
									/>
								</div>
								<div class="form-control w-24">
									<label class="label" for="new-config-color">
										<span class="label-text">Color</span>
									</label>
									<input
										id="new-config-color"
										type="color"
										class="h-9 w-full rounded-md border border-base-300 bg-base-200/50 p-1 transition-colors focus:border-primary/20 focus:bg-base-100"
										bind:value={newOCRConfig.color}
									/>
								</div>
							</div>

							<!-- Shortcut Key -->
							<div class="form-control">
								<label class="label" for="new-config-shortcut">
									<span class="label-text">Shortcut</span>
									<span class="label-text-alt">Press shortcut to trigger this config</span>
								</label>
								<InputShortcut bind:value={newOCRConfig.shortcutKey} />
							</div>

							<div class="form-control">
								<label class="label" for="new-detection-url">
									<span class="label-text">Detection Model URL</span>
									<span class="label-text-alt">URL to the text detection model</span>
								</label>
								<input
									id="new-detection-url"
									type="text"
									placeholder="https://..."
									pattern="^https?://.*"
									class={cn(
										'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
										'focus:border-primary/20 focus:bg-base-100',
										'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
										'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
										'w-full'
									)}
									required
									bind:value={newOCRConfig.ocr_config.detection_model_url}
								/>
							</div>
							<div class="form-control">
								<label class="label" for="new-recognition-url">
									<span class="label-text">Recognition Model URL</span>
									<span class="label-text-alt">URL to the text recognition model</span>
								</label>
								<input
									id="new-recognition-url"
									type="text"
									placeholder="https://..."
									pattern="^https?://.*"
									class={cn(
										'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
										'focus:border-primary/20 focus:bg-base-100',
										'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
										'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
										'w-full'
									)}
									required
									bind:value={newOCRConfig.ocr_config.recognition_model_url}
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
										bind:checked={newOCRConfig.ocr_config.disableLineBreaks}
									/>
								</label>
							</div>
						{/if}

						<div class="flex justify-end gap-2">
							<button
								type="button"
								class="inline-flex items-center gap-2 rounded-md border border-base-300 bg-base-200/50 px-3 py-1.5 text-sm font-medium transition-colors hover:bg-base-200"
								onclick={cancelEditing}
								disabled={!isAddingNew}
							>
								<X class="size-4 text-base-content/70" />
								Cancel
							</button>
							<button
								type="submit"
								class="inline-flex items-center gap-2 rounded-md border border-success/20 bg-success/10 px-3 py-1.5 text-sm font-medium text-success transition-colors hover:bg-success/20"
								disabled={!isAddingNew}
							>
								<Check class="size-4" />
								Add
							</button>
						</div>
					</form>
				</div>
			{/if}

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
										const form = document.querySelector('form');
										if (form?.checkValidity()) {
											saveConfig();
										}
									}}
								>
									<div class="flex gap-4">
										<div class="form-control flex-1">
											<label class="label" for="config-name">
												<span class="label-text">Name</span>
											</label>
											<input
												id="config-name"
												type="text"
												placeholder="Name"
												minlength="1"
												class={cn(
													'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
													'focus:border-primary/20 focus:bg-base-100',
													'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
													'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
													'w-full'
												)}
												required
												bind:value={config.name}
											/>
										</div>
										<div class="form-control w-24">
											<label class="label" for="config-color">
												<span class="label-text">Color</span>
											</label>
											<input
												id="config-color"
												type="color"
												class="h-9 w-full rounded-md border border-base-300 bg-base-200/50 p-1 transition-colors focus:border-primary/20 focus:bg-base-100"
												bind:value={config.color}
											/>
										</div>
									</div>

									<!-- Shortcut Key -->
									<div class="form-control">
										<label class="label" for="config-shortcut">
											<span class="label-text">Shortcut</span>
											<span class="label-text-alt">Press shortcut to trigger this config</span>
										</label>
										<InputShortcut bind:value={config.shortcutKey} />
									</div>

									{#if config.type === 'nougat'}
										<div class="space-y-4">
											<div class="form-control">
												<label class="label" for="model-name">
													<span class="label-text">Model Name</span>
													<span class="label-text-alt">Huggingface model path</span>
												</label>
												<input
													id="model-name"
													type="text"
													placeholder="Model Name"
													class={cn(
														'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
														'focus:border-primary/20 focus:bg-base-100',
														'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
														'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
														'w-full'
													)}
													required
													bind:value={config.nougat_config.hf_model_name}
													pattern="^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$"
												/>
											</div>
											<div class="form-control">
												<label class="label" for="new-temperature">
													<span class="label-text"
														>Temperature ({config.nougat_config.temperature})</span
													>
													<span class="label-text-alt">Controls randomness</span>
												</label>
												<input
													id="new-temperature"
													type="range"
													min="0"
													max="1"
													step="0.1"
													class="range range-xs"
													bind:value={config.nougat_config.temperature}
												/>
											</div>
											<div class="form-control">
												<label class="label" for="new-top-p">
													<span class="label-text">Top P ({config.nougat_config.top_p})</span>
													<span class="label-text-alt">Controls diversity</span>
												</label>
												<input
													id="new-top-p"
													type="range"
													min="0"
													max="1"
													step="0.1"
													class="range range-xs"
													bind:value={config.nougat_config.top_p}
												/>
											</div>
											<div class="form-control">
												<label class="label" for="new-repetition-penalty">
													<span class="label-text">
														Repetition Penalty ({config.nougat_config.repetition_penalty})
													</span>
													<span class="label-text-alt">Prevents repetitive text</span>
												</label>
												<input
													id="new-repetition-penalty"
													type="range"
													min="1"
													max="2"
													step="0.1"
													class="range range-xs"
													bind:value={config.nougat_config.repetition_penalty}
												/>
											</div>
										</div>
									{:else}
										<div class="space-y-4">
											<div class="form-control">
												<label class="label" for="detection-url">
													<span class="label-text">Detection Model URL</span>
													<span class="label-text-alt">URL to the text detection model</span>
												</label>
												<input
													id="detection-url"
													type="text"
													placeholder="https://..."
													class={cn(
														'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
														'focus:border-primary/20 focus:bg-base-100',
														'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
														'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
														'w-full'
													)}
													required
													pattern="^https?://.*"
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
													required
													pattern="^https?://.*"
													class={cn(
														'h-9 rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors',
														'focus:border-primary/20 focus:bg-base-100',
														'disabled:cursor-not-allowed disabled:bg-base-200 disabled:opacity-50',
														'peer [&:user-invalid]:border-error/50 [&:user-invalid]:focus:border-error/50',
														'w-full'
													)}
													bind:value={config.ocr_config.recognition_model_url}
												/>
											</div>
											<div class="form-control">
												<label class="flex items-center justify-between">
													<div>
														<span class="text-base font-medium">Disable Line Breaks</span>
														<p class="text-sm text-base-content/60">
															Disable line breaks in OCR output
														</p>
													</div>
													<input
														type="checkbox"
														class="toggle toggle-primary"
														bind:checked={config.ocr_config.disableLineBreaks}
													/>
												</label>
											</div>
										</div>
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
							{@const isEditing = editingConfig === index.toString()}
							<!-- out:scale|global={{ duration: isEditing ? 0 : 200 }} -->
							<div
								class={cn(
									'rounded-lg border border-base-300 bg-base-100/50 p-3',
									'flex h-14 items-center justify-between',
									'data-[saving=true]:border-success/20 data-[saving=true]:bg-success/10'
								)}
								data-saving={saveConfirmationId === config.id || saveConfirmationIndex === index}
								data-editing={isEditing}
							>
								<div class="flex items-center gap-3">
									<div
										class="cursor-grab opacity-100"
										tabindex={0}
										id="drag-handle"
										aria-label="drag-handle"
										role="button"
										onmousedown={startDrag}
										onmouseup={onDragEnd}
										ontouchstart={startDrag}
										ontouchend={onDragEnd}
									>
										<GripVertical class="size-4 opacity-50 hover:opacity-100" />
									</div>
									<div class="flex-1">
										<div class="flex w-full items-center gap-2">
											{#key index}
												<div
													class="badge badge-sm bg-base-200 text-center font-mono text-xs"
													style={`color: ${config.color}; border-color: ${config.color}; background-color: ${config.color}20`}
													in:fade={{ duration: 200 }}
												>
													{index + 1}
												</div>
											{/key}
											<h3 class="w-[7rem] truncate text-xs font-medium">
												{config.name}
											</h3>
											<div class="flex w-[7rem] items-center gap-1">
												{#if config.shortcutKey}
													<span class="text-xs text-base-content/60">·</span>
													<span class="text-xs text-base-content/60">press</span>
													<kbd class="kbd kbd-sm !p-1 !px-3 font-sans !tracking-widest"
														>{formatShortcut(config.shortcutKey)}</kbd
													>
												{:else}
													<span class="text-xs text-base-content/60">· no shortcut set</span>
												{/if}
											</div>
										</div>
									</div>
									<div class="flex gap-2">
										{#if saveConfirmationId === config.id || saveConfirmationIndex === index}
											<span
												class="inline-flex items-center text-success"
												out:scale={{ duration: 200 }}
											>
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
												in:scale={{ duration: 200, delay: 200 + 50 }}
											>
												<Trash2 class="size-4" />
											</button>
										{/if}
									</div>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</section>
		</div>
	</div>

	<!-- General Settings -->
	<div class="rounded-lg border border-base-300 bg-base-100/50 p-6">
		<div class="space-y-4">
			<h2 class="text-xl font-semibold">General Settings</h2>
			<div class="space-y-4">
				<!-- Start at Login -->
				<div class="form-control">
					<label class="flex items-center justify-between gap-4">
						<div class="flex flex-row gap-3">
							<div class="flex h-5 w-5 items-center justify-center">
								<Power class="h-4 w-4 text-base-content/70" />
							</div>
							<div class="flex min-w-0 flex-col gap-1">
								<span class="text-base font-medium leading-none">Start at Login</span>
								<span class="line-clamp-2 text-sm text-base-content/60"
									>Launch the app automatically when your system starts up</span
								>
							</div>
						</div>
						<div class="flex w-[10rem] flex-shrink-0 justify-end">
							<input
								type="checkbox"
								class="toggle toggle-primary"
								bind:checked={userSettings.state.value.startAtLogin}
							/>
						</div>
					</label>
				</div>

				<!-- Play Sound -->
				<div class="form-control">
					<label class="flex items-center justify-between gap-4">
						<div class="flex flex-row gap-3">
							<div class="flex h-5 w-5 items-center justify-center">
								<Volume2 class="h-4 w-4 text-base-content/70" />
							</div>
							<div class="flex min-w-0 flex-col gap-1">
								<span class="text-base font-medium leading-none">Play Sound</span>
								<span class="line-clamp-2 text-sm text-base-content/60"
									>Play a subtle sound effect when capturing screenshots</span
								>
							</div>
						</div>
						<div class="flex w-[10rem] flex-shrink-0 justify-end">
							<input
								type="checkbox"
								class="toggle toggle-primary"
								bind:checked={userSettings.state.value.playSound}
							/>
						</div>
					</label>
				</div>

				<!-- Auto Copy to Clipboard -->
				<div class="form-control">
					<label class="flex items-center justify-between gap-4">
						<div class="flex flex-row gap-3">
							<div class="flex h-5 w-5 items-center justify-center">
								<Clipboard class="h-4 w-4 text-base-content/70" />
							</div>
							<div class="flex min-w-0 flex-col gap-1">
								<span class="text-base font-medium leading-none">Auto Copy to Clipboard</span>
								<span class="line-clamp-2 text-sm text-base-content/60"
									>Automatically copy extracted text to your clipboard</span
								>
							</div>
						</div>
						<div class="flex w-[10rem] flex-shrink-0 justify-end">
							<input
								type="checkbox"
								class="toggle toggle-primary"
								bind:checked={userSettings.state.value.autoCopyToClipboard}
							/>
						</div>
					</label>
				</div>

				<!-- Show Menu Bar Icon -->
				<!-- <div class="form-control">
					<label class="flex items-center justify-between gap-4">
						<div class="flex flex-row gap-3">
							<div class="flex h-5 w-5 items-center justify-center">
								<MenuSquare class="h-4 w-4 text-base-content/70" />
							</div>
							<div class="flex min-w-0 flex-col gap-1">
								<span class="text-base font-medium leading-none">Show Menu Bar Icon</span>
								<span class="line-clamp-2 text-sm text-base-content/60"
									>Display an icon in your menu bar for quick access</span
								>
							</div>
						</div>
						<div class="flex w-[10rem] flex-shrink-0 justify-end">
							<input
								type="checkbox"
								class="toggle toggle-primary"
								bind:checked={userSettings.state.value.showMenuBarIcon}
							/>
						</div>
					</label>
				</div> -->

				<!-- Disable History -->
				<div class="form-control">
					<label class="flex items-center justify-between gap-4">
						<div class="flex flex-row gap-3">
							<div class="flex h-5 w-5 items-center justify-center">
								<History class="h-4 w-4 text-base-content/70" />
							</div>
							<div class="flex min-w-0 flex-col gap-1">
								<span class="text-base font-medium leading-none">Disable History</span>
								<span class="line-clamp-2 text-sm text-base-content/60"
									>Don't save any capture history to protect your privacy</span
								>
							</div>
						</div>
						<div class="flex w-[10rem] flex-shrink-0 justify-end">
							<input
								type="checkbox"
								class="toggle toggle-primary"
								bind:checked={userSettings.state.value.disableHistory}
							/>
						</div>
					</label>
				</div>

				<!-- Global Shortcut -->
				<div class="form-control">
					<label class="flex items-center justify-between gap-4">
						<div class="flex flex-row gap-3">
							<div class="flex h-5 w-5 items-center justify-center">
								<Keyboard class="h-4 w-4 text-base-content/70" />
							</div>
							<div class="flex min-w-0 flex-col gap-1">
								<span class="text-base font-medium leading-none">Global Capture Shortcut</span>
								<span class="line-clamp-2 text-sm text-base-content/60"
									>Use this keyboard shortcut from anywhere to capture a selected area</span
								>
							</div>
						</div>
						<div class="w-[15rem]">
							<InputShortcut bind:value={userSettings.state.value.globalShortcut} />
						</div>
					</label>
				</div>

				<!-- Show notification on capture -->
				<div class="form-control">
					<label class="flex items-center justify-between gap-4">
						<div class="flex flex-row gap-3">
							<div class="flex h-5 w-5 items-center justify-center">
								<div class="flex h-5 w-5 items-center justify-center">
									<Bell class="h-4 w-4 text-base-content/70" />
								</div>
							</div>
							<div class="flex min-w-0 flex-col gap-1">
								<span class="text-base font-medium leading-none">Show Notification on Capture</span>
								<span class="line-clamp-2 text-sm text-base-content/60"
									>Show a notification with the result of the capture</span
								>
							</div>
						</div>
						<div class="flex w-[10rem] flex-shrink-0 justify-end">
							<input
								type="checkbox"
								class="toggle toggle-primary"
								bind:checked={userSettings.state.value.showNotificationOnCapture}
							/>
						</div>
					</label>
				</div>

				<!-- Notification Permission -->
				<div class="form-control">
					<label class="flex items-center justify-between gap-4">
						<div class="flex flex-row gap-3">
							<div class="flex h-5 w-5 items-center justify-center">
								<div class="flex h-5 w-5 items-center justify-center">
									<Bell class="h-4 w-4 text-base-content/70" />
								</div>
							</div>
							<div class="flex min-w-0 flex-col gap-1">
								<span class="text-base font-medium leading-none">Notification Permission</span>
								<span class="line-clamp-2 text-sm text-base-content/60"
									>Allow the app to send you notifications</span
								>
							</div>
						</div>
						<div class="flex w-[10rem] flex-shrink-0 justify-end">
							{#if systemSettings.notificationPermissionGranted}
								<span
									class="inline-flex items-center gap-2 rounded-md border border-success/20 bg-success/10 px-3 py-1.5 text-sm font-medium text-success"
								>
									<Check class="size-4" />
									Granted
								</span>
							{:else}
								<button
									class="inline-flex items-center gap-2 rounded-md border border-base-300 bg-base-200/50 px-3 py-1.5 text-sm font-medium transition-colors hover:bg-base-300/80"
									onclick={async () => {
										const permission = await requestPermission();
										systemSettings.notificationPermissionGranted = permission === 'granted';
									}}
								>
									<Bell class="size-4 text-base-content/70" />
									Request
								</button>
							{/if}
						</div>
					</label>
				</div>
			</div>
		</div>
	</div>

	<!-- Footer/About -->
	<div class="rounded-lg border border-base-300 bg-base-100/50 p-6">
		<div class="space-y-4">
			<h2 class="text-xl font-semibold">About</h2>
			<div class="space-y-6">
				<div class="flex flex-col gap-1">
					<h3 class="text-base font-medium">Montelimar - OCR</h3>
					<p class="text-sm text-base-content/60">A OCR toolbox integrated in your Mac</p>
				</div>

				<div class="flex flex-col gap-2">
					<div class="flex items-center gap-2 text-sm">
						<span class="font-medium">Version</span>
						{#await getVersion()}
							<span class="text-base-content/60">Loading version...</span>
						{:then version}
							<span class="text-base-content/60">{version}</span>
						{/await}
					</div>
					<div class="flex items-center gap-2 text-sm">
						<span class="font-medium">Created by</span>
						<a
							href="https://twitter.com/JulienBlanchon"
							target="_blank"
							rel="noopener noreferrer"
							class="text-primary hover:underline">Julien Blanchon</a
						>
					</div>
					<div class="flex items-center gap-2 text-sm">
						<span class="font-medium">Source Code</span>
						<a
							href="https://github.com/julien-blanchon/"
							target="_blank"
							rel="noopener noreferrer"
							class="text-primary hover:underline">GitHub</a
						>
					</div>
				</div>

				<div class="space-y-2">
					<p class="text-sm font-medium">Built with</p>
					<div class="flex flex-wrap gap-2">
						<a
							href="https://tauri.app"
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
						>
							<!-- <Icon icon="logos:tauri" class="size-4" /> -->
							<LogosTauriIcon class="size-4" />
						</a>
						<a
							href="https://svelte.dev"
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
						>
							<!-- <Icon icon="logos:svelte-icon" class="size-4" /> -->
							<LogosSvelteIcon class="size-4" />
							Svelte
						</a>
						<a
							href="https://www.rust-lang.org"
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
						>
							<!-- <Icon icon="logos:rust" class="size-4" /> -->
							<LogosRustIcon class="size-4" />
							Rust
						</a>
						<a
							href="https://tailwindcss.com"
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
						>
							<!-- <Icon icon="logos:tailwindcss-icon" class="size-4" /> -->
							<LogosTailwindcssIcon class="size-4" />
							Tailwind CSS
						</a>
						<a
							href="https://github.com/microsoft/fluentui-system-icons/"
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex cursor-pointer items-center gap-2 rounded-full bg-base-200/50 px-3 py-1.5 text-xs font-medium hover:bg-base-300"
						>
							<!-- <Icon icon="logos:microsoft-icon" class="size-4" /> -->
							<LogosMicrosoftIcon class="size-4" />
							Fluent Icons
						</a>
					</div>
				</div>

				<div class="space-y-2">
					<p class="text-sm font-medium">Special Thanks</p>
					<p class="text-sm text-base-content/60">
						Thanks to the amazing open-source community and all the contributors who made this
						project possible. Special thanks to the Tauri, Svelte, and Rust teams for their
						incredible work.
					</p>
				</div>

				<!-- Rate the app -->
				<div class="flex w-full items-center justify-center gap-2">
					<div class="rating gap-1">
						{#each [1, 2, 3, 4, 5] as i}
							<ToggleConfetti>
								<input
									type="radio"
									name="rating-3"
									onclick={() => {
										rating = i;
									}}
									class={cn(
										'mask mask-heart',
										i === 5 && 'bg-red-400',
										i === 4 && 'bg-orange-400',
										i === 3 && 'bg-yellow-400',
										i === 2 && 'bg-lime-400',
										i === 1 && 'bg-green-400',
										i === 0 && 'bg-emerald-400',
										i > rating && 'opacity-50',
										'transition-transform duration-100 hover:scale-110'
									)}
								/>
								{#snippet confetti()}
									<Confetti
										size={10 + i * 3}
										x={[-0.5, 0.5]}
										y={[0.25, 1]}
										cone
										duration={2000}
										infinite={false}
										amount={i * 20}
										colorArray={['url(/tauri.svg)', 'url(/svelte.svg)', 'url(/rust.svg)`']}
									/>
								{/snippet}
							</ToggleConfetti>
						{/each}
						<!-- <input type="radio" name="rating-3" class="mask mask-heart bg-orange-400" />
						<input type="radio" name="rating-3" class="mask mask-heart bg-yellow-400" />
						<input type="radio" name="rating-3" class="mask mask-heart bg-lime-400" />
						<input type="radio" name="rating-3" class="mask mask-heart bg-green-400" /> -->
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Log Viewer Section -->
	<div class="mt-6 rounded-lg border border-base-300 bg-base-100/50 p-6">
		<h2 class="mb-2 text-xl font-semibold">Application Logs</h2>
		<div class="h-64 overflow-auto rounded bg-base-200 p-2 font-mono text-xs">
			{#if logs.length === 0}
				<div class="text-base-content/60">No logs yet.</div>
			{:else}
				{#each logs as log}
					<div>{log}</div>
				{/each}
			{/if}
		</div>
	</div>
</div>

<!-- 
<svelte:window
	onkeydown={(event) => {
		if (!editingConfig && !isAddingNew) return;
		event.preventDefault();
		event.stopPropagation();
		event.stopImmediatePropagation();

		if (event.key === 'Escape') {
			cancelEditing();
			commands.showMenubarPanel();
			return;
		}
	}}
/> -->

<style>
	:global(*:focus) {
		outline: none;
	}
</style>
