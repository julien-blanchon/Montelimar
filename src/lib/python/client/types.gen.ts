// This file is auto-generated by @hey-api/openapi-ts

export type HTTPValidationError = {
    detail?: Array<ValidationError>;
};

export type OCRRequest = {
    /**
     * Filename
     */
    filename?: string;
    /**
     * Model name or path
     */
    model?: string;
    /**
     * Sampling temperature
     */
    temperature?: number;
    /**
     * Top-p sampling threshold
     */
    top_p?: number;
    /**
     * Repetition penalty
     */
    repetition_penalty?: (number | null);
};

export type ValidationError = {
    loc: Array<(string | number)>;
    msg: string;
    type: string;
};

export type OcrOcrPostData = {
    body: OCRRequest;
};

export type OcrOcrPostResponse = (string);

export type OcrOcrPostError = (HTTPValidationError);

export type HealthHealthGetResponse = (string);

export type HealthHealthGetError = unknown;