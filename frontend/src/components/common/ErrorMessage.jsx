import { AlertCircle, X } from "lucide-react";

function ErrorMessage({ message, onDismiss }) {
  if (!message) {
    return null;
  }

  return (
    <div
      role="alert"
      className="flex items-start justify-between gap-4 rounded-2xl border border-red-500/30 bg-red-500/10 p-4"
    >
      <div className="flex items-start gap-3">
        <AlertCircle
          size={22}
          className="mt-0.5 shrink-0 text-red-400"
        />

        <div>
          <h3 className="font-semibold text-red-300">
            Analysis Failed
          </h3>

          <p className="mt-1 text-sm leading-6 text-red-200/80">
            {message}
          </p>
        </div>
      </div>

      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss error"
          className="rounded-lg p-1 text-red-300 transition hover:bg-red-500/20 hover:text-white"
        >
          <X size={18} />
        </button>
      )}
    </div>
  );
}

export default ErrorMessage;