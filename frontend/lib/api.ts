import { ApiErrorResponse, ResearchApiError, ResearchResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";


const CLIENT_TIMEOUT_MS = 90_000;

export async function fetchResearch(topic: string): Promise<ResearchResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CLIENT_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ResearchApiError({
        code: "CLIENT_TIMEOUT",
        message: "This is taking longer than expected. Please try again.",
      });
    }
    throw new ResearchApiError({
      code: "NETWORK_ERROR",
      message: "Couldn't reach the research service. Check your connection and try again.",
    });
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    let detail: ApiErrorResponse["error"] = {
      code: "UNKNOWN_ERROR",
      message: "Something went wrong researching that. Please try again.",
    };
    try {
      const body = (await response.json()) as ApiErrorResponse;
      if (body?.error) detail = body.error;
    } catch {
      
    }
    throw new ResearchApiError(detail);
  }

  return (await response.json()) as ResearchResponse;
}
