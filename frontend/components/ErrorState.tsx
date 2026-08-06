interface Props {
  message: string;
  onRetry: () => void;
}

export default function ErrorState({ message, onRetry }: Props) {
  return (
    <div className="w-full max-w-md mx-auto text-center animate-fadeUp">
      <div className="inline-flex items-center justify-center w-10 h-10 rounded-full border border-rose/40 mb-5">
        <span className="text-rose font-mono text-sm" aria-hidden="true">!</span>
      </div>
      <p className="text-paper text-base mb-6">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="px-5 py-2.5 rounded-md bg-brass text-ink-deep font-medium text-sm hover:bg-brass-bright transition-colors"
      >
        Try again
      </button>
    </div>
  );
}
