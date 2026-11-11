# Project Assumptions

- Visitor registration requires explicit photo-sharing consent.
- Visitor access codes are 16 random characters (80 bits of entropy), formatted
  in groups of four for readability. The code is shown only in the registration
  response; returning visitors must retain it.
- The project-root `.env` file supplies the PostgreSQL connection string as
  `DATABASE_URL`. `.env.example` contains safe setup guidance.
- Phase 2 API tests use in-memory SQLite so the test suite does not mutate a
  developer's PostgreSQL database.