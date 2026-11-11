# Memory Lane Test Plan

## Functional Tests

- Visitor registration succeeds with a valid name and consent.
- Registration trims/collapses name whitespace and refuses blank names.
- Registration refuses missing/false consent.
- Registration returns a formatted access code and does not expose its hash.
- Returning visitor verification succeeds for a valid code and rejects an
  unknown code.
- `GET /api/v1/visitors/me` requires a valid access-code header.
- The database health endpoint executes a database query.

## Validation Tests

- Visitor name length is limited to 100 characters.
- Access codes are normalized case-insensitively and checked against the
  generated-code alphabet and length.

## Security Tests

- Persisted visitor records contain only the access-code digest.
- Access codes are sent in JSON bodies or a header, never in the `/me` URL.
- Visitor response schemas omit the stored digest.

## Concurrent Upload Tests

Not applicable to Phase 2.

## Test Results

- Phase 2 automated API tests: 7 passed using in-memory SQLite.
- PostgreSQL migration: applied at `20261111_01` (head).
- Alembic model/schema consistency: passed; no new upgrade operations detected.
- Python compilation and OpenAPI route checks: passed.