import { Reference } from "@/lib/types";
import Section from "./Section";

export default function References({ items, index }: { items: Reference[]; index: string }) {
  if (items.length === 0) return null;

  return (
    <Section index={index} title="Sources">
      <ol className="space-y-3 -mt-1">
        {items.map((ref, i) => (
          <li key={ref.url} className="flex items-start gap-3">
            <span className="font-mono text-xs text-brass-dim pt-0.5 shrink-0 w-5">
              {String(i + 1).padStart(2, "0")}
            </span>
            <div className="min-w-0">
              <a
                href={ref.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-paper hover:text-brass underline decoration-border-soft
                           hover:decoration-brass underline-offset-4 transition-colors break-words"
              >
                {ref.title}
              </a>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="font-mono text-xs text-muted-dim">{ref.domain}</span>
                <CredibilityDot score={ref.credibility_score} />
              </div>
            </div>
          </li>
        ))}
      </ol>
    </Section>
  );
}

function CredibilityDot({ score }: { score: number }) {
  const color = score >= 0.7 ? "bg-sage" : score >= 0.4 ? "bg-brass-dim" : "bg-rose";
  return (
    <span className="flex items-center gap-1" title={`Credibility: ${Math.round(score * 100)}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${color}`} aria-hidden="true" />
    </span>
  );
}
