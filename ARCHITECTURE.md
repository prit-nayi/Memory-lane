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

## API Design

- `POST /api/v1/visitors/register` creates a visitor after consent and name
  validation.
- `POST /api/v1/visitors/verify` verifies an access code and returns the
  visitor profile.
- `GET /api/v1/visitors/me` accepts the access code through the
  `X-Visitor-Access-Code` header rather than a URL.
- `GET /health/database` executes a database connectivity check.

## Image Storage

Local photograph storage will be documented when upload functionality is
implemented.

## Real-time Communication

WebSocket events will be documented when slideshow updates are implemented.