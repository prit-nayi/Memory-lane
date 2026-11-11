# Memory Lane

Memory Lane is a visitor photo-sharing application. Visitors register, upload
photographs for moderation, and approved photographs appear on a continuously
running slideshow.

## Technology Stack

- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: PostgreSQL with SQLAlchemy and Alembic
- Realtime updates: WebSockets (planned)

## Current Features

- Visitor registration with consent validation
- Unique, human-readable visitor access codes
- Returning visitor verification and profile lookup
- PostgreSQL visitor persistence and Alembic migrations

Photo uploads, moderation, the visitor-facing frontend, slideshow, and admin
features are planned for later phases. See
[Project_implementation_plan.md](./Project_implementation_plan.md) for the
roadmap.

## Local Setup

1. Install PostgreSQL and create the `memory_lane` database.
2. Copy `.env.example` to `.env` and set `DATABASE_URL` to the local PostgreSQL
   connection string. Do not commit `.env`.
3. From `backend`, install the pinned packages and apply migrations:

   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   .\venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
   ```

4. Start the API from `backend`:

   ```powershell
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

5. Open `http://localhost:8000/docs` to try the visitor APIs. Use
   `GET /health/database` to check PostgreSQL connectivity.

## Visitor API

- `POST /api/v1/visitors/register` — accepts `name` and `consent`; returns the
  access code once.
- `POST /api/v1/visitors/verify` — verifies an access code and returns the
  visitor profile.
- `GET /api/v1/visitors/me` — returns the profile for the code supplied in the
  `X-Visitor-Access-Code` header.

## Backend Tests

From `backend`, run:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Tests use an isolated in-memory SQLite database and do not require a running
PostgreSQL server.

## Project Status

Phases 1 and 2 are complete. Phase 2 tests pass and its visitor migration has
been applied to the configured PostgreSQL database.