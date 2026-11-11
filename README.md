# Memory Lane

Memory Lane is a visitor photo-sharing application. Visitors register and
upload photographs that are validated during upload and immediately added to a
continuously running public slideshow.

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
- Multiple JPEG, PNG, and WebP uploads with Pillow content validation
- Local photo storage, per-visitor metadata, and public slideshow delivery
- Immediate slideshow publication after upload-time validation
- Visitor UI for registration, access-code verification, slideshow listing, and
  upload previews/progress
- Public slideshow with automatic cycling and periodic refresh
- Photos are checked for supported format, decodability, and size during
  upload; no approval step is required

Real-time push updates and the admin dashboard remain planned. See
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
- `POST /api/v1/photos/upload` — uploads one or more images as multipart field
  `files`; requires `X-Visitor-Access-Code`.
- `GET /api/v1/photos/my-photos` — lists the authenticated visitor's photo
  metadata.
- `GET /api/v1/photos/{photo_id}` — returns metadata only when the photo belongs
  to the authenticated visitor.
- `DELETE /api/v1/photos/{photo_id}` — deletes an owned photo and its stored
  file; deletion also removes it from the public slideshow.
- `GET /api/v1/slideshow/photos` — lists all uploaded, validated photos for
  public display.
- `GET /api/v1/slideshow/photos/{photo_id}/image` — serves a validated image
  file for the slideshow.
- `GET /api/v1/slideshow/settings` — returns the slide and refresh intervals.

Uploads are limited by `MAX_IMAGE_SIZE_MB` per image and
`MAX_PHOTOS_PER_UPLOAD` per request. `STORAGE_PATH` is private local storage;
uploaded files are not mounted as public static files.

## Backend Tests

From `backend`, run:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Tests use an isolated in-memory SQLite database and do not require a running
PostgreSQL server.

## Frontend Development

In another terminal, from `frontend`, run:

```powershell
npm install
npm run dev
```

Vite proxies `/api` and `/health` to `http://localhost:8000`. Set
`VITE_API_PROXY_TARGET` in `frontend/.env` to override the local API address.
Run `npm run lint` and `npm run build` in `frontend` to validate the UI.
Visitor access codes are held in tab-scoped `sessionStorage`.

## Project Status

Phases 1–5 are complete. The slideshow displays all validated uploads without
an approval queue. Migration `20261111_03` removes the former photo status
column. The slideshow cycles every 7 seconds and refreshes its feed every
5 seconds. Real-time push updates and admin features remain planned.