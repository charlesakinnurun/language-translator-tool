import { ErrorAlert } from "./components/ErrorAlert";
import { InputPanel } from "./components/InputPanel";
import { LanguageSelect } from "./components/LanguageSelect";
import { ResultCard } from "./components/ResultCard";
import { SwapButton } from "./components/SwapButton";
import { useSpeechSynthesis } from "./hooks/useSpeechSynthesis";
import { useTranslation } from "./hooks/useTranslation";

export default function App() {
  const {
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
  } = useTranslation();

  const { supported, speaking, speak, stop } = useSpeechSynthesis();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/50 to-slate-100">
      <div className="mx-auto w-full max-w-5xl px-4 py-8 sm:py-12">
        <header className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-lg shadow-indigo-600/25">
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="M3 12h18" />
              <path d="M12 3a15 15 0 010 18M12 3a15 15 0 000 18" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
              Language Translation Tool
            </h1>
            <p className="text-sm text-slate-500">
              Fast, private translations powered by the Google Cloud Translation API
            </p>
          </div>
        </header>

        <main className="mt-8 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-xl shadow-indigo-950/5 backdrop-blur sm:p-8">
          {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

          <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
            <div className="grid w-full grid-cols-1 items-end gap-3 sm:grid-cols-[1fr_auto_1fr]">
              <LanguageSelect
                id="source-language"
                label="From"
                value={sourceLanguage}
                onChange={setSourceLanguage}
              />
              <SwapButton onClick={swapLanguages} />
              <LanguageSelect
                id="target-language"
                label="To"
                value={targetLanguage}
                onChange={setTargetLanguage}
              />
            </div>
            <button
              type="button"
              onClick={translate}
              disabled={isLoading}
              className="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-8 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-500 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60 lg:w-auto"
            >
              {isLoading && (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />
              )}
              {isLoading ? "Translating..." : "Translate"}
            </button>
          </div>

          <div className="mt-6 grid gap-5 md:grid-cols-2">
            <InputPanel
              text={text}
              onChange={setText}
              maxLength={maxTextLength}
              disabled={isLoading}
              onTranslate={translate}
            />
            <ResultCard
              result={result}
              isLoading={isLoading}
              canUseSpeech={supported}
              isSpeaking={speaking}
              onSpeak={() => result && speak(result.translated_text, result.target_language)}
              onStopSpeaking={stop}
            />
          </div>

          {text.length > 0 && (
            <div className="mt-5 flex justify-end">
              <button
                type="button"
                onClick={clearAll}
                className="focus-ring rounded-lg px-3 py-2 text-sm font-medium text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
              >
                Clear everything
              </button>
            </div>
          )}
        </main>

        <footer className="mt-8 text-center text-xs text-slate-400">
          Your text is sent to the translation service each time you hit translate.
          No data is stored.
        </footer>
      </div>
    </div>
  );
}