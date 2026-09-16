interface InputPanelProps {
  text: string;
  onChange: (text: string) => void;
  maxLength: number;
  disabled?: boolean;
  onTranslate?: () => void;
}

export function InputPanel({
  text,
  onChange,
  maxLength,
  disabled = false,
  onTranslate,
}: InputPanelProps) {
  const remaining = maxLength - text.length;

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      onTranslate?.();
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="source-text" className="sr-only">
        Text to translate
      </label>
      <textarea
        id="source-text"
        value={text}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        maxLength={maxLength}
        disabled={disabled}
        placeholder="Type or paste text to translate..."
        rows={8}
        className="focus-ring w-full resize-none rounded-xl border border-slate-200 bg-white p-4 text-base leading-relaxed text-slate-800 shadow-sm transition placeholder:text-slate-400"
      />
      <div className="flex items-center justify-between px-1 text-xs text-slate-400">
        <span>{remaining.toLocaleString()} characters remaining</span>
        {text.length > 0 && (
          <button
            type="button"
            onClick={() => onChange("")}
            className="focus-ring rounded-md px-1.5 py-0.5 font-medium text-slate-500 transition hover:text-slate-700"
          >
            Clear
          </button>
        )}
      </div>
      <p className="px-1 text-xs text-slate-400">
        Press Ctrl/Cmd + Enter to translate.
      </p>
    </div>
  );
}