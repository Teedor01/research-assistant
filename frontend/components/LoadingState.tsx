"use client";

import { useEffect, useState } from "react";


const STAGES = [
  "Searching the web…",
  "Reading sources…",
  "Cross-checking facts…",
  "Writing your explanation…",
];

const SLOW_THRESHOLD_MS = 30_000;

export default function LoadingState({ topic }: { topic: string }) {
  const [stageIndex, setStageIndex] = useState(0);
  const [showSlowNotice, setShowSlowNotice] = useState(false);

  useEffect(() => {
    const stageTimer = setInterval(() => {
      setStageIndex((i) => Math.min(i + 1, STAGES.length - 1));
    }, 6000);
    const slowTimer = setTimeout(() => setShowSlowNotice(true), SLOW_THRESHOLD_MS);
    return () => {
      clearInterval(stageTimer);
      clearTimeout(slowTimer);
    };
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto text-center animate-fadeUp" role="status" aria-live="polite">
      <p className="eyebrow mb-3">Researching</p>
      <h2 className="font-display text-2xl sm:text-3xl text-[#111827] mb-8 leading-snug">
        &ldquo;{topic}&rdquo;
      </h2>

      <div className="inline-flex items-center gap-3 rounded-full border border-[#E2E8F0] bg-[#F8FAFC] px-5 py-3">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#2563EB] opacity-60" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-[#2563EB]" />
        </span>
        <span className="font-mono text-sm text-[#64748B]">{STAGES[stageIndex]}</span>
      </div>

      {showSlowNotice && (
        <p className="mt-8 text-sm text-[#64748B] max-w-md mx-auto animate-fadeUp">
          Still working thorough research can take a little while, especially for broad
          or comparison topics.
        </p>
      )}
    </div>
  );
}