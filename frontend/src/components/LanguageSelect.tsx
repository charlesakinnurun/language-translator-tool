import { LANGUAGES } from "../services/languages";

interface LanguageSelectProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
}

export function LanguageSelect({
  id,
  label,
  value,
  onChange,
}: LanguageSelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="focus-ring h-11 w-full rounded-xl border border-slate-200 bg-white px-3 pr-8 text-sm font-medium text-slate-800 shadow-sm transition hover:border-slate-300"
      >
        {LANGUAGES.map((language) => (
          <option key={language.code} value={language.code}>
            {language.name}
          </option>
        ))}
      </select>
    </div>
  );
}