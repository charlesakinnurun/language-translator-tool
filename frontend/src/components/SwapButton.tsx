interface SwapButtonProps {
  onClick: () => void;
}

export function SwapButton({ onClick }: SwapButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label="Swap languages"
      title="Swap source and target languages"
      className="focus-ring inline-flex h-11 w-11 shrink-0 items-center justify-center self-end rounded-xl border border-slate-200 bg-white text-slate-500 shadow-sm transition hover:border-indigo-300 hover:text-indigo-600 active:scale-95"
    >
      <svg
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M8 7h12m0 0l-3-3m3 3l-3 3" />
        <path d="M16 17H4m0 0l3 3m-3-3l3-3" />
      </svg>
    </button>
  );
}