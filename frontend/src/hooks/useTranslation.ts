import { useCallback, useState } from "react";

import { translateText } from "../services/translationApi";
import { TranslationResponse } from "../types/translation";

const DEFAULT_MAX_TEXT_LENGTH = 5000;
const DEFAULT_SOURCE_LANGUAGE = "en";
const DEFAULT_TARGET_LANGUAGE = "es";

interface UseTranslationOptions {
  maxTextLength?: number;
}

/**
 * Central state machine for the translator UI: input text, language pair,
 * result, loading and error handling.
 */
export function useTranslation(options: UseTranslationOptions = {}) {
  const maxTextLength = options.maxTextLength ?? DEFAULT_MAX_TEXT_LENGTH;
  const [text, setText] = useState("");
  const [sourceLanguage, setSourceLanguage] = useState(DEFAULT_SOURCE_LANGUAGE);
  const [targetLanguage, setTargetLanguage] = useState(DEFAULT_TARGET_LANGUAGE);
  const [result, setResult] = useState<TranslationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const translate = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed) {
      setError("Please enter some text to translate.");
      return;
    }
    if (sourceLanguage === targetLanguage) {
      setError("Source and target languages must be different.");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await translateText({
        text: trimmed,
        source_language: sourceLanguage,
        target_language: targetLanguage,
      });
      setResult(response);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "Translation failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [text, sourceLanguage, targetLanguage]);

  const swapLanguages = useCallback(() => {
    setSourceLanguage(targetLanguage);
    setTargetLanguage(sourceLanguage);
    if (result) {
      setText(result.translated_text);
      setResult(null);
    }
    setError(null);
  }, [sourceLanguage, targetLanguage, result]);

  const clearAll = useCallback(() => {
    setText("");
    setResult(null);
    setError(null);
  }, []);

  return {
    text,
    setText,
    maxTextLength,
    sourceLanguage,
    setSourceLanguage,
    targetLanguage,
    setTargetLanguage,
    result,
    isLoading,
    error,
    setError,
    translate,
    swapLanguages,
    clearAll,
  };
}