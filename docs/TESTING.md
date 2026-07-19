# Testing Guide

## Backend (pytest)

Tests exercise the real FastAPI app through an in-process HTTP client
(`httpx.AsyncClient` + `ASGITransport`) against a real PostgreSQL database —
not mocks, not SQLite. The models use PostgreSQL-specific column types
(UUID, JSONB, ARRAY), so a Postgres test database is required.

### Setup

```bash
cd backend
createdb cosib_test   # or: psql -c "CREATE DATABASE cosib_test;"
export TEST_DATABASE_URL=postgresql+asyncpg://cosib:cosib@localhost:5432/cosib_test
pytest -v
```

If `TEST_DATABASE_URL` isn't set, tests fall back to `DATABASE_URL` from
your `.env` — **point that at a disposable database**, since the test
suite creates and drops all tables each run.

### What's covered

| File | Covers |
|---|---|
| `test_health.py` | Health check endpoint (what Railway polls) |
| `test_auth.py` | Register, login, `/auth/me`, refresh-token rotation, weak-password/duplicate-email rejection |
| `test_rbac.py` | Role-gated endpoints reject the wrong role, super-admin-only actions reject plain admins, suspended accounts are rejected |
| `test_chat.py` | Sending a message creates a conversation with a real (mock-provider) reply, conversation history/rename/pin, cross-user access is blocked |
| `test_prompt_engineering.py` | Mode detection and system prompt construction — pure functions, no database needed, run instantly |

### Adding a new test

Use the `client` fixture for HTTP calls and `db_session` for direct DB
assertions/setup (e.g. promoting a test user's role without going through
a role-gated endpoint). `auth_headers` gives you a ready-to-use bearer
token for a seeded student account.

## Frontend (Vitest)

```bash
cd frontend
npm install
npm run test        # single run
npm run test:watch  # watch mode
```

Component tests use `@testing-library/react` and live under
`src/test/`, mirroring the `src/` structure they cover
(`src/test/components/`, `src/test/lib/`, etc).

Current coverage is intentionally focused on pure/presentational logic
(`PasswordStrength`, `Badge`, the `cn()` utility) that doesn't require
mocking the API layer. Expanding to API-dependent components (forms,
admin pages) is a natural next step — mock `src/lib/api.ts` with
`vi.mock()` rather than hitting a real backend.

## What isn't covered yet

- End-to-end browser tests (Playwright/Cypress) — noted as a future
  addition per the ES-004 spec's "Future E2E Testing" line item.
- Load/performance testing.
- AI provider integration tests against real Gemini/OpenAI keys (the
  mock provider is what CI-style runs should use).
