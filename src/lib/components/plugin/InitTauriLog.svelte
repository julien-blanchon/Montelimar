<script lang="ts">
	import { warn, debug, trace, info, error } from '@tauri-apps/plugin-log';

	type ConsoleFunction = 'log' | 'debug' | 'info' | 'warn' | 'error';

	interface Props {
		enabled: boolean;
	}

	const { enabled }: Props = $props();

	function forwardConsole(fnName: ConsoleFunction, logger: (message: string) => Promise<void>) {
		const original = console[fnName];
		console[fnName] = (message: string, ...optionalParams: unknown[]) => {
			original(message, ...optionalParams);
			logger(`${message}`);
		};
		return original; // Return the original function for cleanup
	}

	$effect(() => {
		if (!enabled) return;
		// Store the original functions for cleanup
		const originalFunctions: Record<ConsoleFunction, (...args: any[]) => void> = {
			log: console.log,
			debug: console.debug,
			info: console.info,
			warn: console.warn,
			error: console.error
		};

		// Override console functions
		forwardConsole('log', trace);
		forwardConsole('debug', debug);
		forwardConsole('info', info);
		forwardConsole('warn', warn);
		forwardConsole('error', error);

		return () => {
			// Cleanup logic: Restore original console functions
			console.log = originalFunctions.log;
			console.debug = originalFunctions.debug;
			console.info = originalFunctions.info;
			console.warn = originalFunctions.warn;
			console.error = originalFunctions.error;
		};
	});
</script>
