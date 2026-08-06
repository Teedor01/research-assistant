interface Props {
  index: string;
  title: string;
  children: React.ReactNode;
}

export default function Section({ index, title, children }: Props) {
  return (
    <section className="py-8 border-b border-border-soft last:border-b-0">
      <div className="flex items-baseline gap-3 mb-4">
        <span className="font-mono text-xs text-brass-dim">{index}</span>
        <h2 className="font-display text-xl text-paper">{title}</h2>
      </div>
      <div className="pl-0 sm:pl-8 text-[15px] leading-[1.7] text-paper/90 space-y-4 whitespace-pre-line">
        {children}
      </div>
    </section>
  );
}
