# Performance Report

## Backend

- **Fully async request path**: FastAPI routes, SQLAlchemy 2.0 async
  sessions, and AI provider calls (via `httpx.AsyncClient`) are all
  non-blocking, so one slow AI response doesn't stall other requests on
  the same worker.
- **Connection pooling**: `create_async_engine` is configured with
  `pool_size=10, max_overflow=20, pool_pre_ping=True` (`app/db/session.py`)
  — reused connections, dead-connection detection, and headroom for bursts.
- **Streaming responses**: chat replies stream token-by-token via SSE
  rather than waiting for the full response, so perceived latency (time to
  first token) is much lower than total generation time.
- **Database indexing**: every UUID primary key is indexed by default;
  additional indexes are declared on frequently-filtered/joined columns
  (`User.email`, `User.username`, `Course.code`, `AuditLog.action`, etc.)
  — see the relevant `mapped_column(..., index=True)` declarations in
  `app/models/`.
- **Knowledge retrieval is bounded**: `search_knowledge()` caps results
  per source table (`max_results`, default 4) and extracts at most 6
  keyword terms per query, so a pathologically long question can't trigger
  an unbounded search.
- **Conversation memory window is capped**: only the last 12 messages are
  sent to the AI provider per request (`MAX_HISTORY_MESSAGES` in
  `chat_service.py`), keeping prompt size — and therefore latency and
  token cost — bounded regardless of how long a conversation grows.

## Frontend

- **Vite build**: esbuild-based bundling and dev server, far faster cold
  starts and HMR than older bundlers.
- **TanStack Query**: caches server responses (`staleTime: 30s` default),
  avoiding redundant refetches when navigating between views that share data.
- **Route-level code organization**: pages are separate components under
  `src/pages/`, structured to support `React.lazy()` code-splitting if
  bundle size becomes a concern — not yet wired up, since the current app
  size doesn't warrant it (see "Not yet done" below).
- **Tailwind's production build** purges unused classes automatically via
  the `content` glob in `tailwind.config.js`, keeping shipped CSS small.
- **Framer Motion used sparingly**: animations are applied to specific,
  purposeful moments (quick-action card entrance, modal/toast transitions)
  rather than globally, keeping animation-related re-renders localized.

## What was not measured (honest gaps)

- **No Lighthouse run performed** — this sandbox has no network access to
  build and serve the frontend, so no real score is available. Recommended:
  run `npm run build && npm run preview`, then Lighthouse against the
  preview server, once you have the project running locally.
- **No load testing performed** — no k6/locust/Artillery scripts included.
  For a final-year presentation this is a reasonable gap; for anything
  handling real student traffic, load-test the chat streaming endpoint
  specifically, since it holds connections open longer than typical REST calls.
- **No code-splitting/lazy-loading wired up yet** — the current page count
  and bundle size don't obviously need it, but if the admin portion grows
  further, wrapping `AdminLayout`'s child routes in `React.lazy()` would
  keep the initial (student-facing) bundle from including admin-only code.
- **No CDN/image optimization pipeline** — the app currently has minimal
  image assets (a placeholder favicon, no product photography), so this
  wasn't a priority; revisit if the department adds substantial imagery
  (lecturer photos, campus photos) to the knowledge base or landing page.

## Recommended next steps, in priority order

1. Run an actual Lighthouse audit once `npm install` completes locally,
   and record the baseline score in this file.
2. Add `React.lazy()` for the admin route tree if bundle size becomes
   noticeable in that audit.
3. Load-test `/api/v1/chat/stream` specifically before any real-traffic
   deployment, since it's the most resource-intensive endpoint (holds a
   connection open per active conversation).
4. Add response caching (e.g. short-TTL cache on `/api/v1/analytics/*`
   dashboard endpoints) if the admin dashboard is refreshed frequently by
   multiple concurrent admins.
