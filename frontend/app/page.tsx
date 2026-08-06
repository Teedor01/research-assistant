"use client";

import { useState } from "react";
import { fetchResearch } from "@/lib/api";
import { ResearchApiError, ResearchResponse } from "@/lib/types";
import ResearchInput from "@/components/ResearchInput";
import LoadingState from "@/components/LoadingState";
import ResultView from "@/components/ResultView";
import ErrorState from "@/components/ErrorState";

type Status = "idle" | "loading" | "result" | "error";

export default function Home() {
  const [status, setStatus] = useState<Status>("idle");
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(newTopic: string) {
    setTopic(newTopic);
    setStatus("loading");
    try {
      const data = await fetchResearch(newTopic);
      setResult(data);
      setStatus("result");
    } catch (err) {
      const message =
        err instanceof ResearchApiError
          ? err.message
          : "Something went wrong researching that. Please try again.";
      setErrorMessage(message);
      setStatus("error");
    }
  }

  function reset() {
    setStatus("idle");
    setResult(null);
    setErrorMessage("");
  }

  return (
    <main className="min-h-screen flex flex-col items-center px-5 py-16 sm:py-24">
      {status === "idle" && <ResearchInput onSubmit={handleSubmit} disabled={false} />}
      {status === "loading" && <LoadingState topic={topic} />}
      {status === "result" && result && <ResultView data={result} onReset={reset} />}
      {status === "error" && <ErrorState message={errorMessage} onRetry={() => handleSubmit(topic)} />}
    </main>
  );
}
