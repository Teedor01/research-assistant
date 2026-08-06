# AI Research Agent — Frontend

## Setup

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000.

## Developing without the backend running

`app/page.tsx` calls `fetchResearch()` from `lib/api.ts`, which hits
`NEXT_PUBLIC_API_BASE_URL` + `/api/research`. Until the backend is running,
you can preview the result screen directly using the mock data:

```tsx
// Temporarily, in app/page.tsx, swap the real call for the mock:
import { mockResearchResponse, mockPartialResponse } from "@/lib/mock-data";

// e.g. in handleSubmit, instead of `await fetchResearch(newTopic)`:
const data = mockResearchResponse; // or mockPartialResponse to test the
                                    // partial/low-confidence/null-how-it-works path
```

Revert to the real `fetchResearch` call once the backend's `/api/research`
route is up — see the backend's frontend brief (`frontend-engineer-brief.md`)
for the full API contract this is built against.

## Structure

- `app/page.tsx` — the whole app is one page with a 4-state state machine:
  `idle → loading → result | error`. No routing, no history — matches v1
  backend scope exactly (see the brief's "explicit non-goals" section).
- `lib/types.ts` — mirrors the backend's `FinalResponse` / `ResearchResponse`
  schema by hand. If the backend contract changes, update this file first.
- `lib/api.ts` — the single fetch call, with a 90s client timeout (backend's
  own soft budget is 45s — this leaves headroom rather than cutting off a
  legitimately slow-but-successful response).
- `components/` — one component per screen state, `sections/` holds the ten
  result sections in their designed reading order.

## Design tokens

Defined in `tailwind.config.ts`. Dark "researcher's notebook" palette —
`ink`/`card` for surfaces, `brass` as the single accent (citations, the
confidence gauge, interactive states), `sage`/`rose` reserved narrowly for
corroboration/caution signals. Fraunces for display headings, Inter for body
text, IBM Plex Mono for labels and citation numbers.
