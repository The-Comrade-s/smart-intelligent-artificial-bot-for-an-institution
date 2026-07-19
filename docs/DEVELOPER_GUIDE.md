# Developer Guide

## Architecture

COSIB follows a modular, layered architecture on both sides of the stack.

### Backend (`backend/app/`)

```
core/       # config, security (JWT/bcrypt), RBAC deps, exceptions, logging, rate limiting
db/         # async engine/session, declarative base + mixins (UUID PK, timestamps)
models/     # SQLAlchemy ORM models, one file per domain area
schemas/    # Pydantic request/response models
services/   # business logic (kept out of route handlers so it's testable)
api/v1/     # route handlers, thin — validate input, call services, return schema
```

Route handlers should stay thin: validate the request (Pydantic does most of
this automatically), call a service function, map the result to a response
schema. Business logic belongs in `services/`, not in the route function.

### Frontend (`frontend/src/`)

```
lib/api.ts        # axios instance with auth header + refresh-token interceptor
store/authStore    # React context for auth state (user, login, register, logout)
routes/            # route guards (ProtectedRoute)
pages/             # top-level route components
components/        # shared/reusable UI (populated further in ES-004)
```

## Adding a new database model

1. Create the model in `app/models/<domain>.py` using `UUIDMixin` + `TimestampMixin`.
2. Import it in `app/models/__init__.py` (required for Alembic autogenerate).
3. Run `alembic revision --autogenerate -m "add <thing>"`.
4. Review the generated migration before applying — autogenerate doesn't
   always catch everything (e.g. some index/constraint changes).
5. `alembic upgrade head`.

## Adding a new API route module

1. Add Pydantic schemas in `app/schemas/`.
2. Add a service function in `app/services/` if there's real business logic.
3. Add the router in `app/api/v1/<name>.py`.
4. Register it in `app/api/v1/router.py`.
5. Protect write operations with `Depends(require_roles(...))` from `app.core.deps`.

## Authentication model

- Access tokens: short-lived JWT (30 min default), sent as `Authorization: Bearer <token>`.
- Refresh tokens: longer-lived (14 days), stored hashed in the `refresh_tokens`
  table, rotated on every use (old token is marked revoked, a new one issued).
- The frontend axios client automatically retries a request once with a
  refreshed token on `401`, then redirects to `/login` if refresh also fails.

## Error format

Every error response follows:

```json
{ "success": false, "error": { "code": "SOME_CODE", "message": "Human readable message" } }
```

Raise `AppError` subclasses from `app.core.exceptions` (`NotFoundError`,
`UnauthorizedError`, `ForbiddenError`, `ConflictError`) rather than raw
`HTTPException` where possible, for consistency.

## Coding standards

- Type hints everywhere (Python) / strict TypeScript (frontend).
- No business logic in route handlers.
- No placeholder implementations without an explicit marker (see
  `app/api/v1/future_modules.py` for how deferred modules are handled).
- One model/schema/router per domain file — don't grow a single giant file.
