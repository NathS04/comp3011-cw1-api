# COMP3011 CW1 - Upgrade to Outstanding (95%)

## Phase 1: Novel Data Integration (Coding)
- [x] 1.1 Database Schema
    - [x] Add `DataSource` model (provenance tracking)
    - [x] Add `ImportRun` model (execution logs)
    - [x] Add `source_id`, `source_record_id`, `is_seeded` to `Event` model
    - [x] Generate Alembic migration
- [x] 1.2 Import Pipeline
    - [x] Create `scripts/import_dataset.py`
    - [x] Implement idempotency checks
    - [x] Implement error logging and summary stats
    - [x] Add sample CSV dataset (10-30 rows)

## Phase 2: Analytics & Recommendations (Coding)
- [x] 2.1 Analytics Endpoints
    - [x] `GET /analytics/events/seasonality` (SQL aggregation)
    - [x] `GET /analytics/events/trending` (Rolling window scoring)
- [x] 2.2 Recommendation Engine
    - [x] `GET /events/recommendations` (Deterministic scoring algorithm)
- [x] 2.3 Schemas
    - [x] Add Pydantic models for analytics responses

## Phase 3: Testing & Security (Coding)
- [x] 3.1 Tests
    - [x] Test import script (mocked)
    - [x] Test analytics endpoints (data shape)
    - [x] Test recommendations (logic check)
- [x] 3.2 Security
    - [x] Verify auth on new endpoints (public vs protected)

## Phase 4: Documentation (Completed)
- [x] API Documentation PDF (referencing new endpoints)
- [x] Technical Report Upgrade (Novel integration, design, GenAI alternatives)
- [x] Slide Deck Content
- [x] GenAI Logs Appendix
- [x] README with PDF links and GitHub repo
