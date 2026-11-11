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
- Upload multiple valid images and verify metadata and local storage.
- List and retrieve photos belonging to the authenticated visitor.
- Delete a pending photo and remove its local file.
- Reject visitor deletion of approved photos.

## Validation Tests

- Visitor name length is limited to 100 characters.
- Access codes are normalized case-insensitively and checked against the
  generated-code alphabet and length.
- Accept only decodable JPEG, PNG, and WebP content regardless of filename or
  client-provided MIME type.
- Reject corrupt images, files over the configured size, and batches over the
  configured count.

## Security Tests

- Persisted visitor records contain only the access-code digest.
- Access codes are sent in JSON bodies or a header, never in the `/me` URL.
- Visitor response schemas omit the stored digest.
- Photo metadata and deletion are scoped to the authenticated visitor.
- Client filenames are not used in storage paths and upload files are not
  served publicly.
- Failed multi-image uploads leave no files or photo records behind.

## Concurrent Upload Tests

Concurrent request stress tests are not yet implemented. Upload batches are
bounded by configuration, and failed-batch cleanup is tested.

## Test Results

- Phase 2 automated API tests: 7 passed using in-memory SQLite.
- Phase 2 PostgreSQL migration: applied at `20261111_01`.
- Alembic model/schema consistency: passed; no new upgrade operations detected.
- Python compilation and OpenAPI route checks: passed.
- Phase 3 photo tests: 9 passed using in-memory SQLite.
- PostgreSQL photo migration: applied at `20261111_02`.