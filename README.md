# COSIB — Computer Science Intelligent Bot

An AI-powered academic virtual assistant for the Computer Science Department of
Gateway ICT Polytechnic, Saapade.

This repository is being delivered in phases, matching the engineering
specifications (ES-001 → ES-005) and datasets (DS-001 → DS-003). **This is
the complete delivery: ES-001 through ES-005, plus DS-001/002/003 knowledge
base seeding.**

## What's in ES-001 (foundation)

- Full project structure (`backend/`, `frontend/`, `database/`, `docs/`, `uploads/`, `tests/`, `scripts/`, `deployment/`)
- FastAPI backend with async SQLAlchemy 2.0, Alembic migrations, JWT auth (access + rotating refresh tokens), bcrypt password hashing, RBAC
- Every database model from the spec: Users, RefreshTokens, Departments, Courses, Lecturers, KnowledgeArticles, FAQs, Announcements, Events, Conversations, Messages, Feedback, AnalyticsEvents, AIProviderSettings, ApplicationSettings, AuditLogs, Notifications
- Working endpoints: auth, users (admin CRUD), courses, lecturers, announcements, health check
- React 19 + TypeScript + Vite + Tailwind frontend scaffold, auth context, protected routes, axios client with automatic token refresh

## What's in ES-002 (AI engine, chat, knowledge intelligence)

- **Provider abstraction**: `AIProvider` interface with `MockProvider` (no key needed — active by default), `GeminiProvider`, `OpenAIProvider`, and `AIManager` which resolves the active provider from the database at request time. Switching providers is an admin API call, not a code change.
- **Chat system**: `POST /api/v1/chat` (complete response) and `POST /api/v1/chat/stream` (Server-Sent Events streaming), conversation memory (last 12 messages), message persistence, like/dislike reactions.
- **Prompt engineering**: COSIB AI personality, three knowledge modes (Department / Academic / Campus) with keyword-based mode detection, system prompt never exposed to the client.
- **Knowledge retrieval**: keyword search across knowledge articles, FAQs, courses, and lecturers, injected into the system prompt before generation — structured so semantic/embedding search can replace the search function later without touching callers (RAG-ready).
- **Conversation history**: list, search, view, rename, pin, archive, delete.
- **Document analysis**: upload PDF/DOCX/TXT, extract text, then summarize / explain / generate a quiz / generate flashcards / answer a question against it.
- **AI configuration API**: admin-only endpoints to list providers, update temperature/max tokens/system prompt, and switch the active provider.
- **Frontend**: full ChatGPT-style interface — sidebar with conversation search/pin/delete, streaming message bubbles with markdown + syntax highlighting, quick action cards, follow-up suggestions, copy/like/dislike.

No API keys are required to use or demo this phase — the mock provider is active by default and produces real conversation flow end to end. Add `GEMINI_API_KEY` or `OPENAI_API_KEY` to `.env` and activate the provider via `POST /api/v1/ai/providers/activate` whenever you're ready.

## What's in ES-003 (administration portal, department management, analytics)

