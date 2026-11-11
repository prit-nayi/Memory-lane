# Memory Lane Test Plan

## Functional Tests

- Visitor UI routes expose registration, returning visitor, dashboard, and
  upload workflows.
- Registration form requires a name and explicit consent; successful
  registration presents the access code and a copy action.
- Returning visitor form formats the access code, reports API failures, and
  navigates to the dashboard after successful verification.
- Dashboard loads photo metadata and slideshow availability, with empty and loading
  states.
- Upload page previews multiple supported images, allows removing selections,
  reports progress/errors, and refreshes the visitor's collection on success.
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
- Make a newly uploaded valid image immediately available to the public
  slideshow.
- Serve an uploaded image through the slideshow image endpoint.
- Delete an owned photo and remove it from the slideshow and local storage.

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
  exposed through a static directory mount.
- Slideshow API intentionally publishes validated image files without visitor
  authentication.
- Failed multi-image uploads leave no files or photo records behind.
- Visitor access codes are stored only in tab-scoped `sessionStorage`, not the
  URL or persistent local storage.

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
- Phase 4 frontend build: passed.
- Phase 4 ESLint: passed.
- Browser smoke checks: home and registration/returning routes render; invalid
  access code displays the API error, and Vite `/health` proxy reaches FastAPI.
- Phase 4 browser end-to-end: registration and one-time code display, returning
  visitor verification, dashboard photo listing, image preview/upload with
  upload completion, and owner deletion all passed against local FastAPI and
  PostgreSQL. Temporary visitor, photo, and image fixture were cleaned up.
- Direct publication change: backend suite passed (19 tests), including public
  feed/image access, upload validation, and status-free photo deletion.
- PostgreSQL migration `20261111_03`: applied; Alembic model/schema check
  reports no new upgrade operations.
- Direct publication browser smoke: registered a temporary visitor, uploaded
  a validated image, confirmed the upload success message, and verified the
  image was in the public feed and served with HTTP 200; temporary data was
  removed.
- Frontend ESLint and production build: passed.