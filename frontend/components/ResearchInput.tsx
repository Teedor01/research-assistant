"use client";

import { FormEvent, useState } from "react";

interface Props {
  onSubmit: (topic: string) => void;
  disabled: boolean;
}

export default function ResearchInput({ onSubmit, disabled }: Props) {
  const [topic, setTopic] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = topic.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
  }

  return (
    <div className="w-full max-w-2xl mx-auto animate-fadeUp px-4">
      <p className="eyebrow mb-4">A research agent that reads before it answers</p>
      <h1 className="font-display text-2xl sm:text-4xl md:text-5xl leading-[1.1] text-[#111827] mb-3">
        What are you trying to <em className="text-[#2563EB] not-italic font-medium">understand</em>?
      </h1>
      <p className="text-[#64748B] text-sm sm:text-base md:text-lg mb-10 max-w-xl">
        Give it a topic. It searches, reads several sources, checks them against each other,
        and writes you a clear explanation with the receipts attached.
      </p>

      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-stretch gap-2 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] shadow-card focus-within:border-[#2563EB] transition-colors">
          <div className="hidden sm:flex items-center pl-5 font-mono text-[#1D4ED8] select-none">
            <span aria-hidden="true">&gt;</span>
          </div>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="How does Bitcoin mining work?"
            aria-label="Topic to research"
            disabled={disabled}
            maxLength={500}
            className="flex-1 min-w-0 bg-transparent py-3 sm:py-4 px-3 sm:px-2 text-[#111827] placeholder:text-[#64748B] font-body text-sm sm:text-base outline-none disabled:opacity-50"
            autoFocus
          />
          <button
            type="submit"
            disabled={disabled || !topic.trim()}
            className="m-1.5 sm:m-2 px-2.5 sm:px-5 py-2 sm:py-2.5 rounded-md bg-[#2563EB] text-white font-medium text-xs sm:text-sm whitespace-nowrap
                       hover:bg-[#1D4ED8] active:bg-[#1D4ED8]
                       disabled:opacity-30 disabled:cursor-not-allowed
                       transition-colors flex-shrink-0"
          >
            <span className="sm:hidden">Go</span>
            <span className="hidden sm:inline">Research this</span>
          </button>
        </div>
      </form>

      <div className="mt-6 flex flex-wrap gap-2">
        {EXAMPLE_TOPICS.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => !disabled && onSubmit(example)}
            disabled={disabled}
            className="font-mono text-xs text-[#64748B] hover:text-[#2563EB] border border-[#E2E8F0]
                       hover:border-[#2563EB] rounded-full px-3 py-1.5 transition-colors
                       disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}

const EXAMPLE_TOPICS = [
  "What is Kubernetes?",
  "REST vs GraphQL",
  "How do transformers work?",
];