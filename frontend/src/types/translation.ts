export interface TranslationRequest {
  text: string;
  source_language: string;
  target_language: string;
}

export interface TranslationResponse {
  translated_text: string;
  source_language: string;
  target_language: string;
  detected_language: string | null;
}

export interface ErrorDetail {
  code: string;
  message: string;
}

export interface ApiErrorBody {
  detail: ErrorDetail | ErrorDetail[];
}

export type ApiErrorCode = string;

export class TranslationApiError extends Error {
  readonly code: ApiErrorCode;
  readonly status: number;

  constructor(message: string, code: ApiErrorCode, status: number) {
    super(message);
    this.name = "TranslationApiError";
    this.code = code;
    this.status = status;
  }
}