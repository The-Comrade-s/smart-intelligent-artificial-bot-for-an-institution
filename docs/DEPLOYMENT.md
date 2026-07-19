# Deployment Guide (Vercel + Railway + Supabase)

COSIB deploys across three managed platforms, connected via GitHub for
automatic CI/CD:

| Component | Platform | Deploys from |
|---|---|---|
| Frontend (React SPA) | **Vercel** | `frontend/` directory, auto-deploy on push |
| Backend (FastAPI API) | **Railway** | `backend/Dockerfile`, auto-deploy on push |
| Database | **Supabase PostgreSQL** | Managed — provisioned once, not deployed per-push |

This is a deployment-target change only — no application functionality,
architecture, or business logic changed as part of this migration. See
`docs/ARCHITECTURE.md` for the unchanged system design.

## 1. Supabase: provision the database

1. Create a project at [supabase.com](https://supabase.com).
2. Go to **Project Settings -> Database -> Connection string**. Copy the
   **Direct connection** string (port `5432`), not the Transaction Pooler
   (port `6543`) — see the note in `backend/.env.example` for why: this
   app's SQLAlchemy async engine manages its own connection pool and
   asyncpg's prepared statements, which need extra configuration to work
   correctly behind pgbouncer's transaction-pooling mode that this app
   doesn't currently add. If your Supabase plan has a low direct-connection
   limit and you hit it, switch to the **Session Pooler** connection string
   instead (also compatible, different host/port than the Transaction Pooler).
3. Rewrite the copied `postgres://...` string into the two formats this app
   needs:
   - `DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
   - `DATABASE_URL_SYNC=postgresql+psycopg2://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
4. That's it for provisioning — table creation happens via Alembic
   migrations (below), not through the Supabase dashboard.

**On Supabase Auth & Storage**: the stack list for this migration includes
Supabase for "Authentication & Storage." COSIB has its own JWT-based
authentication system (`app/core/security.py`, `app/services/auth_service.py`)
that this migration explicitly preserves rather than replaces — switching
to Supabase Auth would be an authentication *architecture* change, which
was out of scope ("preserve... authentication... without changing
functionality, architecture, or business logic"). Supabase is used here
strictly as the managed PostgreSQL provider. Similarly, file uploads
(`app/api/v1/documents.py`) are processed in-memory and never written to
disk today, so there's no current use for Supabase Storage — `UPLOAD_DIR`
in config is reserved for a future persistent-storage feature, and Supabase
Storage would be the natural choice if that's built later.

## 2. Railway: deploy the backend

1. Push this repository to GitHub (if you haven't already).
2. In the [Railway dashboard](https://railway.app): **New Project -> Deploy
   from GitHub repo**, select this repository.
3. This repo is a monorepo (`backend/` and `frontend/` in one repository).
   Railway needs to know the backend service's root: open the new
   service's **Settings -> Source -> Root Directory** and set it to
   `backend`. This setting can only be made via the dashboard (or the
   GraphQL API) — Railway's config-as-code file (`backend/railway.json`)
   intentionally doesn't control it, so this step can't be skipped by
   editing a file.
4. With Root Directory set to `backend`, Railway automatically discovers
   `backend/railway.json` (build/deploy settings — Dockerfile builder,
   health check path `/api/v1/health`, restart policy) and
   `backend/Dockerfile`. You shouldn't need to touch build settings
   manually — confirm in **Settings -> Build** that the builder shows
   **Dockerfile**.
5. Railway auto-assigns and injects `$PORT` at runtime, which
   `backend/Dockerfile`'s `CMD` already reads — no manual port
   configuration needed, but confirm **Settings -> Networking -> Generate
   Domain** is done so the service gets a public URL.
6. Add environment variables under **Variables** (mark `SECRET_KEY`,
   `DATABASE_URL`, `DATABASE_URL_SYNC`, `GEMINI_API_KEY`, `OPENAI_API_KEY`
   as **sealed/secret** variables; the rest — `APP_ENV=production`,
   `DEBUG=false`, `CORS_ORIGINS`, `CORS_ORIGIN_REGEX`,
   `AI_PROVIDER_DEFAULT` — as plain variables). Full list:
   `backend/.env.example`.
7. Deploy. Connecting the GitHub repo already wires up automatic
   deployment on every push to the selected branch — no extra CI/CD setup
   needed. Railway also builds a preview environment per pull request if
   you enable **PR Environments** in project settings.
8. Note the public URL Railway assigns
   (`https://<service-name>.up.railway.app`, or your custom domain) — you'll
   need it for the frontend's `VITE_API_BASE_URL`.

### First deploy: migrate and seed

Open a shell against the running service — Railway dashboard -> your
service -> the terminal icon (**"SSH"**/shell), or via the CLI
(`railway shell` after `railway link`) — and run:

```bash
cd backend
alembic upgrade head
python -m scripts.seed
python -m scripts.seed_knowledge_base
# Optional, recommended for a live demo:
python -m scripts.seed_demo
```

Migrations are **not** run automatically on deploy — run `alembic upgrade
head` manually after any push that includes a schema change, before
traffic hits the new revision.

## 3. Vercel: deploy the frontend

1. In the [Vercel dashboard](https://vercel.com): **Add New -> Project ->
   Import Git Repository**, select this repository.
2. Set **Root Directory** to `frontend` (this is a monorepo-style layout —
   Vercel needs to know the frontend lives in a subdirectory). Vercel
   auto-detects the Vite framework preset from `frontend/vercel.json` and
   `frontend/package.json`.
3. Add the environment variable `VITE_API_BASE_URL` set to your Railway
   backend URL from step 2.8 above (no trailing slash, no `/api/v1` suffix
   — that's appended by the app).
4. Click **Deploy**. Vercel builds (`npm run build`, output `dist/`) and
   deploys to a `*.vercel.app` URL, and — like Railway — this connection
   registers automatic deployment on every push to your production branch,
   plus a unique preview URL for every other branch/PR.
5. Once you know your production Vercel URL, go back to Railway and update
   `CORS_ORIGINS` to match it exactly (and redeploy the backend, or restart
   the service, for the env var change to take effect).

### Vercel preview deployments and CORS

Every branch/PR gets its own preview URL
(`cosib-frontend-git-<branch>-<org>.vercel.app`), which won't match a
fixed `CORS_ORIGINS` entry. Set `CORS_ORIGIN_REGEX` on the backend (e.g.
`https://cosib-frontend.*\.vercel\.app`) to allow all of them, or leave it
blank and accept that only the production frontend URL can call the API —
reasonable for a small student project where preview deploys aren't
routinely tested against production data.

## 4. HTTPS

Both Vercel and Railway terminate TLS automatically for their
`*.vercel.app` / `*.up.railway.app` domains and any custom domain you
attach — no application code changes needed. The backend's HSTS header
(`Strict-Transport-Security`, set in `app/main.py` when `APP_ENV=production`)
reinforces this at the browser level once you're confident HTTPS is
working correctly end-to-end.

## 5. Custom domains

- **Vercel**: Project Settings -> Domains -> add your domain, follow the
  DNS instructions (usually a CNAME to `cname.vercel-dns.com`).
- **Railway**: Service Settings -> Networking -> Custom Domain -> add your
  domain, follow the DNS instructions (a CNAME to the target Railway gives
  you).
- After adding either, update `CORS_ORIGINS` (backend) and
  `VITE_API_BASE_URL` (frontend) to the new domains and redeploy both.

## 6. Rolling back

- **Vercel**: every deployment is kept and instantly promotable —
  Deployments tab -> select a previous one -> **Promote to Production**.
- **Railway**: Deployments tab on your service -> select a previous
  successful deployment -> **Redeploy**. If a schema migration needs
  reverting too, run `alembic downgrade -1` via the service shell before
  rolling back code that depended on the newer schema.

## 7. Logs

- **Railway**: Runtime and build logs are in the service's **Deployments ->
  View Logs** tab, or via `railway logs` (CLI, after `railway link`). The
  backend uses `structlog`, emitting JSON logs in production
  (`APP_ENV=production`) for easier filtering.
- **Vercel**: Build logs are on each deployment's detail page; there are no
  meaningful runtime server logs for a static SPA (no server-side code runs
  on Vercel here — this is a pure static deployment, not using Vercel
  Functions).
