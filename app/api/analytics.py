
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, select, desc
from datetime import datetime, timedelta, timezone
from typing import List

from app.core.db import get_db
from app.models import Event, RSVP, Attendee
from app.schemas import SeasonalityResponse, SeasonalityItem, TrendingItem, RecommendationResponse, RecommendationItem
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/analytics/events/seasonality", response_model=SeasonalityResponse)
def get_event_seasonality(db: Session = Depends(get_db)):
    """
    Get event aggregation by month to identify seasonal trends.
    """
    events = db.scalars(select(Event)).all()
    
    # Aggregation by month with location tracking
    month_data = {}
    for event in events:
        month_key = event.start_time.strftime("%Y-%m")
        if month_key not in month_data:
            month_data[month_key] = {"count": 0, "locations": {}}
        month_data[month_key]["count"] += 1
        loc = event.location or "Unknown"
        month_data[month_key]["locations"][loc] = month_data[month_key]["locations"].get(loc, 0) + 1
        
    # Format response with top locations derived from data
    items = []
    for month, data in sorted(month_data.items()):
        # Get top 3 locations for this month
        sorted_locs = sorted(data["locations"].items(), key=lambda x: x[1], reverse=True)
        top_locs = [loc for loc, count in sorted_locs[:3]]
        items.append(SeasonalityItem(
            month=month,
            count=data["count"],
            top_categories=top_locs if top_locs else ["N/A"]
        ))
        
    return SeasonalityResponse(items=items)

@router.get("/analytics/events/trending", response_model=List[TrendingItem])
def get_trending_events(window_days: int = 30, limit: int = 5, db: Session = Depends(get_db)):
    """
    Identify trending events based on recent RSVP activity.
    Trending Score = (Recent RSVPs * 1.5) + (Total RSVPs * 0.5)
    """
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    
    # Fetch events with their RSVPs
    events = db.scalars(select(Event)).all()
    
    trending = []
    for event in events:
        total_rsvps = len(event.rsvps)
        # Handle offset-naive vs aware datetimes for SQLite
        try:
            recent_rsvps = sum(1 for r in event.rsvps if r.created_at.replace(tzinfo=None) >= cutoff)
        except:
            recent_rsvps = sum(1 for r in event.rsvps if r.created_at >= cutoff.replace(tzinfo=timezone.utc))
        
        score = (recent_rsvps * 1.5) + (total_rsvps * 0.5)
        
        if score > 0:
            trending.append(TrendingItem(
                event_id=event.id,
                title=event.title,
                trending_score=score,
                recent_rsvps=recent_rsvps
            ))
            
    # Sort by score desc
    trending.sort(key=lambda x: x.trending_score, reverse=True)
    return trending[:limit]

@router.get("/events/recommendations", response_model=RecommendationResponse)
def get_recommendations(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Personalized event recommendations based on user's past RSVP history (mock logic for demo).
    Algorithm:
    1. Find events user attended.
    2. Recommend future events in same location or similar time of day.
    """
    # 1. Get user's past events
    # We need to find the attendee record linked to this user email
    attendee = db.scalar(select(Attendee).where(Attendee.email == user.email))
    
    if not attendee:
        # Cold start: recommend trending future events
        upcoming = db.scalars(
            select(Event)
            .where(Event.start_time > datetime.utcnow())
            .order_by(Event.start_time)
            .limit(5)
        ).all()
        
        recs = [
            RecommendationItem(
                event_id=e.id, title=e.title, score=1.0, 
                reason="Top upcoming event", location=e.location, start_time=e.start_time
            ) for e in upcoming
        ]
        return RecommendationResponse(recommendations=recs, user_id=user.id)

    # 2. Logic for returning user
    # Find locations they frequent
    past_rsvps = attendee.rsvps
    visited_locations = {r.event.location for r in past_rsvps}
    
    # Recommend future events at those locations
    candidates = db.scalars(
        select(Event)
        .where(Event.start_time > datetime.utcnow())
        .where(Event.location.in_(visited_locations))
    ).all()
    
    recs = []
    for event in candidates:
        if any(r.event_id == event.id for r in past_rsvps):
            continue # Already RSVPd
            
        recs.append(RecommendationItem(
            event_id=event.id,
            title=event.title,
            score=0.9,
            reason=f"Based on your interest in {event.location}",
            location=event.location,
            start_time=event.start_time
        ))
        
    return RecommendationResponse(recommendations=recs, user_id=user.id)
