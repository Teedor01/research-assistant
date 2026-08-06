import { Completeness } from "@/lib/types";

interface Props {
  confidence: number; // 0-1
  completeness: Completeness;
}


export default function ConfidenceNotice({ confidence, completeness }: Props) {
  const filledTicks = Math.round(confidence * 5);
  const tier = confidence >= 0.7 ? "high" : confidence >= 0.4 ? "medium" : "low";

  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6 rounded-lg border border-border-soft bg-card-raised px-5 py-4">
      <div className="flex items-center gap-3 shrink-0">
        <span className="eyebrow">Confidence</span>
        <div className="flex items-center gap-[3px]" aria-hidden="true">
          {Array.from({ length: 5 }).map((_, i) => (
            <span
              key={i}
              className={`block w-1.5 h-4 rounded-sm ${
                i < filledTicks
                  ? tier === "high"
                    ? "bg-brass"
                    : tier === "medium"
                    ? "bg-brass-dim"
                    : "bg-rose"
                  : "bg-border"
              }`}
            />
          ))}
        </div>
        <span className="sr-only">
          {tier === "high" ? "High confidence" : tier === "medium" ? "Some uncertainty" : "Low confidence"}
        </span>
      </div>

      {tier !== "high" && (
        <p className="text-sm text-muted">
          {tier === "medium"
            ? "Some details here are less well-documented than others."
            : "Sources on this topic were limited or disputed — treat this as a starting point, not a final word."}
        </p>
      )}

      {completeness === "partial" && (
        <p className="text-sm text-brass sm:ml-auto sm:text-right">
          <span className="font-mono text-xs uppercase tracking-wide2 mr-1.5">Partial —</span>
          research hit a limit before covering everything.
        </p>
      )}
    </div>
  );
}
