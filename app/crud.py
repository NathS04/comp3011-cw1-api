from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Event, Attendee, RSVP
from .schemas import EventCreate, EventUpdate, AttendeeCreate, RSVPCreate

def create_event(db: Session, data: EventCreate) -> Event:
    obj = Event(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_events(db: Session, q: Optional[str] = None, location: Optional[str] = None, start_after: Optional[datetime] = None, start_before: Optional[datetime] = None) -> List[Event]:
    stmt = select(Event)
    if q:
        stmt = stmt.where(Event.title.ilike(f"%{q}%"))
    if location:
        stmt = stmt.where(Event.location.ilike(f"%{location}%"))
    if start_after:
        stmt = stmt.where(Event.start_time >= start_after)
    if start_before:
        stmt = stmt.where(Event.start_time <= start_before)
    stmt = stmt.order_by(Event.start_time.asc())
    return list(db.execute(stmt).scalars().all())

def get_event(db: Session, event_id: int) -> Optional[Event]:
    return db.get(Event, event_id)

def update_event(db: Session, event: Event, data: EventUpdate) -> Event:
    patch = data.model_dump(exclude_unset=True)
    for k, v in patch.items():
        setattr(event, k, v)
    db.commit()
    db.refresh(event)
    return event

def delete_event(db: Session, event: Event) -> None:
    db.delete(event)
    db.commit()

def create_attendee(db: Session, data: AttendeeCreate) -> Attendee:
    obj = Attendee(**data.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj

def get_attendee(db: Session, attendee_id: int) -> Optional[Attendee]:
    return db.get(Attendee, attendee_id)

def create_rsvp(db: Session, event_id: int, data: RSVPCreate) -> RSVP:
    obj = RSVP(event_id=event_id, attendee_id=data.attendee_id, status=data.status)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj

def list_rsvps_for_event(db: Session, event_id: int) -> List[RSVP]:
    stmt = select(RSVP).where(RSVP.event_id == event_id).order_by(RSVP.created_at.asc())
    return list(db.execute(stmt).scalars().all())

def delete_rsvp(db: Session, rsvp: RSVP) -> None:
    db.delete(rsvp)
    db.commit()

def get_event_stats(db: Session, event: Event):
    stmt = select(RSVP.status, func.count(RSVP.id)).where(RSVP.event_id == event.id).group_by(RSVP.status)
    rows = db.execute(stmt).all()
    counts = {status: count for status, count in rows}
    going = int(counts.get("going", 0))
    maybe = int(counts.get("maybe", 0))
    not_going = int(counts.get("not_going", 0))
    remaining = max(int(event.capacity) - going, 0)
    return {"event_id": event.id, "going": going, "maybe": maybe, "not_going": not_going, "remaining_capacity": remaining}
