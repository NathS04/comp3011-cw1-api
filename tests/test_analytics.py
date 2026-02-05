
from fastapi.testclient import TestClient
from app.models import Event, DataSource, ImportRun, User, RSVP, Attendee
import pytest
from datetime import datetime, timedelta

def test_seasonality_endpoint(client: TestClient, db):
    # Seed events in different months
    # Note: depends on client fixture using same db, which we ensured with StaticPool
    
    # Check empty first
    response = client.get("/analytics/events/seasonality")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

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
    user_email = "test@example.com"

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
