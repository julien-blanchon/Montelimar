// This file is auto-generated by @hey-api/openapi-ts

import { createClient, createConfig, type OptionsLegacyParser } from '@hey-api/client-fetch';
import type { LlmLlmOcrData, LlmLlmOcrError, LlmLlmOcrResponse, OcrOcrData, OcrOcrError, OcrOcrResponse, HealthHealthError, HealthHealthResponse, ShutdownShutdownError, ShutdownShutdownResponse, LogsGetLogsError, LogsGetLogsResponse } from './types.gen';

export const client = createClient(createConfig());

/**
 * Perform OCR on an image using LLM vision capabilities
 * Extract text from images using Large Language Models with vision capabilities like GPT-4 Vision
 */
export const llmLlmOcr = <ThrowOnError extends boolean = false>(options: OptionsLegacyParser<LlmLlmOcrData, ThrowOnError>) => {
    return (options?.client ?? client).post<LlmLlmOcrResponse, LlmLlmOcrError, ThrowOnError>({
        ...options,
        url: '/llm/ocr'
    });
};

/**
 * Perform OCR on an image or PDF
 */
export const ocrOcr = <ThrowOnError extends boolean = false>(options: OptionsLegacyParser<OcrOcrData, ThrowOnError>) => {
    return (options?.client ?? client).post<OcrOcrResponse, OcrOcrError, ThrowOnError>({
        ...options,
        url: '/ocr'
    });
};

/**
 * Health check endpoint
 */
export const healthHealth = <ThrowOnError extends boolean = false>(options?: OptionsLegacyParser<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<HealthHealthResponse, HealthHealthError, ThrowOnError>({
        ...options,
        url: '/health'
    });
};

/**
 * Shutdown endpoint
 */
export const shutdownShutdown = <ThrowOnError extends boolean = false>(options?: OptionsLegacyParser<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<ShutdownShutdownResponse, ShutdownShutdownError, ThrowOnError>({
        ...options,
        url: '/shutdown'
    });
};

/**
 * Get current log file contents
 */
export const logsGetLogs = <ThrowOnError extends boolean = false>(options?: OptionsLegacyParser<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<LogsGetLogsResponse, LogsGetLogsError, ThrowOnError>({
        ...options,
        url: '/logs'
    });
};