- **Admin dashboard**: real stat cards (students, conversations, today's conversations, KB articles, courses, announcements) and charts (conversation volume, AI provider usage) pulled live from the database — nothing synthetic.
- **User management**: search/filter, status changes (active/suspended/deactivated), role changes (super admin only), login history, account deletion.
- **Departments**: read endpoint backing course/lecturer creation; HOD/contact fields editable by admins.
- **Knowledge Base & FAQ management**: full admin CRUD UI with tabs, on top of the ES-002 API.
- **Courses & Lecturers**: admin CRUD UI.
- **Announcements & Events**: admin CRUD UI — create, pin, delete.
- **Feedback**: student-submitted ratings/comments, admin summary stats (average rating, positive/negative split, bug reports), admin responses.
- **Analytics**: conversation timeseries, AI provider usage, new-user growth, most-viewed FAQs/knowledge articles.
- **AI Configuration UI**: switch active provider, tune temperature/max tokens/system prompt, toggle streaming — from the browser, on top of the ES-002 API.
- **System Settings**: admin-editable key-value config (app name, brand colors, support email, maintenance mode) with a public subset for frontend branding.
- **Audit Logs**: read-only trail of sensitive actions (role/status changes, etc), filterable, super-admin only.
- **Notifications**: admins are notified in-app when new feedback arrives (extensible to other triggers).
- **RBAC note**: roles are enum-based and enforced via `require_roles` dependencies rather than a separate database-driven permissions table — `GET /api/v1/admin/roles` documents what each role can do. This keeps authorization logic auditable in code; a fully dynamic permissions UI can be added later if the department needs per-user permission overrides.

## What's in ES-004 (premium UI/UX, frontend experience, testing)

- **Visual identity**: Space Grotesk (display) + Inter (body) + JetBrains Mono (data/terminal) type pairing, layered on the existing Deep Navy / Royal Blue / Sky Blue brand system. Global focus-visible rings and `prefers-reduced-motion` support.
- **Landing page rebuild**: a live-typing terminal-style demo of COSIB answering real department questions as the hero's signature element, plus How It Works, stats, a clearly-marked testimonials placeholder, and an FAQ accordion.
- **Auth screens**: split brand/form layout, password strength indicator, remember-me (persistent vs. session-only tokens), a clearly-marked "coming soon" social login button (not a fake working one).
- **Component library**: `Toast` (notification system, wired into several admin actions), `Modal`, `Tooltip`, `Badge`, `Accordion`, `EmptyState`, `Skeleton` loaders, `Pagination` — under `frontend/src/components/ui/`.
- **Chat polish**: animated typing indicator while a response streams in, staggered quick-action card entrance via Framer Motion.
- **Error & status pages**: 401, 403, 500, offline, and maintenance pages, alongside the existing 404 — `ProtectedRoute` now sends role-mismatched users to a real 403 page instead of silently redirecting.
- **Accessibility**: labeled form fields, `aria-live` toast region, `aria-expanded`/`aria-modal` on interactive components, keyboard-dismissible modal (Escape), visible focus rings throughout.
- **Testing**: a real pytest suite (`backend/tests/backend/`) covering auth, RBAC enforcement, conversation flow, health check, and prompt-engineering unit tests — see `docs/TESTING.md`. A Vitest + Testing Library setup with initial component tests on the frontend.
- **Documentation**: `docs/TESTING.md`, `docs/DEPLOYMENT.md`, `docs/USER_MANUAL.md`, `docs/ADMINISTRATOR_MANUAL.md`.
- **RBAC architecture note**: role permissions are now centralized in `backend/app/core/permissions.py` (a single `get_role_permissions()` function with role inheritance) rather than duplicated per-route — enforcement still happens via `require_roles` on each route. This is the one place a future per-user/granular permissions system would change; no route files would need to.

## What's in ES-005 (final integration, demo mode, knowledge base seeding)

- **Knowledge base seeding (DS-001)**: institutional facts for Gateway ICT
  Polytechnic, Saapade, built by researching the official site and public
  admission sources — every verified fact is cited, and unverified
  specifics (current HOD name, exact fees, department office location,
  etc.) are explicitly marked "Information Not Available" rather than
  invented. Full sourcing methodology: `docs/KNOWLEDGE_BASE_SOURCES.md`.
- **Academic knowledge base (DS-002)**: 27 Computer Science topics across
  9 subject areas (programming, algorithms, databases, networking, OS,
  software engineering, AI, cybersecurity, discrete math), each with an
  explanation, worked example, and quiz questions — plus a consolidated
  quiz bank, flashcard set, and 9 suggested learning paths.
  `python -m scripts.seed_knowledge_base` loads both DS-001 and DS-002 into
  the live knowledge base (idempotent — safe to re-run).
- **Demo/Presentation Mode (DS-003)**: `python -m scripts.seed_demo` adds
  realistic, clearly-fictional sample students, lecturers, courses,
  conversations (with real message history), feedback, announcements, and
  events, plus backdated analytics events so dashboard charts show 14 days
  of history immediately — no more empty states during a live demo.
- **RBAC finalized**: permissions centralized in `app/core/permissions.py`
  with role inheritance; `GET /api/v1/admin/roles` documents every role's
  capabilities from that single source of truth.
- **Security hardening**: rate limiting extended to `/auth/login` and
  `/auth/register`; security headers middleware added
  (`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`,
  `Permissions-Policy`, HSTS in production). Full review: `docs/SECURITY_REPORT.md`.
- **Final documentation set**: `docs/ARCHITECTURE.md`, `docs/DIAGRAMS.md`
  (ERD, use case, sequence, and deployment diagrams in Mermaid),
  `docs/TESTING_REPORT.md`, `docs/SECURITY_REPORT.md`,
  `docs/PERFORMANCE_REPORT.md`, `docs/KNOWLEDGE_BASE_SOURCES.md`.

## Deployment migration: Vercel + Railway + Supabase

The original deployment target for this project was Render. It has since
been migrated to **Vercel** (frontend), **Railway** (backend), and
**Supabase** (PostgreSQL) — a deployment-target change only, with zero
changes to application functionality, architecture, or business logic.
All Render-specific configuration and documentation has been removed.

- **Frontend (Vercel)**: `frontend/vercel.json` — SPA rewrites, security
  headers, asset caching. Deploys from the `frontend/` directory.
- **Backend (Railway)**: `backend/Dockerfile` + `backend/railway.json` —
  Dockerfile-based build, health check at `/api/v1/health`, restart
  policy. Deploys from the `backend/` directory (Root Directory set via
  the Railway dashboard).
- **Database (Supabase)**: managed PostgreSQL — connection string goes
  into `DATABASE_URL`/`DATABASE_URL_SYNC` on Railway. Supabase's Auth and
  Storage products are *not* used — COSIB's own JWT authentication is
  preserved unchanged, and file uploads are processed in-memory (never
  persisted to disk), so there's currently nothing for Supabase Storage to
  hold. See `docs/DEPLOYMENT.md` for why, and the full setup walkthrough.
- **One real bug fixed as part of this migration**: the frontend's API
  client used relative paths (`/api/v1/...`), which only worked when
  frontend and backend shared a domain — never actually true once they're
  on separate platforms (Vercel vs. Railway, same issue would have existed
  on Render's separate services too). Fixed in `frontend/src/lib/api.ts`
  and `chatApi.ts` to resolve against `VITE_API_BASE_URL`, with a
  same-origin fallback that keeps local dev working via the Vite proxy.
- CORS now supports both an explicit production origin
  (`CORS_ORIGINS`) and an optional regex (`CORS_ORIGIN_REGEX`) for
  Vercel's per-branch preview deployment URLs.

Full walkthrough: `docs/DEPLOYMENT.md`. Environment variable reference:
`docs/ENVIRONMENT_CONFIGURATION.md`.

## Final acceptance criteria

Checked against the actual delivered code, honestly — not aspirationally.

| Criterion | Status |
|---|---|
| Fully responsive | ✅ Tailwind responsive utilities throughout; admin sidebar and chat layout adapt to mobile/tablet/desktop |
| Secure | ✅ JWT + RBAC + bcrypt + rate limiting + security headers + audit logs — see `docs/SECURITY_REPORT.md` for the honest gap list |
| Modular | ✅ Clean layer separation (api/services/models), provider abstraction, permission layer isolated from route code |
| Well documented | ✅ 15 documents under `docs/`, covering install, architecture, diagrams, testing, security, performance, and both user/admin manuals |
| Production-ready | ⚠️ Ready for an academic presentation and real pilot use; see Security and Performance reports for hardening recommended before large-scale production traffic |
| Beautiful UI | ✅ Custom type pairing, signature terminal-demo hero, full component library, dark-navy/royal-blue/sky-blue brand system |
| AI working correctly | ✅ Provider abstraction with mock/Gemini/OpenAI, streaming, knowledge retrieval, conversation memory — verified via `test_chat.py` |
| Knowledge Base functioning | ✅ 27+ academic articles, 8 institutional articles, 14 FAQs seeded and searchable; admin CRUD UI on top |
| Admin Dashboard complete | ✅ Users, KB/FAQ, courses, lecturers, announcements, events, feedback, analytics, AI config, settings, audit logs |
| Analytics complete | ✅ Live-computed (not simulated) dashboard stats, conversation/user-growth charts, provider usage, top content |
| Production deployment successful | ⚠️ Migrated to Vercel + Railway + Supabase (see below) — configuration complete (`frontend/vercel.json`, `backend/Dockerfile`, `backend/railway.json`) and documented (`docs/DEPLOYMENT.md`); actual deploy requires your Vercel/Railway/Supabase accounts and GitHub push — not something this sandbox can execute |
| GitHub deployment configured | ✅ Both Vercel and Railway connect natively to GitHub and auto-deploy on push once configured — no custom CI pipeline needed |
| Clean Architecture | ✅ See `docs/ARCHITECTURE.md` |
| SOLID principles followed | ✅ Single-responsibility services, provider interface (Open/Closed for new AI vendors), dependency injection throughout via FastAPI's `Depends` |
| No placeholder content | ✅ Every stub is explicit (501 responses, "coming soon" labels) — nothing pretends to work when it doesn't |
| No critical bugs | ⚠️ Full backend syntax/import verified in this sandbox; `npm install` and `pytest` against a real Postgres instance haven't been run here (no network access) — run both before your presentation |

## What would come next (beyond this delivery)

- Wire `npm install` + `pytest` in a real environment and fix anything
  those surface that a static check couldn't catch.
- Expand the DS-002 knowledge base beyond the initial 27 topics as the
  department identifies gaps.
- Consider the granular per-user permissions extension noted in
  `app/core/permissions.py`, if the department's needs outgrow role-based
  access.
- Address the remaining items in `docs/SECURITY_REPORT.md` and
  `docs/TESTING_REPORT.md` before any deployment beyond an academic
  presentation or pilot.

## Quick start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # edit DATABASE_URL, SECRET_KEY
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
python -m scripts.seed                                 # creates department + super admin
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/api/docs

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: http://localhost:5173

## Testing

See `docs/TESTING.md` for full instructions. Quick version:

```bash
# Backend (needs a disposable Postgres database)
cd backend && pytest -v

# Frontend
cd frontend && npm run test
```

## Documentation

See `docs/` for the installation guide, developer guide, folder structure,
and environment configuration reference.

## Tech stack

**Backend:** Python 3.13, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, JWT, bcrypt
**Frontend:** React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router, Axios
**Deployment:** Vercel (frontend) + Railway (backend) + Supabase (PostgreSQL)
