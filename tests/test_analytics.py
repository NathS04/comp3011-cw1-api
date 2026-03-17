from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.api.analytics import _month_expr
from app.models import RSVP, Attendee, Event


def test_month_expr_uses_sqlite_strftime(db):
    """Verify that _month_expr selects the SQLite strftime branch for in-memory SQLite."""
    expr = _month_expr("sqlite", Event.start_time)
    compiled = str(expr.compile(compile_kwargs={"literal_binds": True}))
    assert "strftime" in compiled.lower()


def test_month_expr_uses_postgresql_functions():
    """Verify that the PostgreSQL branch uses date_trunc + to_char."""
    expr = _month_expr("postgresql", Event.start_time)
    compiled = str(expr.compile(compile_kwargs={"literal_binds": True}))
    lowered = compiled.lower()
    assert "date_trunc" in lowered
    assert "to_char" in lowered


def test_seasonality_response_shape(client: TestClient, db):
    """Verify JSON response shape is stable after portability refactor."""
    ev = Event(
        title="Shape Test",
        location="Central Hall",
        start_time=datetime(2026, 6, 15, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 15, 3, tzinfo=timezone.utc),
        capacity=50,
    )
    db.add(ev)
    db.commit()

    resp = client.get("/analytics/events/seasonality")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    item = data["items"][0]
    assert set(item.keys()) == {"month", "count", "top_locations"}
    assert item["month"] == "2026-06"
    assert item["count"] >= 1
    assert isinstance(item["top_locations"], list)


def test_seasonality_top_locations_regression(client: TestClient, db):
    """Regression: top_locations must contain actual location strings, not nulls."""
    for loc in ["Leeds Arena", "Leeds Arena", "Town Hall"]:
        db.add(Event(
            title=f"Evt at {loc}",
            location=loc,
            start_time=datetime(2026, 4, 10, tzinfo=timezone.utc),
            end_time=datetime(2026, 4, 10, 2, tzinfo=timezone.utc),
            capacity=20,
        ))
    db.commit()

    resp = client.get("/analytics/events/seasonality")
    assert resp.status_code == 200
    items = resp.json()["items"]
    april = [i for i in items if i["month"] == "2026-04"]
    assert len(april) == 1
    assert "Leeds Arena" in april[0]["top_locations"]


def test_seasonality_endpoint(client: TestClient, db):
    # Seed events in different months
    # Note: depends on client fixture using same db, which we ensured with StaticPool

    # Check empty first
    response = client.get("/analytics/events/seasonality")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_seasonality_uses_top_locations_field(client: TestClient, db):
    """Verify the schema field is `top_locations` (not the old `top_categories`)."""
    from app.models import Event

    ev = Event(
        title="Loc Test",
        location="Leeds Centre",
        start_time=datetime(2026, 3, 1, tzinfo=timezone.utc),
        end_time=datetime(2026, 3, 1, 2, tzinfo=timezone.utc),
        capacity=10,
    )
    db.add(ev)
    db.commit()

    resp = client.get("/analytics/events/seasonality")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1
    # Must have `top_locations`, NOT `top_categories`
    assert "top_locations" in items[0]
    assert "top_categories" not in items[0]
    assert "Leeds Centre" in items[0]["top_locations"]
def test_trending_events(client: TestClient, db, auth_headers):
    # Create event
    response = client.post(
        "/events",
        json={
            "title": "Trending Party",
            "location": "Club",
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.utcnow() + timedelta(days=1, hours=2)).isoformat(),
            "capacity": 100
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    event_id = response.json().get("id")

    # Add RSVP
    # First create attendee
    att_resp = client.post("/attendees", json={"name": "Fan", "email": "fan@example.com"}, headers=auth_headers)
    attendee_id = att_resp.json().get("id")

    client.post(f"/events/{event_id}/rsvps", json={"attendee_id": attendee_id, "status": "going"}, headers=auth_headers)

    # Check trending
    resp = client.get("/analytics/events/trending")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert data[0]["event_id"] == event_id
    assert data[0]["trending_score"] > 0

def test_recommendations_cold_start(client: TestClient, auth_headers):
    # User with no history
    resp = client.get("/events/recommendations", headers=auth_headers)
    if resp.status_code != 200:
        print(resp.json())
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert "user_id" in data

def test_recommendations_personalized(client: TestClient, auth_headers, db):
    # 1. Setup: Ensure user has an attendee record
    # auth_headers comes from a fixture creating a user with email "test@example.com" or similar.
    # We need to know the specific email. The auth fixture logic usually allows us to know this or we inspect the token?
    # Actually, simpler: create a new user/token dynamic here if needed, OR just match the email used in conftest.
    # Assuming conftest uses "test@example.com".

    # Let's inspect the `auth_headers` user identity by hitting /auth/me if it exists, or just use a known email.
    # The standard conftest usually sets `test@example.com`.
    user_email = "authtest@example.com"

    # Create Attendee linked to this user
    client.post("/attendees", json={"name": "Test User", "email": user_email}, headers=auth_headers)
    att = db.query(Attendee).filter(Attendee.email == user_email).first()
    assert att is not None

    # 2. Create History: User attended an event at "Preferred Location"
    past_event = Event(
        title="Past Event",
        description="Desc",
        location="Preferred Location",
        start_time=datetime.now(timezone.utc) - timedelta(days=20),
        end_time=datetime.now(timezone.utc) - timedelta(days=20, hours=2),
        capacity=100
    )
    db.add(past_event)
    db.commit()
    db.refresh(past_event)

    rsvp = RSVP(event_id=past_event.id, attendee_id=att.id, status="going")
    db.add(rsvp)
    db.commit()

    # 3. Create Future Events
    # Target Event (Same Location)
    target_event = Event(
        title="Target Event",
        description="Desc",
        location="Preferred Location",
        start_time=datetime.now(timezone.utc) + timedelta(days=5),
        end_time=datetime.now(timezone.utc) + timedelta(days=5, hours=2),
        capacity=100
    )
    # Noise Event (Different Location)
    noise_event = Event(
        title="Noise Event",
        description="Desc",
        location="Ignored Location",
        start_time=datetime.now(timezone.utc) + timedelta(days=5),
        end_time=datetime.now(timezone.utc) + timedelta(days=5, hours=2),
        capacity=100
    )
    db.add(target_event)
    db.add(noise_event)
    db.commit()

    # 4. Verify Recommendations
    resp = client.get("/events/recommendations", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    recs = data["recommendations"]
    rec_ids = [r["event_id"] for r in recs]

    # Assert Target is recommended
    assert target_event.id in rec_ids
    # Assert Noise is NOT recommended (because logic filters by location)
    assert noise_event.id not in rec_ids

    # Verify reason text
    target_rec = next(r for r in recs if r["event_id"] == target_event.id)
    assert "Preferred Location" in target_rec["reason"]
