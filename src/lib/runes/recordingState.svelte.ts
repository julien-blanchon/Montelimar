export const recordingState = $state<{
    isRecording: boolean;
    pressedModifiers: Set<string>;
    currentKey: string | null;
    displayText: string;
}>({
    isRecording: false,
    pressedModifiers: new Set(),
    currentKey: null,
    displayText: ''
});
