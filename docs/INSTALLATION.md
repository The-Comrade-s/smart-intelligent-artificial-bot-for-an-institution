# Installation Guide

## Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL 15+ (local, for development — or a Supabase PostgreSQL project for a shared/production database)

## 1. Clone and configure

```bash
git clone <your-repo-url> cosib
cd cosib
```

## 2. Database

Create a local PostgreSQL database:

```sql
CREATE DATABASE cosib;
CREATE USER cosib WITH PASSWORD 'cosib';
GRANT ALL PRIVILEGES ON DATABASE cosib TO cosib;
```

## 3. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- `DATABASE_URL` — your async PostgreSQL connection string
- `DATABASE_URL_SYNC` — same database, sync driver (used by some tooling)

Run migrations and seed data:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
python -m scripts.seed
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/api/docs for interactive API docs.

Default seeded super admin: `admin@cosib.local` / `ChangeMe123!` (change this
immediately — override via `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD` in `.env`
before seeding for a real deployment).

The seed script also creates default `AIProviderSetting` rows for `mock`,
`gemini`, and `openai`, with `mock` active. This means chat works immediately
with no API keys. To switch providers later:

```bash
curl -X POST http://localhost:8000/api/v1/ai/providers/activate \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini"}'
```

(Set `GEMINI_API_KEY` or `OPENAI_API_KEY` in `.env` first — if the key is
missing, `AIManager` automatically falls back to the mock provider rather
than failing requests.)

### Load the knowledge base (DS-001 + DS-002)

```bash
python -m scripts.seed_knowledge_base
```

Ingests verified institutional facts (DS-001) and general Computer Science
curriculum content (DS-002) from `database/seed_data/` into the
`knowledge_articles` and `faqs` tables. Safe to re-run — it skips records
that already exist by title/question. See
`database/seed_data/ds001_institution/` for source citations on every
institutional fact, and note that several fields are explicitly marked
"Information Not Available" rather than guessed — see
`docs/KNOWLEDGE_BASE_SOURCES.md`.

### Load demo/presentation data (optional, recommended for a live demo)

```bash
python -m scripts.seed_demo
```

Adds clearly-fictional sample students, lecturers, courses, conversations
(with real message history), feedback, announcements, and events, so the
admin dashboard and chat history aren't empty during a demo. Demo student
accounts log in with password `DemoPass123!`. Run this *after*
`scripts/seed.py` and `scripts/seed_knowledge_base.py`.

## 4. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit http://localhost:5173.

## 5. Verify

- `GET /api/v1/health` should return `{"status": "ok", ...}`
- Register a student account from the frontend, then log in
- Log in as the seeded super admin to confirm role-based access

## 6. Access the admin portal

Log in as the seeded super admin (`admin@cosib.local`) at http://localhost:5173/login,
then visit http://localhost:5173/admin — or click "Admin" in the chat header,
which only appears for administrator/super administrator accounts.
