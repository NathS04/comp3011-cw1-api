# COMP3011 CW1 - Upgrade to Outstanding (95%)

## Phase 1: Novel Data Integration (Coding)
- [ ] 1.1 Database Schema
    - [ ] Add `DataSource` model (provenance tracking)
    - [ ] Add `ImportRun` model (execution logs)
    - [ ] Add `source_id`, `source_record_id`, `is_seeded` to `Event` model
    - [ ] Generate Alembic migration
- [ ] 1.2 Import Pipeline
    - [ ] Create `scripts/import_dataset.py`
    - [ ] Implement idempotency checks
    - [ ] Implement error logging and summary stats
    - [ ] Add sample CSV dataset (10-30 rows)

## Phase 2: Analytics & Recommendations (Coding)
- [ ] 2.1 Analytics Endpoints
    - [ ] `GET /analytics/events/seasonality` (SQL aggregation)
    - [ ] `GET /analytics/events/trending` (Rolling window scoring)
- [ ] 2.2 Recommendation Engine
    - [ ] `GET /events/recommendations` (Deterministic scoring algorithm)
- [ ] 2.3 Schemas
    - [ ] Add Pydantic models for analytics responses

## Phase 3: Testing & Security (Coding)
- [ ] 3.1 Tests
    - [ ] Test import script (mocked)
    - [ ] Test analytics endpoints (data shape)
    - [ ] Test recommendations (logic check)
- [ ] 3.2 Security
    - [ ] Verify auth on new endpoints (public vs protected)

## Phase 4: Documentation (Future Phase - Claude)
- [ ] API Documentation PDF (referencing new endpoints)
- [ ] Technical Report Upgrade (Novel integration, design, GenAI alternatives)
- [ ] Slide Deck Content
