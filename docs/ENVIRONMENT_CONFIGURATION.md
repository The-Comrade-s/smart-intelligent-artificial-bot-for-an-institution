# Environment Configuration

## Backend (`backend/.env`)

| Variable | Description | Example |
|---|---|---|
| `APP_ENV` | `development` \| `staging` \| `production` | `production` |
| `DEBUG` | Enables SQL echo + verbose errors | `false` in production |
| `SECRET_KEY` | JWT signing key — must be long and random | generate with `secrets.token_urlsafe(64)` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `14` |
| `DATABASE_URL` | Async PostgreSQL URL (`postgresql+asyncpg://...`) | Supabase's **Direct connection** string, rewritten with the `+asyncpg` driver — see `backend/.env.example` |
| `DATABASE_URL_SYNC` | Sync PostgreSQL URL (`postgresql+psycopg2://...`), used by some tooling | Same Supabase connection, `+psycopg2` driver |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `https://cosib-frontend.vercel.app` |
| `CORS_ORIGIN_REGEX` | Optional regex to also allow Vercel preview URLs | `https://cosib-frontend.*\.vercel\.app` |
| `AI_PROVIDER_DEFAULT` | Active provider until an admin switches it via the UI | `mock` |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` | Only needed once you move off the mock provider | — |
| `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD` | Used by `scripts/seed.py` | change before first deploy |

## Frontend (`frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Base origin of the deployed backend (Railway URL) — **no trailing slash, no `/api/v1` suffix**, that's appended by the app. Required in production since the frontend (Vercel) and backend (Railway) are on different domains; a relative path won't reach the API. |

## Platform environment variables

### Railway (backend)

Set via the Railway dashboard's Variables tab (see `backend/railway.json`
for the build/deploy settings reference; environment variables themselves
are set separately in the Variables tab, marking anything sensitive as
sealed/secret rather than plain):
`SECRET_KEY`, `DATABASE_URL`, `DATABASE_URL_SYNC` (all sealed — never
plain env vars), plus `APP_ENV=production`, `DEBUG=false`, `CORS_ORIGINS`,
`CORS_ORIGIN_REGEX`, `AI_PROVIDER_DEFAULT`, and the AI provider keys
(sealed) once you're ready to use them.

### Vercel (frontend)

Project Settings -> Environment Variables:
`VITE_API_BASE_URL` pointing at your Railway backend URL. Vite bakes this
in at build time, so changing it requires a redeploy (Vercel does this
automatically if you push a commit; for an env-var-only change, trigger a
manual redeploy from the Vercel dashboard).

### Supabase (database)

No application env vars live in Supabase itself — you pull the connection
string *from* Supabase into Railway's `DATABASE_URL` / `DATABASE_URL_SYNC`.
Supabase project settings (connection pooling mode, password rotation) are
managed in the Supabase dashboard directly.

Never commit a real `.env` file — only `.env.example` is checked into git.
