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
    <div className="w-full max-w-2xl mx-auto animate-fadeUp">
      <p className="eyebrow mb-4">A research agent that reads before it answers</p>
      <h1 className="font-display text-4xl sm:text-5xl leading-[1.1] text-paper mb-3">
        What are you trying to <em className="text-brass not-italic font-medium">understand</em>?
      </h1>
      <p className="text-muted text-base sm:text-lg mb-10 max-w-xl">
        Give it a topic. It searches, reads several sources, checks them against each other,
        and writes you a clear explanation — with the receipts attached.
      </p>

      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-stretch gap-3 rounded-lg border border-border bg-card shadow-card focus-within:border-brass-dim transition-colors">
          <div className="flex items-center pl-5 font-mono text-brass-dim select-none">
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
            className="flex-1 bg-transparent py-4 pr-2 text-paper placeholder:text-muted-dim font-body text-base outline-none disabled:opacity-50"
            autoFocus
          />
          <button
            type="submit"
            disabled={disabled || !topic.trim()}
            className="m-2 px-5 rounded-md bg-brass text-ink-deep font-medium text-sm
                       hover:bg-brass-bright active:bg-brass-dim
                       disabled:opacity-30 disabled:cursor-not-allowed
                       transition-colors"
          >
            Research this
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
            className="font-mono text-xs text-muted hover:text-brass border border-border-soft
                       hover:border-brass-dim rounded-full px-3 py-1.5 transition-colors
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
