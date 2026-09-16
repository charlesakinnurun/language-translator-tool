import { afterEach, describe, expect, it, vi } from "vitest";

import { translateText } from "../services/translationApi";

function mockFetchResponse(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  });
}

const REQUEST = { text: "Hello", source_language: "en", target_language: "fr" };

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
});

describe("translateText", () => {
  it("posts the request and returns the parsed translation", async () => {
    const fetchMock = mockFetchResponse(200, {
      translated_text: "Bonjour",
      source_language: "en",
      target_language: "fr",
      detected_language: null,
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await translateText(REQUEST);

    expect(result.translated_text).toBe("Bonjour");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/translate"),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(REQUEST),
      }),
    );
  });

  it("maps a validation error into a TranslationApiError", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetchResponse(422, {
        detail: [
          {
            loc: ["body", "text"],
            msg: "text must not be empty or whitespace only",
            type: "value_error",
          },
        ],
      }),
    );

    await expect(
      translateText({ ...REQUEST, text: "" }),
    ).rejects.toMatchObject({ code: "validation_error", status: 422 });
  });

  it("maps a backend service error into a TranslationApiError", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetchResponse(503, {
        detail: {
          code: "provider_unavailable",
          message: "The translation provider is temporarily unavailable.",
        },
      }),
    );

    await expect(translateText(REQUEST)).rejects.toMatchObject({
      code: "provider_unavailable",
      status: 503,
      message: "The translation provider is temporarily unavailable.",
    });
  });

  it("maps network failures to a network_error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("Failed to fetch")),
    );

    await expect(translateText(REQUEST)).rejects.toMatchObject({
      code: "network_error",
      status: 0,
    });
  });

  it("maps aborted requests to a timeout error", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(
        (_url: string, init: RequestInit) =>
          new Promise((_resolve, reject) => {
            const signal = init.signal as AbortSignal;
            signal.addEventListener("abort", () =>
              reject(new DOMException("The operation was aborted.", "AbortError")),
            );
          }),
      ),
    );

    const pending = translateText(REQUEST);
    vi.advanceTimersByTime(30_001);

    await expect(pending).rejects.toMatchObject({ code: "timeout" });
  });

  it("rejects when the server body is not JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => {
          throw new SyntaxError("Unexpected token < in JSON");
        },
      }),
    );

    await expect(translateText(REQUEST)).rejects.toMatchObject({
      code: "invalid_response",
    });
  });
});