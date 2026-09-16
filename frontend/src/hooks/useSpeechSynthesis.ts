import { useCallback, useEffect, useRef, useState } from "react";

import { getSpeechCode } from "../services/languages";

/**
 * Thin wrapper around the browser SpeechSynthesis API with cleanup and a
 * safe no-op when the API is unavailable.
 */
export function useSpeechSynthesis() {
  const supported =
    typeof window !== "undefined" && "speechSynthesis" in window;
  const [speaking, setSpeaking] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    return () => {
      if (supported) {
        window.speechSynthesis.cancel();
      }
    };
  }, [supported]);

  const stop = useCallback(() => {
    if (!supported) {
      return;
    }
    window.speechSynthesis.cancel();
    setSpeaking(false);
    utteranceRef.current = null;
  }, [supported]);

  const speak = useCallback(
    (text: string, languageCode: string) => {
      if (!supported || !text.trim()) {
        return;
      }
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = getSpeechCode(languageCode);
      utterance.rate = 1;
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = () => setSpeaking(false);

      utteranceRef.current = utterance;
      setSpeaking(true);
      window.speechSynthesis.speak(utterance);
    },
    [supported],
  );

  return { supported, speaking, speak, stop };
}