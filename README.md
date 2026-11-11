# Memory Lane

Memory Lane is a visitor photo-sharing application. Visitors register and
upload photographs that are validated during upload and immediately added to a
continuously running personal slideshow visible only to the visitor who owns
those photographs.

## Technology Stack

- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: PostgreSQL with SQLAlchemy and Alembic
- Realtime updates: WebSockets

## Current Features

- Visitor registration with consent validation
- Unique, human-readable visitor access codes
- Returning visitor verification and profile lookup
- PostgreSQL visitor persistence and Alembic migrations
- Multiple JPEG, PNG, and WebP uploads with Pillow content validation
- Local photo storage, per-visitor metadata, and owner-scoped slideshow delivery
- Immediate slideshow publication after upload-time validation
- Visitor UI for registration, access-code verification, slideshow listing, and
  upload previews/progress
- Authenticated personal slideshow with automatic cycling and periodic refresh
- Live WebSocket updates with automatic reconnection
- Slideshow controls for play/pause, previous/next, shuffle, fullscreen,
  slide duration, and fade speed
- Admin portal for visitor/photo management and shared slideshow defaults
- Photos are checked for supported format, decodability, and size during
  upload; no approval step is required

## Local Setup

1. Install PostgreSQL and create the `memory_lane` database.
2. Copy `.env.example` to `.env` and set `DATABASE_URL` to the local PostgreSQL
   connection string. Do not commit `.env`.
3. From `backend`, install the pinned packages and apply migrations:

   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   .\venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
   ```

4. Configure `ADMIN_USERNAME`, `ADMIN_PASSWORD` (at least 12 characters), and
   `ADMIN_TOKEN_SECRET` (at least 32 random characters) in `.env`, then create
   or update the administrator record:

   ```powershell
   .\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
   .\venv\Scripts\python.exe -m app.bootstrap_admin
   ```

   Running the bootstrap command again updates the configured admin password.
   The database stores only its salted password hash.

5. Start the API from `backend`:

   ```powershell
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

6. Open `http://localhost:8000/docs` to try the APIs. Use
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
  file; deletion also removes it from the owner's slideshow.
- `GET /api/v1/slideshow/photos` — lists uploaded, validated photos owned by
  the visitor identified by `X-Visitor-Access-Code`.
- `GET /api/v1/slideshow/photos/{photo_id}/image` — serves a validated image
  file only to its owner.
- `GET /api/v1/slideshow/settings` — returns the slide and refresh intervals.
- `WS /api/v1/slideshow/ws` — notifies connected slideshow screens after an
  upload or deletion; screens reload their own photo feed on reconnect.
- `POST /api/v1/admin/login` — exchanges administrator credentials for a
  short-lived signed bearer token.
- `GET /api/v1/admin/dashboard` — returns visitor and photo counts.
- `GET /api/v1/admin/visitors` and `PATCH /api/v1/admin/visitors/{id}` — list,
  disable, or reactivate visitor accounts without deleting their photos.
- `GET /api/v1/admin/photos?visitor_id={id}` and
  `DELETE /api/v1/admin/photos/{photo_id}` — review visitor photo history and
  remove photos.
- `GET /api/v1/admin/settings` and `PUT /api/v1/admin/settings` — manage
  persistent slideshow defaults and available controls.

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

Phases 1–7 are complete. Each visitor's slideshow displays only their validated
uploads; other visitors' photo feeds and image endpoints are inaccessible.
Deleting a photo removes it from the owner's slideshow and prevents further
image access.
Migration `20261111_03` removes the former photo status column; `20261111_04`
adds admin management and slideshow settings. The slideshow cycles every
7 seconds by default and refreshes its feed every 5 seconds; timing preferences
are stored on each display device.
WebSocket notifications are process-local; multi-worker deployments require a
shared pub/sub service.