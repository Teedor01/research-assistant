import Section from "./Section";

export default function AdvantagesLimitations({
  advantages,
  limitations,
  index,
}: {
  advantages: string;
  limitations: string;
  index: string;
}) {
  return (
    <Section index={index} title="Weighing it up">
      <div className="grid sm:grid-cols-2 gap-6 sm:gap-8">
        <div>
          <p className="font-mono text-xs uppercase tracking-wide2 text-sage mb-2">Advantages</p>
          <p className="whitespace-pre-line text-paper/90">{advantages}</p>
        </div>
        <div>
          <p className="font-mono text-xs uppercase tracking-wide2 text-rose mb-2">Limitations</p>
          <p className="whitespace-pre-line text-paper/90">{limitations}</p>
        </div>
      </div>
    </Section>
  );
}
