# Folder Structure

```
cosib/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers (auth, users, courses, lecturers, announcements,
│   │   │                       chat, conversations, knowledge_base, documents, ai_config,
│   │   │                       events, feedback, analytics, settings, audit_logs,
│   │   │                       notifications, admin, departments, health)
│   │   ├── core/            # config, security, deps (RBAC), permissions, exceptions, logging, rate limiting
│   │   ├── db/               # session, declarative base
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/            # business logic, incl. ai_providers/ (mock/gemini/openai + manager)
│   │   └── main.py               # FastAPI app entrypoint
│   ├── alembic/                    # migrations
│   ├── scripts/
│   │   ├── seed.py                     # department + super admin + AI/app settings
│   │   ├── seed_knowledge_base.py       # ingests DS-001 + DS-002 into KnowledgeArticle/FAQ
│   │   └── seed_demo.py                  # demo/presentation mode sample data
│   ├── tests/backend/                # pytest suite
│   ├── Dockerfile                      # production image, built by Railway
│   ├── railway.json                      # Railway build/deploy config (health check, restart policy)
│   ├── .dockerignore
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/            # LandingPage, LoginPage, RegisterPage, ChatPage, NotFoundPage,
│   │   │                        errors/ (401, 403, 500, offline, maintenance), admin/ (12 admin pages)
│   │   ├── layouts/            # AdminLayout, AuthSplitLayout
│   │   ├── components/           # ChatSidebar, ChatMessageBubble, QuickActionCards, TerminalDemo, ui/ (component library)
│   │   ├── routes/            # ProtectedRoute
│   │   ├── store/               # authStore (React context)
│   │   ├── lib/                   # api.ts (axios, cross-origin-safe base URL), chatApi.ts, adminApi.ts, academicsApi.ts, utils.ts
│   │   ├── test/                    # Vitest component/unit tests
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── vercel.json                   # Vercel build + SPA rewrite + headers config
│   ├── package.json
│   └── .env.example
├── database/           # DS-001/002/003 seed datasets + reserved for ERD exports
│   └── seed_data/
│       ├── ds001_institution/   # institution.json, department.json, academic_regulations.json, student_services.json, faq.json
│       ├── ds002_academic/      # programming.json, algorithms.json, ... quiz_bank.json, flashcards.json, learning_paths.json
│       └── ds003_dynamic/       # announcements.json, events.json, feedback.json, suggested_prompts.json, ai_configuration.json, conversation_analytics.json
├── docs/                # this documentation set
├── uploads/documents|images|pdfs   # reserved for future persistent file storage (not currently used — see docs/DEPLOYMENT.md)
└── assets/               # brand assets (logo, etc.)
```
