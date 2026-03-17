from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models import RSVP, Attendee, Event, User
from app.schemas import RecommendationItem, RecommendationResponse, SeasonalityItem, SeasonalityResponse, TrendingItem

router = APIRouter()


def _month_expr(dialect_name: str, col: Any) -> Any:
    """Return a dialect-aware SQL expression that extracts YYYY-MM from a datetime column."""
    if dialect_name == "postgresql":
        return func.to_char(func.date_trunc("month", col), "YYYY-MM")
    return func.strftime("%Y-%m", col)


@router.get("/analytics/events/seasonality", response_model=SeasonalityResponse)
def get_event_seasonality(db: Session = Depends(get_db)) -> SeasonalityResponse:
    """Get event aggregation by month using dialect-aware SQL GROUP BY."""
    month = _month_expr(db.get_bind().dialect.name, Event.start_time)

    stmt = (
        select(
            month.label("month"),
            func.count(Event.id).label("event_count"),
        )
        .group_by(month)
        .order_by(month)
    )
    rows = db.execute(stmt).all()

    loc_stmt = (
        select(
            month.label("month"),
            Event.location,
            func.count(Event.id).label("loc_count"),
        )
        .group_by(month, Event.location)
        .order_by(month, desc(func.count(Event.id)))
    )
    loc_rows = db.execute(loc_stmt).all()

    month_locations: dict[str, list[str]] = {}
    for row in loc_rows:
        m = row.month
        if m not in month_locations:
            month_locations[m] = []
        if len(month_locations[m]) < 3:
            month_locations[m].append(row.location or "Unknown")

    items = [
        SeasonalityItem(
            month=row.month,
            count=row.event_count,
            top_locations=month_locations.get(row.month, ["N/A"]),
        )
        for row in rows
    ]
    return SeasonalityResponse(items=items)


@router.get("/analytics/events/trending", response_model=list[TrendingItem])
def get_trending_events(
    window_days: int = 30,
    limit: int = 5,
    db: Session = Depends(get_db),
) -> list[TrendingItem]:
    """Trending events by weighted RSVP activity, computed in SQL."""
    cutoff = datetime.utcnow() - timedelta(days=window_days)

    total_rsvps = (
        select(RSVP.event_id, func.count(RSVP.id).label("total_count"))
        .group_by(RSVP.event_id)
        .subquery("total_rsvps")
    )

    recent_rsvps = (
        select(RSVP.event_id, func.count(RSVP.id).label("recent_count"))
        .where(RSVP.created_at >= cutoff)
        .group_by(RSVP.event_id)
        .subquery("recent_rsvps")
    )

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
            (func.coalesce(total_rsvps.c.total_count, 0) > 0)
            | (func.coalesce(recent_rsvps.c.recent_count, 0) > 0)
        )
        .order_by(
            desc(
                func.coalesce(recent_rsvps.c.recent_count, 0) * 1.5
                + func.coalesce(total_rsvps.c.total_count, 0) * 0.5
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
def get_recommendations(
    user: User = Depends(get_current_user),  # type: ignore[assignment]
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    """Personalised event recommendations based on RSVP history."""
    attendee = db.scalar(select(Attendee).where(Attendee.email == user.email))

    if not attendee:
        upcoming = db.scalars(
            select(Event)
            .where(Event.start_time > datetime.utcnow())
            .order_by(Event.start_time)
            .limit(5)
        ).all()

        recs = [
            RecommendationItem(
                event_id=e.id,
                title=e.title,
                score=1.0,
                reason="Top upcoming event",
                location=e.location,
                start_time=e.start_time,
            )
            for e in upcoming
        ]
        return RecommendationResponse(recommendations=recs, user_id=user.id)

    past_rsvps = attendee.rsvps
    visited_locations = {r.event.location for r in past_rsvps}

    candidates = db.scalars(
        select(Event)
        .where(Event.start_time > datetime.utcnow())
        .where(Event.location.in_(visited_locations))
    ).all()

    recs = []
    for event in candidates:
        if any(r.event_id == event.id for r in past_rsvps):
            continue

        recs.append(
            RecommendationItem(
                event_id=event.id,
                title=event.title,
                score=0.9,
                reason=f"Based on your interest in {event.location}",
                location=event.location,
                start_time=event.start_time,
            )
        )

    return RecommendationResponse(recommendations=recs, user_id=user.id)
