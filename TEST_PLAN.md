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
- Make a newly uploaded valid image immediately available only to its owner's
  slideshow.
- Serve an uploaded image through the slideshow image endpoint.
- Deny another visitor access to the photo list and image endpoint.
- Delete an owned photo and remove it from the owner's slideshow and storage.
- Verify connected slideshow WebSocket clients receive updates after photo
  uploads and deletions.
- Verify the slideshow reconnects and reloads the photo feed after a dropped
  WebSocket connection.
- Verify pause/resume, previous/next, shuffle, fullscreen, slide duration,
  fade speed, and persisted display preferences.
- Verify admin login, expired/tampered token rejection, protected admin routes,
  dashboard counts, visitor disable/reactivation, photo deletion, visitor photo
  history, and persisted slideshow defaults.

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
- Slideshow API requires visitor authentication and scopes validated image
  files to their owners.
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
- Direct publication change: backend suite passed (19 tests), including
  slideshow feed/image access, upload validation, and status-free photo deletion.
- PostgreSQL migration `20261111_03`: applied; Alembic model/schema check
  reports no new upgrade operations.
- Direct publication browser smoke: registered a temporary visitor, uploaded
  a validated image, confirmed the upload success message, and verified the
  image was in the public feed and served with HTTP 200; temporary data was
  removed.
- Frontend ESLint and production build: passed.
- Phase 6 WebSocket upload/deletion notification test: passed as part of the
  20-test backend suite.
- Slideshow browser smoke: live connection established; a photo uploaded in a
  separate visitor session appeared in the connected slideshow feed without a
  page refresh.
- Slideshow browser controls: pause/resume, previous/next, shuffle, hide/show,
  duration updates, persisted preferences after reload, slide advancement at
  the selected duration, fade speed, and fullscreen were verified.
- Browser showed a reconnecting state after the backend was stopped; a full
  reconnect-after-restart browser check could not be completed because the
  browser page handle expired. Automatic reconnect and feed refresh are
  implemented in the client hook.
- Owner privacy regression suite: two visitors receive only their own feed;
  cross-owner image reads return 404; deleting a photo removes it from the feed
  and blocks image reads.
- Phase 7 admin API suite: admin password login, signed-token protection,
  visitor disable/reactivation, photo history/deletion, and slideshow settings
  passed in the 26-test backend suite.
- Phase 7 admin frontend: lint and production build passed.