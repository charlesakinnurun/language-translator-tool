import {
  ApiErrorBody,
  TranslationApiError,
  TranslationRequest,
  TranslationResponse,
} from "../types/translation";

// Empty in development: the Vite dev proxy forwards /api to the backend.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/+$/, "");
const TRANSLATE_PATH = "/api/v1/translate";
const REQUEST_TIMEOUT_MS = 30_000;

function extractErrorDetail(
  body: ApiErrorBody | null,
): { code: string; message: string } {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = body.detail;
    if (!Array.isArray(detail)) {
      return { code: detail.code, message: detail.message };
    }
    return {
      code: "validation_error",
      message: detail.map((item) => item.message).join(" "),
    };
  }
  return { code: "unknown_error", message: "An unknown error occurred." };
}

/**
 * Send a translation request to the backend.
 *
 * Rejects with a `TranslationApiError` whose `code` mirrors the backend's
 * machine-readable error codes so the UI can render specific guidance.
 */
export async function translateText(
  request: TranslationRequest,
): Promise<TranslationResponse> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${BASE_URL}${TRANSLATE_PATH}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    let body: ApiErrorBody | null = null;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = null;
    }

    if (!response.ok) {
      const { code, message } = extractErrorDetail(body);
      throw new TranslationApiError(message, code, response.status);
    }

    if (body === null) {
      throw new TranslationApiError(
        "The server returned an unreadable response.",
        "invalid_response",
        response.status,
      );
    }

    return body as unknown as TranslationResponse;
  } catch (error) {
    if (error instanceof TranslationApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new TranslationApiError(
        "The request timed out. Please try again.",
        "timeout",
        0,
      );
    }
    throw new TranslationApiError(
      "Unable to reach the translation service. Check your connection and try again.",
      "network_error",
      0,
    );
  } finally {
    window.clearTimeout(timeoutId);
  }
}