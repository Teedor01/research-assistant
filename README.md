# AI Research Agent

An agent that researches a topic before it explains it. Instead of answering from a
language model's memory alone, it searches the web, reads and cross-checks multiple
sources, and produces a structured, beginner-friendly explanation with real citations
and an honest confidence signal.

Built for the Brainwave 2026 hackathon.

## The problem this solves

Language models answer confidently even when they're wrong, out of date, or simply
guessing. This agent is built to do the opposite: it treats every answer as something
that needs to be earned through actual research, not recalled from memory. If the
research comes up thin, the agent says so instead of papering over it.

## What it does

Give it a topic, for example "How does Kubernetes work?" or "REST vs GraphQL", and it
will:

1. Classify the question (broad or narrow, a comparison, an appropriate reading level)
2. Plan and run targeted web searches based on that classification
3. Validate sources before and after fetching them, and extract clean readable text
4. Synthesize findings into a structured knowledge graph of concepts, claims,
   relationships, and conflicts, not just a flat summary
5. Identify gaps in that knowledge and run further targeted searches if needed, in a
   bounded, iterative research loop
6. Write a clear explanation grounded only in verified, sourced knowledge
7. Cite every source that actually contributed to the final answer

The agent surfaces its own uncertainty. When sources disagree or research is cut short,
that shows up directly in the response instead of being smoothed over.

## Architecture

```
frontend/   Next.js, React, and Tailwind. A single page UI.
backend/    FastAPI and LangGraph. The research pipeline itself.
```

The backend is a LangGraph state machine. Each stage of research, intent analysis,
search, extraction, validation, synthesis, gap detection, writing, and citation, is an
isolated node that reads and writes one shared state object. External services (the
language model, search, and page extraction) sit behind swappable provider interfaces,
so the pipeline logic has no dependency on which specific service is powering it.

## Tech stack

- Frontend: Next.js (App Router), React, Tailwind CSS
- Backend: FastAPI, LangGraph, Pydantic
- Language model: Groq, accessed through an OpenAI-compatible interface behind a
  swappable provider abstraction
- Search: Tavily
- Content extraction: trafilatura

There is no database in this build. Each request is researched fresh and returned
directly, with nothing persisted. Storage was designed but deliberately cut for MVP
scope. See "Known limitations" below.

## Running it locally

You will need two terminals: one for the backend and one for the frontend.

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS or Linux
pip install -r requirements.txt
copy .env.example .env         # then fill in your real API keys
uvicorn app.main:app --reload
```

Runs on `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Runs on `http://localhost:3000`. Open that address in your browser.

### API keys required

- Groq: `https://console.groq.com/keys`, free tier, no card required
- Tavily: `https://app.tavily.com`, free tier

Both go in `backend/.env`. See `backend/.env.example` for the exact variable names.

## Known limitations

These are deliberate MVP scoping decisions, not oversights.

- No persistence. Results are not saved, and refreshing the page loses them. A storage
  layer was designed for this but cut to keep the demo simple and dependency free.
- No streaming. The frontend waits for one complete response. Depending on topic
  breadth and free tier rate limits, research can take anywhere from thirty seconds to
  a few minutes.
- Free tier rate limits. Running on Groq's free tier means research concurrency is
  intentionally throttled to stay under per minute token limits, which trades speed
  for reliability.

## Project structure

See `frontend/README.md` and the inline documentation throughout `backend/app/` for a
closer look at what each module is responsible for.
