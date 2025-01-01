<script lang="ts">
	import { cn } from '@/utils';
	import type { Snippet } from 'svelte';
	import { tick } from 'svelte';

	interface Props {
		children: Snippet;
		confetti: Snippet;
		class?: string;
		toggleOnce?: boolean;
		relative?: boolean;
		active?: boolean;
	}

	let {
		children,
		confetti,
		class: className,
		toggleOnce = false,
		relative = true,
		active = $bindable()
	}: Props = $props();

	async function click() {
		if (toggleOnce) {
			active = !active;
			return;
		}

		active = false;
		await tick();
		active = true;
	}
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<span onclick={click} class={cn('relative', className)}>
	{@render children()}
	{#if active}
		<div class="absolute left-1/2 top-1/2">
			{@render confetti()}
		</div>
	{/if}
</span>
