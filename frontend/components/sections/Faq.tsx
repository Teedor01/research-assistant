"use client";

import { useState } from "react";
import { FaqItem } from "@/lib/types";
import Section from "./Section";

export default function Faq({ items, index }: { items: FaqItem[]; index: string }) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  if (items.length === 0) return null;

  return (
    <Section index={index} title="Questions worth asking">
      <div className="space-y-2 -mt-1">
        {items.map((item, i) => {
          const isOpen = openIndex === i;
          return (
            <div key={i} className="border border-border-soft rounded-md overflow-hidden">
              <button
                type="button"
                onClick={() => setOpenIndex(isOpen ? null : i)}
                aria-expanded={isOpen}
                className="w-full flex items-center justify-between gap-4 px-4 py-3 text-left
                           bg-card hover:bg-card-raised transition-colors"
              >
                <span className="text-paper text-sm font-medium">{item.question}</span>
                <span
                  className={`font-mono text-brass-dim shrink-0 transition-transform ${isOpen ? "rotate-45" : ""}`}
                  aria-hidden="true"
                >
                  +
                </span>
              </button>
              {isOpen && (
                <div className="px-4 pb-4 pt-1 text-sm text-muted leading-relaxed">
                  {item.answer}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Section>
  );
}
