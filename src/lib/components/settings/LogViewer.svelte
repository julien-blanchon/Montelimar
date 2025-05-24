<script lang="ts">
	let { logs }: { logs: string[] } = $props();

	let isExpanded = $state(false);

	function getLogLevelClass(log: string): string {
		if (log.includes('[ERROR]')) return 'text-red-600 dark:text-red-400';
		if (log.includes('[WARN]')) return 'text-yellow-600 dark:text-yellow-400';
		if (log.includes('[INFO]')) return 'text-blue-600 dark:text-blue-400';
		if (log.includes('[DEBUG]')) return 'text-green-600 dark:text-green-400';
		if (log.includes('[TRACE]')) return 'text-gray-600 dark:text-gray-400';
		return 'text-gray-800 dark:text-gray-200';
	}
</script>

<div class="rounded-lg border border-base-300 bg-base-100/50 p-6">
	<div class="mb-6 flex items-center justify-between">
		<h2 class="text-xl font-semibold">Application Logs</h2>
		<button onclick={() => (isExpanded = !isExpanded)} class="btn btn-outline btn-sm">
			{isExpanded ? 'Collapse' : 'Expand'}
		</button>
	</div>

	{#if isExpanded}
		<div class="rounded-lg border bg-base-200/50">
			<div class="border-b border-base-300 p-3">
				<span class="text-sm font-medium text-base-content">
					{logs.length} log{logs.length !== 1 ? 's' : ''}
				</span>
				{#if logs.length > 500}
					<span class="ml-2 text-xs text-yellow-600 dark:text-yellow-400">
						(Showing last 500 entries)
					</span>
				{/if}
			</div>

			<div class="max-h-96 overflow-y-auto">
				{#if logs.length === 0}
					<div class="p-8 text-center text-base-content/60">No logs available</div>
				{:else}
					<div class="space-y-1 p-3">
						{#each logs as log, i}
							<div class="font-mono text-xs leading-relaxed {getLogLevelClass(log)}">
								{log}
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{:else}
		<div class="text-sm text-base-content/60">
			{logs.length} log entries available. Click "Expand" to view.
		</div>
	{/if}
</div>
