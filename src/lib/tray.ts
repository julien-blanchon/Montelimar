function wait(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function changeTrayWithEasing(
    frameCount: number,
    duration: number,
    easing: (t: number) => number,
    setFrame: (frameIndex: number) => void
): Promise<void> {
    const frameDurations = [];

    // Precompute frame delays
    for (let i = 0; i < frameCount - 1; i++) {
        const easedTime = easing(i / (frameCount - 1));
        const nextEasedTime = easing((i + 1) / (frameCount - 1));
        frameDurations.push((nextEasedTime - easedTime) * duration);
    }

    // Apply frames
    for (let i = 0; i < frameCount; i++) {
        setFrame(i);
        if (i < frameDurations.length) {
            await wait(frameDurations[i]);
        }
    }

    setFrame(0); // Reset to the first frame
}
