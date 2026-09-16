import { useCallback, useState } from "react";

import { getLanguageName } from "../services/languages";
import { TranslationResponse } from "../types/translation";

interface ResultCardProps {
  result: TranslationResponse | null;
  isLoading: boolean;
  canUseSpeech: boolean;
  isSpeaking: boolean;
  onSpeak: () => void;
  onStopSpeaking: () => void;
}

async function copyToClipboard(text: string): Promise<boolean> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fall through to the legacy path.
    }
  }
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  const successful = document.execCommand("copy");
  document.body.removeChild(textarea);
  return successful;
}

function LoadingState() {
  return (
    <div
      className="flex h-full min-h-56 flex-col items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white p-6"
      role="status"
      aria-label="Translating..."
    >
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      <p className="text-sm text-slate-500">Translating...</p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full min-h-56 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/60 p-6 text-center">
      <p className="text-sm text-slate-500">Your translation will appear here.</p>
    </div>
  );
}

export function ResultCard({
  result,
  isLoading,
  canUseSpeech,
  isSpeaking,
  onSpeak,
  onStopSpeaking,
}: ResultCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    if (!result) {
      return;
    }
    const successful = await copyToClipboard(result.translated_text);
    if (successful) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    }
  }, [result]);

  if (isLoading) {
    return <LoadingState />;
  }

  if (!result) {
    return <EmptyState />;
  }

  const outputLabel = result.target_language
    ? getLanguageName(result.target_language)
    : null;

  return (
    <div className="flex h-full flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Translation{outputLabel ? ` (${outputLabel})` : ""}
        </p>
        <span className="h-2 w-2 rounded-full bg-emerald-400" aria-hidden="true" />
      </div>

      <p className="whitespace-pre-wrap text-lg font-medium leading-relaxed text-slate-800">
        {result.translated_text}
      </p>

      {result.detected_language && (
        <p className="text-xs text-slate-400">
          Detected language:{" "}
          <span className="font-medium text-slate-500">
            {getLanguageName(result.detected_language) ?? result.detected_language}
          </span>
        </p>
      )}

      <div className="mt-auto flex flex-wrap gap-2 border-t border-slate-100 pt-4">
        <button
          type="button"
          onClick={handleCopy}
          className="focus-ring inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3.5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 active:scale-95"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2" />
            <path d="M16 8h2a2 2 0 012 2v8a2 2 0 01-2 2h-8a2 2 0 01-2-2v-2" />
          </svg>
          {copied ? "Copied!" : "Copy translation"}
        </button>

        {canUseSpeech && (
          <button
            type="button"
            onClick={isSpeaking ? onStopSpeaking : onSpeak}
            className="focus-ring inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-indigo-300 hover:text-indigo-600 active:scale-95"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M11 5L6 9H2v6h4l5 4V5z" />
              <path d="M15.5 8.5a5 5 0 010 7" />
              <path d="M18.5 5.5a9 9 0 010 13" />
            </svg>
            {isSpeaking ? "Stop" : "Listen"}
          </button>
        )}
      </div>
    </div>
  );
}