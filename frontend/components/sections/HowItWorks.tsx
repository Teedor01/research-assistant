import Section from "./Section";

export default function HowItWorks({ content, index }: { content: string | null; index: string }) {

  if (!content) return null;

  return (
    <Section index={index} title="How it works">
      {content}
    </Section>
  );
}
