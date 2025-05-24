<script lang="ts">
	import type { ShortcutKey, ModifierKey } from '@/types';
	import { X } from 'lucide-svelte';
	import { cn } from '@/utils';
	import { formatShortcut, formatRealTimeShortcut, getActualKey } from '@/shortcut';
	import { recordingState } from '@/runes/recordingState.svelte';

	interface Props {
		value: ShortcutKey | null;
		placeholder?: string;
		disabled?: boolean;
	}

	let { value = $bindable(), placeholder = 'Click to set', disabled = false }: Props = $props();
	let inputRef: HTMLInputElement;

	let displayValue = $derived.by(() => {
		if (recordingState.isRecording) {
			return recordingState.displayText || 'Recording...';
		}
		return formatShortcut(value) || '';
	});

	function startRecording() {
		if (disabled) return;
		recordingState.isRecording = true;
		recordingState.pressedModifiers.clear();
		recordingState.currentKey = null;
		recordingState.displayText = '';
		inputRef?.focus();
	}

	function stopRecording() {
		recordingState.isRecording = false;
		recordingState.pressedModifiers.clear();
		recordingState.currentKey = null;
		recordingState.displayText = '';
		inputRef?.blur();
	}

	function clearShortcut() {
		value = null;
	}

	function updateDisplayText() {
		recordingState.displayText = formatRealTimeShortcut(
			recordingState.pressedModifiers,
			recordingState.currentKey
		);
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (!recordingState.isRecording) return;
		event.preventDefault();
		event.stopPropagation();

		// Handle escape to cancel recording
		if (event.key === 'Escape') {
			stopRecording();
			return;
		}

		// Track modifier keys
		const modifiers = new Set<string>();
		if (event.ctrlKey) modifiers.add('Ctrl');
		if (event.altKey) modifiers.add('Alt');
		if (event.shiftKey) modifiers.add('Shift');
		if (event.metaKey) modifiers.add('Super');

		// Update pressed modifiers
		recordingState.pressedModifiers = modifiers;

		// Get the actual key without modifier interference
		const actualKey = getActualKey(event);

		// Check if this is just a modifier key being pressed
		const isModifierKey = ['Control', 'Alt', 'Shift', 'Meta', 'Super'].includes(event.key);

		if (isModifierKey) {
			// Just update the display with current modifiers
			recordingState.currentKey = null;
			updateDisplayText();
		} else {
			// This is a complete shortcut
			recordingState.currentKey = actualKey;
			updateDisplayText();

			// Save the shortcut
			const modifierArray: ModifierKey[] = [];
			if (modifiers.has('Ctrl')) modifierArray.push('Ctrl');
			if (modifiers.has('Alt')) modifierArray.push('Alt');
			if (modifiers.has('Shift')) modifierArray.push('Shift');
			if (modifiers.has('Super')) modifierArray.push('Super');

			value = {
				modifiers: modifierArray.length > 0 ? modifierArray : undefined,
				primaryKey: actualKey
			};

			// Stop recording after a short delay to show the complete shortcut
			setTimeout(() => {
				stopRecording();
			}, 150);
		}
	}

	function handleKeyUp(event: KeyboardEvent) {
		if (!recordingState.isRecording) return;
		event.preventDefault();
		event.stopPropagation();

		// Update modifier state on key up
		const modifiers = new Set<string>();
		if (event.ctrlKey) modifiers.add('Ctrl');
		if (event.altKey) modifiers.add('Alt');
		if (event.shiftKey) modifiers.add('Shift');
		if (event.metaKey) modifiers.add('Super');

		recordingState.pressedModifiers = modifiers;

		// If no modifiers are pressed and no current key, clear the display
		if (modifiers.size === 0 && !recordingState.currentKey) {
			recordingState.displayText = '';
		} else {
			updateDisplayText();
		}
	}

	function handleBlur() {
		// Only stop recording if we're not in the middle of capturing a shortcut
		if (recordingState.isRecording && recordingState.pressedModifiers.size === 0) {
			stopRecording();
		}
	}

	function handleFocus() {
		if (recordingState.isRecording) {
			// Ensure we maintain focus during recording
			inputRef?.focus();
		}
	}
</script>

<div class="flex w-[10rem] flex-col gap-1">
	<div class="flex items-center justify-between gap-2">
		<input
			bind:this={inputRef}
			type="text"
			{placeholder}
			class={cn(
				'h-9 w-full rounded-md border border-base-300 bg-base-200/50 px-3 text-sm transition-colors focus:border-primary/20 focus:bg-base-100',
				recordingState.isRecording &&
					'input-primary animate-pulse ring-2 ring-primary/20 ring-offset-1'
			)}
			value={displayValue}
			data-is-recording={recordingState.isRecording}
			onclick={startRecording}
			onkeydown={handleKeyDown}
			onkeyup={handleKeyUp}
			onblur={handleBlur}
			onfocus={handleFocus}
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
