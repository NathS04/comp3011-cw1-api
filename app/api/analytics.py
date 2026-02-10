
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, select, desc, case, literal_column, text
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
    Get event aggregation by month using SQL GROUP BY.
    Uses database-level aggregation for scalability.
    """
    # SQL aggregate: GROUP BY month, COUNT events per month
    # strftime works on both SQLite and can be adapted for PostgreSQL
    month_expr = func.strftime("%Y-%m", Event.start_time)
    
    stmt = (
        select(
            month_expr.label("month"),
            func.count(Event.id).label("event_count"),
        )
        .group_by(month_expr)
        .order_by(month_expr)
    )
    
    rows = db.execute(stmt).all()
    
    # For top locations per month, use a secondary grouped query
    loc_stmt = (
        select(
            month_expr.label("month"),
            Event.location,
            func.count(Event.id).label("loc_count"),
        )
        .group_by(month_expr, Event.location)
        .order_by(month_expr, desc(func.count(Event.id)))
    )
    loc_rows = db.execute(loc_stmt).all()
    
    # Build location lookup {month: [top locations]}
    month_locations: dict = {}
    for row in loc_rows:
        m = row.month
        if m not in month_locations:
            month_locations[m] = []
        if len(month_locations[m]) < 3:  # Top 3 locations
            month_locations[m].append(row.location or "Unknown")
    
    items = [
        SeasonalityItem(
            month=row.month,
            count=row.event_count,
            top_categories=month_locations.get(row.month, ["N/A"])
        )
        for row in rows
    ]
    
    return SeasonalityResponse(items=items)

@router.get("/analytics/events/trending", response_model=List[TrendingItem])
def get_trending_events(window_days: int = 30, limit: int = 5, db: Session = Depends(get_db)):
    """
    Identify trending events using SQL aggregation.
    Trending Score = (Recent RSVPs * 1.5) + (Total RSVPs * 0.5)
    Computed entirely in SQL for scalability.
    """
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    
    # SQL subquery: count total RSVPs and recent RSVPs per event
    total_rsvps = (
        select(
            RSVP.event_id,
            func.count(RSVP.id).label("total_count"),
        )
        .group_by(RSVP.event_id)
        .subquery("total_rsvps")
    )
    
    recent_rsvps = (
        select(
            RSVP.event_id,
            func.count(RSVP.id).label("recent_count"),
        )
        .where(RSVP.created_at >= cutoff)
        .group_by(RSVP.event_id)
        .subquery("recent_rsvps")
    )
    
    # Main query: JOIN events with RSVP counts, compute score
    stmt = (
        select(
            Event.id,
            Event.title,
            func.coalesce(total_rsvps.c.total_count, 0).label("total"),
            func.coalesce(recent_rsvps.c.recent_count, 0).label("recent"),
        )
        .outerjoin(total_rsvps, Event.id == total_rsvps.c.event_id)
        .outerjoin(recent_rsvps, Event.id == recent_rsvps.c.event_id)
        .where(
            (func.coalesce(total_rsvps.c.total_count, 0) > 0) |
            (func.coalesce(recent_rsvps.c.recent_count, 0) > 0)
        )
        .order_by(
            desc(
                func.coalesce(recent_rsvps.c.recent_count, 0) * 1.5 +
                func.coalesce(total_rsvps.c.total_count, 0) * 0.5
            )
        )
        .limit(limit)
    )
    
    rows = db.execute(stmt).all()
    
    return [
        TrendingItem(
            event_id=row.id,
            title=row.title,
            trending_score=(row.recent * 1.5) + (row.total * 0.5),
            recent_rsvps=row.recent,
        )
        for row in rows
    ]

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
