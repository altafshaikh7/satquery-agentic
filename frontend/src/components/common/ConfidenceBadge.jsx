import { ShieldCheck } from "lucide-react";
import { formatConfidence } from "../../utils/formatters";

function ConfidenceBadge({ confidence }) {
  if (confidence === null || confidence === undefined) {
    return null;
  }

  const numericConfidence = Number(confidence);
  const percentage = Math.round(
    numericConfidence <= 1
      ? numericConfidence * 100
      : numericConfidence
  );

  let status = "Low";
  let statusClass =
    "border-red-500/30 bg-red-500/10 text-red-300";

  if (percentage >= 80) {
    status = "High";
    statusClass =
      "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  } else if (percentage >= 60) {
    status = "Medium";
    statusClass =
      "border-yellow-500/30 bg-yellow-500/10 text-yellow-300";
  }

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-medium ${statusClass}`}
    >
      <ShieldCheck size={16} />

      <span>Confidence: {formatConfidence(numericConfidence)}</span>

      <span className="opacity-70">• {status}</span>
    </div>
  );
}

export default ConfidenceBadge;