# Memory Lane Architecture

## Technology Stack

- React + Vite frontend
- FastAPI backend
- PostgreSQL database accessed through SQLAlchemy
- Alembic schema migrations

## System Architecture

The backend separates HTTP routes (`app/api`), request/response validation
(`app/schemas`), visitor persistence and business logic (`app/services`), and
SQLAlchemy models (`app/models`). Configuration is loaded from the project-root
`.env` file. Database sessions are provided per request and closed after use.

The React visitor app is routed through React Router. Visitor and photo API
calls are isolated in `frontend/src/services`, with the visitor code and profile
managed by context. In local development Vite proxies `/api` and `/health` to
FastAPI; this avoids requiring permissive development CORS settings.

Visitor access codes are held in tab-scoped `sessionStorage`, validated against
`GET /api/v1/visitors/me` when restoring a session, and sent in the
`X-Visitor-Access-Code` request header for protected API calls. Photo previews
use browser object URLs and do not expose server-side local file paths.

## Database Design

### `visitors`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | Primary key |
| `name` | varchar(100) | Required |
| `access_code_hash` | varchar(64) | Required, unique |
| `created_at` | timestamp with time zone | Required, database default |
| `updated_at` | timestamp with time zone | Required, database default |

Access codes contain 16 random characters from an alphabet that omits
ambiguous characters. The formatted code is returned only during registration;
the database stores its SHA-256 digest. The code's 80 bits of random entropy
are the basis for using a fast digest rather than a password-oriented hash.

### `photos`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | Primary key |
| `visitor_id` | UUID | Required foreign key to `visitors.id`, cascade on visitor deletion |
| `original_filename` | varchar(255) | Required; used only as display metadata |
| `storage_key` | varchar(41) | Required, unique, generated UUID filename |
| `content_type` | varchar(32) | Required; inferred from decoded image format |
| `file_size` | integer | Required; bytes |
| `created_at` | timestamp with time zone | Required, database default |
| `updated_at` | timestamp with time zone | Required, database default |

Photo files are written to the configured local storage directory and are not
mounted as public static assets. Uploads are staged and validated before their
metadata is committed. Failed requests clean up staged/finalized files.
Validated photos are published to the public slideshow immediately. Visitor
metadata operations are scoped to the visitor identified by their access code;
slideshow image delivery is intentionally public. Owners may delete their own
photos, which removes them from the slideshow.

## API Design

- `POST /api/v1/visitors/register` creates a visitor after consent and name
  validation.
- `POST /api/v1/visitors/verify` verifies an access code and returns the
  visitor profile.
- `GET /api/v1/visitors/me` accepts the access code through the
  `X-Visitor-Access-Code` header rather than a URL.
- `GET /health/database` executes a database connectivity check.
- `POST /api/v1/photos/upload` validates and stores multiple JPEG, PNG, or
  WebP images for the authenticated visitor; they are published immediately.
- `GET /api/v1/photos/my-photos` lists only the authenticated visitor's photos.
- `GET /api/v1/photos/{photo_id}` returns metadata only to the photo's owner.
- `DELETE /api/v1/photos/{photo_id}` removes an owned photo.
- `GET /api/v1/slideshow/photos` lists all validated photos available to the
  public slideshow.
- `GET /api/v1/slideshow/photos/{photo_id}/image` serves an image file to the
  slideshow.
- `GET /api/v1/slideshow/settings` supplies the display intervals.

## Image Storage

`STORAGE_PATH` selects the local upload directory (relative paths resolve from
the project root). Uploads are first streamed to temporary files in that
directory, with a configurable per-image byte limit. Pillow verifies and
decodes each image before it is moved to a generated UUID filename. Database
records store that generated key; client filenames are display metadata only.
Only JPEG, PNG, and WebP content is accepted, and the API does not expose a
public static mount for the upload directory.

## Real-time Communication

WebSocket events will be documented when real-time push updates are implemented.