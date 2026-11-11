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
- Image files remain in non-public local storage. The slideshow image API is
  intentionally public so shared photos can be displayed to all visitors.
- Photos are published automatically after upload validation; there is no
  approval queue. Owners can remove their own published photos.