import { ResearchResponse } from "./types";


export const mockResearchResponse: ResearchResponse = {
  topic: "How does Retrieval-Augmented Generation (RAG) work?",
  simple_explanation:
    "Retrieval-Augmented Generation, or RAG, is a way of making AI language models more accurate by giving them access to outside information before they answer a question. Instead of relying only on what the model memorized during training, a RAG system first searches a knowledge source — like a document database or the web — for relevant information, then hands that information to the model along with the original question. The model reads both and writes an answer grounded in what it just retrieved.\n\nThis matters because language models can be confidently wrong about facts, especially recent events or specialized topics they weren't trained on deeply. RAG reduces that problem by letting the model 'look things up' rather than guess from memory alone.",
  core_concepts:
    "Retrieval: searching a knowledge base or the web for information relevant to a question.\n\nGeneration: the language model's job of producing a written answer.\n\nAugmentation: adding retrieved information into the model's input alongside the original question.\n\nVector embeddings: converting text into numbers that capture meaning, enabling search by similarity rather than exact keywords.",
  how_it_works:
    "1. A user asks a question.\n2. The system searches a knowledge source for relevant content.\n3. The most relevant retrieved text is selected and formatted alongside the question.\n4. This combined input is given to the language model.\n5. The model generates an answer using both its own knowledge and the retrieved context.\n6. Many systems also return the sources used, so the answer can be checked.",
  why_it_matters:
    "Without retrieval, a language model can only answer from what it learned during training, which has a fixed cutoff date. RAG lets a general-purpose model be used for narrow or fast-changing domains without retraining it, and makes answers more checkable since sources can be shown.",
  real_world_examples:
    "Customer support chatbots answering from a company's own help-center articles. AI research assistants that search the web before writing an explanation. Legal and medical AI tools that retrieve from a curated, trusted document set.",
  advantages:
    "Reduces factual errors compared to answering from memory alone. Can incorporate information newer than the training cutoff. Makes answers more transparent, since sources can be shown.",
  limitations:
    "Answer quality depends heavily on retrieval quality. Adds latency and infrastructure complexity. Doesn't fully eliminate incorrect answers — the model can still misread retrieved content.",
  common_misconceptions:
    "\"RAG guarantees factual accuracy.\" It significantly reduces certain errors but doesn't eliminate them. \"RAG is a specific product.\" It's a general technique, not any single tool.",
  faq: [
    {
      question: "Is RAG the same thing as fine-tuning a model?",
      answer:
        "No. Fine-tuning changes the model's underlying weights through additional training. RAG leaves the model unchanged and instead feeds it relevant information at the moment it answers.",
    },
    {
      question: "Does RAG work with any language model?",
      answer:
        "In principle, yes — RAG is mostly about how information is prepared and delivered to the model, not a special property the model needs to have.",
    },
  ],
  summary:
    "RAG improves AI-generated answers by searching for relevant information before writing a response, trading some added complexity for meaningfully more accurate, current, and checkable answers.",
  references: [
    {
      title: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
      url: "https://arxiv.org/abs/2005.11401",
      domain: "arxiv.org",
      credibility_score: 0.91,
    },
    {
      title: "What is Retrieval-Augmented Generation (RAG)?",
      url: "https://www.ibm.com/topics/retrieval-augmented-generation",
      domain: "ibm.com",
      credibility_score: 0.78,
    },
    {
      title: "Retrieval-Augmented Generation Explained",
      url: "https://developer.nvidia.com/blog/what-is-retrieval-augmented-generation/",
      domain: "developer.nvidia.com",
      credibility_score: 0.8,
    },
  ],
  overall_confidence: 0.83,
  completeness: "complete",
};

export const mockPartialResponse: ResearchResponse = {
  ...mockResearchResponse,
  topic: "What is the current state of room-temperature superconductor research?",
  how_it_works: null,
  faq: [],
  overall_confidence: 0.34,
  completeness: "partial",
};
