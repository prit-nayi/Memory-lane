# Project Assumptions

- Visitor registration requires explicit photo-sharing consent.
- Visitor access codes are 16 random characters (80 bits of entropy), formatted
  in groups of four for readability. The code is shown only in the registration
  response; returning visitors must retain it.
- The project-root `.env` file supplies the PostgreSQL connection string as
  `DATABASE_URL`. `.env.example` contains safe setup guidance.
- Phase 2 API tests use in-memory SQLite so the test suite does not mutate a
  developer's PostgreSQL database.
- Phase 3 accepts JPEG, PNG, and WebP image contents; filename extensions and
  client-provided MIME types are not trusted.
- Upload limits default to 10 MB per image and 10 images per request, and are
  configurable through the existing `MAX_IMAGE_SIZE_MB` and
  `MAX_PHOTOS_PER_UPLOAD` environment variables.
- Image files remain in non-public local storage. Slideshow listing and image
  delivery require the owner's access code; visitors cannot see other users'
  photos.
- Photos are published automatically after upload validation; there is no
  approval queue. Owners can remove their own published photos.
- Slideshow controls are device-local preferences stored in browser local
  storage; they do not change playback on other connected screens.
- Administrator accounts are bootstrapped from environment credentials using
  the explicit bootstrap command; admin passwords are salted and hashed in the
  database. Admin bearer tokens expire after the configured lifetime.
- Visitor management disables/reactivates accounts rather than deleting
  visitor records or their photos.
- Admin slideshow settings are persisted shared defaults; visitor display
  duration and fade-speed preferences may override them locally.
- WebSocket broadcasts are process-local and assume a single backend worker;
  multi-worker deployments require shared pub/sub.