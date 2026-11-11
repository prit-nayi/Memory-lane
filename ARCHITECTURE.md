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
| `status` | varchar(8) | Required; `pending`, `approved`, or `rejected` |
| `created_at` | timestamp with time zone | Required, database default |
| `updated_at` | timestamp with time zone | Required, database default |

Photo files are written to the configured local storage directory and are not
served as public static assets. Only photo metadata is returned by visitor
endpoints; access is scoped to the visitor identified by their access code.
Uploads are staged and validated before their metadata is committed. Failed
requests clean up staged/finalized files. Visitors can delete pending or
rejected photos; approved photos are read-only to visitors.

## API Design

- `POST /api/v1/visitors/register` creates a visitor after consent and name
  validation.
- `POST /api/v1/visitors/verify` verifies an access code and returns the
  visitor profile.
- `GET /api/v1/visitors/me` accepts the access code through the
  `X-Visitor-Access-Code` header rather than a URL.
- `GET /health/database` executes a database connectivity check.
- `POST /api/v1/photos/upload` validates and stores multiple JPEG, PNG, or
  WebP images for the authenticated visitor.
- `GET /api/v1/photos/my-photos` lists only the authenticated visitor's photos.
- `GET /api/v1/photos/{photo_id}` returns metadata only to the photo's owner.
- `DELETE /api/v1/photos/{photo_id}` removes an owned pending/rejected photo.

## Image Storage

`STORAGE_PATH` selects the local upload directory (relative paths resolve from
the project root). Uploads are first streamed to temporary files in that
directory, with a configurable per-image byte limit. Pillow verifies and
decodes each image before it is moved to a generated UUID filename. Database
records store that generated key; client filenames are display metadata only.
Only JPEG, PNG, and WebP content is accepted, and the API does not expose a
public static mount for the upload directory.

## Real-time Communication

WebSocket events will be documented when slideshow updates are implemented.