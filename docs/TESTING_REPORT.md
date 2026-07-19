# Testing Report

## Summary

A real, runnable test suite exists on both sides of the stack (see
`docs/TESTING.md` for how to run it). This report is an honest account of
what's covered and what isn't — written from the code, not aspirational.

## Backend (pytest) — 20 tests across 5 files

| File | Tests | What's verified |
|---|---|---|
| `test_health.py` | 1 | Health check returns `ok` with a working DB connection |
| `test_auth.py` | 8 | Registration (success, duplicate email, weak password), login (success, wrong password), `/auth/me` (requires token, returns correct user), refresh token rotation (issues new pair, old token single-use) |
| `test_rbac.py` | 5 | Students blocked from admin-only routes (403), promoted admins gain access, plain admins can't self-elevate to super-admin actions, suspended accounts rejected at auth |
| `test_chat.py` | 4 | Sending a message creates a conversation with a real assistant reply (via mock provider), conversation appears in history with correct message ordering, cross-user access to a conversation is blocked (403), rename/pin work |
| `test_prompt_engineering.py` | 6 | Mode detection (academic/department/campus/ambiguous), system prompt correctly includes/excludes knowledge context and admin overrides |

All 20 tests exercise real code paths through the actual FastAPI app — no
mocked business logic. The only substitution is the AI provider, which
uses the real `MockProvider` (not a test double) since it's designed to be
production-safe with no external dependency.

**Requires**: a disposable PostgreSQL database (models use PostgreSQL-
specific types, so SQLite can't stand in — see `docs/TESTING.md`).

## Frontend (Vitest + Testing Library) — 8 tests across 3 files

| File | Tests | What's verified |
|---|---|---|
| `PasswordStrength.test.tsx` | 3 | Empty password renders nothing, weak/strong passwords get correct labels |
| `Badge.test.tsx` | 2 | Renders children, applies variant styling |
| `utils.test.ts` | 3 | `cn()` merges classes, resolves Tailwind conflicts, drops falsy values |

This is intentionally scoped to pure/presentational logic that doesn't
require mocking the API layer — see `docs/TESTING.md` for how to extend
coverage to API-dependent components.

## What is NOT covered (honest gaps)

- **Frontend component tests for API-dependent components** (chat page,
  admin CRUD pages, auth forms) — would need `vi.mock()` on `src/lib/api.ts`.
- **End-to-end browser tests** (Playwright/Cypress) — noted in the ES-004
  spec as "Future E2E Testing"; not built in this delivery.
- **Load/performance testing** — no k6/locust scripts included.
- **Real AI provider integration tests** against live Gemini/OpenAI keys —
  deliberately out of scope since CI-style runs shouldn't depend on paid
  external APIs; the mock provider stands in.
- **File upload/document analysis endpoint tests** — `POST /documents/extract`
  and `/documents/analyze` are implemented and manually verifiable via
  `/api/docs`, but don't yet have automated pytest coverage.
- **Admin CRUD route tests** beyond RBAC gating (courses, lecturers,
  announcements, events, knowledge base, settings) — the RBAC tests confirm
  access control on these routes, but not every field-level validation path.

## Recommended next additions, in priority order

1. Document upload/analysis endpoint tests (highest-risk untested surface —
   file parsing has more edge cases than pure CRUD).
2. Admin CRUD field validation tests (e.g. course creation with a bad
   `department_id`).
3. Frontend tests for the chat page's streaming logic, mocking `chatApi.ts`.
4. A single Playwright smoke test covering register → login → send a
   message → see a response, as the first E2E test.
