<script lang="ts">
	import type { ShortcutKey, ModifierKey } from '@/types';
	import { X } from 'lucide-svelte';
	import { cn } from '@/utils';
	import { formatShortcut } from '@/shortcut';

	interface Props {
		value: ShortcutKey | null;
		placeholder?: string;
		disabled?: boolean;
	}

	let { value = $bindable(), placeholder = 'Click to set', disabled = false }: Props = $props();
	let isRecording = $state(false);
	let inputRef: HTMLInputElement;

	let displayValue = $derived.by(() => {
		return formatShortcut(value);
	});

	function startRecording() {
		if (disabled) return;
		isRecording = true;
		inputRef?.focus();
	}

	function stopRecording() {
		isRecording = false;
		inputRef?.blur();
	}

	function clearShortcut() {
		value = null;
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (!isRecording) return;
		event.preventDefault();
		event.stopPropagation();

		if (event.key === 'Escape') {
			stopRecording();
			return;
		}

		const modifiers: ModifierKey[] = [];
		if (event.ctrlKey) modifiers.push('Ctrl');
		if (event.altKey) modifiers.push('Alt');
		if (event.shiftKey) modifiers.push('Shift');
		if (event.metaKey) modifiers.push('Super');

		const primaryKey = event.key;
		if (
			primaryKey !== 'Control' &&
			primaryKey !== 'Alt' &&
			primaryKey !== 'Shift' &&
			primaryKey !== 'Super'
		) {
			value = {
				modifiers: modifiers.length > 0 ? modifiers : undefined,
				primaryKey
			};
			stopRecording();
		}
	}

	function handleBlur() {
		stopRecording();
	}
</script>

<div class="flex w-[10rem] w-full flex-col gap-1">
	<div class="flex items-center justify-between gap-2">
		<input
			bind:this={inputRef}
			type="text"
			{placeholder}
			class={cn(
				'h-9 w-full rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors focus:border-primary/20 focus:bg-base-100',
				isRecording && 'input-primary animate-pulse ring-2 ring-primary/20 ring-offset-1'
			)}
			value={isRecording ? 'Recording...' : displayValue}
			onclick={startRecording}
			onkeydown={handleKeyDown}
			onblur={handleBlur}
			readonly
			required={false}
			{disabled}
		/>
		<button
			class={cn(
				'btn btn-square btn-outline btn-sm w-[2rem] flex-none flex-shrink-0',
				value && !disabled && 'visible',
				(!value || disabled) && 'invisible'
			)}
			onclick={(e) => {
				e.preventDefault();
				e.stopPropagation();
				clearShortcut();
			}}
			title="Clear shortcut"
		>
			<X class="h-4 w-4" />
		</button>
	</div>
</div>
