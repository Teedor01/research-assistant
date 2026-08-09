import { ResearchResponse } from "@/lib/types";
import ConfidenceNotice from "./ConfidenceNotice";
import Section from "./sections/Section";
import HowItWorks from "./sections/HowItWorks";
import AdvantagesLimitations from "./sections/AdvantagesLimitations";
import Faq from "./sections/Faq";
import References from "./sections/References";

interface Props {
  data: ResearchResponse;
  onReset: () => void;
}

export default function ResultView({ data, onReset }: Props) {
  return (
    <div className="w-full max-w-2xl mx-auto animate-fadeUp">
      <button
        type="button"
        onClick={onReset}
        className="font-mono text-xs text-[#64748B] hover:text-[#2563EB] mb-6 inline-flex items-center gap-1.5"
      >
        <span aria-hidden="true">←</span> Research another topic
      </button>

      <p className="eyebrow mb-2">Research summary</p>
      <h1 className="font-display text-3xl sm:text-4xl text-[#111827] leading-tight mb-6">
        {data.topic}
      </h1>

      <ConfidenceNotice confidence={data.overall_confidence} completeness={data.completeness} />

      <div className="mt-2">
        <Section index="01" title="In short">
          {data.simple_explanation}
        </Section>

        <Section index="02" title="Core concepts">
          {data.core_concepts}
        </Section>

        <HowItWorks content={data.how_it_works} index="03" />

        <Section index="04" title="Why it matters">
          {data.why_it_matters}
        </Section>

        <Section index="05" title="In practice">
          {data.real_world_examples}
        </Section>

        <AdvantagesLimitations
          advantages={data.advantages}
          limitations={data.limitations}
          index="06"
        />

        <Section index="07" title="Common misconceptions">
          {data.common_misconceptions}
        </Section>

        <Faq items={data.faq} index="08" />

        <Section index="09" title="Summary">
          {data.summary}
        </Section>

        <References items={data.references} index="10" />
      </div>
    </div>
  );
}