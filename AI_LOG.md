# AI Development Log

Record AI prompts, responses, mistakes, verification and corrections.

| Date | Task | AI Tool | AI Mistake | Correction |
|---|---|---|---|---|
| 2026-11-11 | Phase 2 SQLAlchemy visitor model, access-code registration/verification APIs, migrations and tests | Copilot SDK | Initial test placement mixed fixture and endpoint tests | Separated shared test setup into `backend/tests/conftest.py` and API tests into `backend/tests/test_visitors.py`; all seven tests passed and the PostgreSQL migration/model consistency check succeeded |