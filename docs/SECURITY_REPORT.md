# Security Report

Self-assessment against the ES-005 security review checklist, written
against the actual implementation — not a generic checklist filled in
optimistically.

## Authentication

- **JWT access tokens** (30 min default) + **rotating refresh tokens** (14
  days default, single-use — each refresh revokes the old token and issues
  a new one). See `app/core/security.py`, `app/services/auth_service.py`.
- **Passwords hashed with bcrypt** via `passlib`, never stored or logged in
  plain text. See `hash_password()` in `app/core/security.py`.
- **Password complexity enforced** at registration: minimum 8 characters,
  at least one digit, at least one uppercase letter (`RegisterRequest`
  validator in `app/schemas/auth.py`).
- **Refresh tokens stored hashed** (SHA-256) in the database, not in plain
  text — a database leak doesn't directly expose usable tokens.

## Authorization (RBAC)

- Every sensitive route is gated with `Depends(require_roles(...))`,
  checked directly against `User.role` — explicit and auditable per route.
- Suspended/deactivated accounts are rejected at the `get_current_user`
  dependency level, not just at login — a suspended user's existing token
  stops working immediately rather than remaining valid until expiry.
- See `docs/ARCHITECTURE.md` and `app/core/permissions.py` for how this is
  structured to support future granular permissions without a rewrite.

## Input validation

- Every request body is a Pydantic model — type coercion and validation
  happen before a route handler runs; malformed input returns `422`
  automatically, not a stack trace.
- File uploads are validated by extension (`pdf`/`docx`/`txt` allowlist,
  not a denylist) and size (`MAX_UPLOAD_SIZE_MB`, default 15MB) before
  processing — see `app/api/v1/documents.py`.

## Injection protection

- **SQL injection**: all database access goes through SQLAlchemy's async
  ORM with parameterized queries — no raw string-formatted SQL anywhere in
  the codebase.
- **Prompt injection**: the system prompt explicitly instructs the model
  never to reveal or discuss its own instructions, and knowledge-base
  context is clearly delimited from the user's message in the prompt
  structure (see `app/services/prompt_engineering.py`). This reduces but,
  as with any LLM-based system, cannot fully eliminate prompt injection
  risk — no absolute claim is made here.

## Transport & headers

- **CORS** is configured via an explicit origin allowlist
  (`CORS_ORIGINS`), not a wildcard.
- **HTTPS** is enforced at the infrastructure level (Vercel and Railway both
  terminate TLS automatically for their platform domains and any custom
  domain attached).
- **Security headers** are set on every response via middleware
  (`app/main.py`): `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`,
  a restrictive `Permissions-Policy`, and `Strict-Transport-Security` in
  production. A full Content-Security-Policy is not set, since the
  frontend is a separate static site rather than server-rendered by this
  service — CSP is better configured at the static-site/CDN layer if
  needed.

## Rate limiting

- `slowapi`-based rate limiting is applied throughout: chat endpoints
  (`RATE_LIMIT_CHAT`, default 20/minute), authentication endpoints —
  `/auth/login` and `/auth/register` (`RATE_LIMIT_AUTH`, default
  10/minute) to slow down credential-stuffing and registration abuse, and
  a general default (`RATE_LIMIT_DEFAULT`, 100/minute) for everything else.

## Auditability

- Sensitive actions (role changes, status changes) are recorded in
  `AuditLog` with actor, action, resource, IP address, and timestamp,
  readable only by super administrators.
- Structured logging (`structlog`) throughout, JSON-formatted in
  production for log-aggregator compatibility.

## Secrets management

- All secrets (`SECRET_KEY`, database credentials, AI provider keys) are
  environment variables, never hardcoded — `.env` is gitignored, only
  `.env.example` (with placeholder values) is committed.
- `SECRET_KEY` is generated once (`secrets.token_urlsafe(64)`) and stored
  as a Railway sealed variable; `DATABASE_URL`/`DATABASE_URL_SYNC` are pulled from
  Supabase's connection string and likewise stored as Railway sealed variables —
  neither touches the repository.

## Database security (Supabase-specific)

- All database access goes through the backend's own SQLAlchemy layer with
  application-level RBAC (`require_roles`) — the database is not exposed
  directly to the frontend, so Supabase's Row Level Security (RLS) and
  PostgREST auto-API, while available on the platform, are not part of
  this app's access-control path and don't need to be configured. Access
  control lives entirely in `app/core/deps.py` and route-level
  `require_roles` checks, unchanged from the previous deployment target.
- Rotate the Supabase database password periodically via the Supabase
  dashboard (Project Settings -> Database -> Reset database password), and
  update the corresponding Railway sealed variable afterward.

## Known gaps / recommended hardening before any production use beyond an academic presentation

1. Add CSRF protection if cookie-based sessions are ever introduced (not
   currently used — the app is bearer-token-only, which is inherently not
   CSRF-vulnerable in the same way cookie auth is, but worth stating
   explicitly rather than leaving implicit).
2. Add automated dependency vulnerability scanning (e.g. `pip-audit`,
   `npm audit`) to a CI pipeline, if one is set up.
3. Consider a Web Application Firewall (WAF) or DDoS protection layer
   (e.g. Cloudflare in front of Railway, or Railway's own platform-level
   protections) for a real production deployment beyond a school
   presentation.
4. Consider a proper Content-Security-Policy at the static-site/CDN layer.
