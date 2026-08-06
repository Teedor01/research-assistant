export interface FaqItem {
  question: string;
  answer: string;
}

export interface Reference {
  title: string;
  url: string;
  domain: string;
  credibility_score: number;
}

export type Completeness = "complete" | "partial";

export interface ResearchResponse {
  topic: string;
  simple_explanation: string;
  core_concepts: string;
  how_it_works: string | null;
  why_it_matters: string;
  real_world_examples: string;
  advantages: string;
  limitations: string;
  common_misconceptions: string;
  faq: FaqItem[];
  summary: string;
  references: Reference[];
  overall_confidence: number;
  completeness: Completeness;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
}

export interface ApiErrorResponse {
  error: ApiErrorDetail;
}

export class ResearchApiError extends Error {
  code: string;
  constructor(detail: ApiErrorDetail) {
    super(detail.message);
    this.code = detail.code;
  }
}
