from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .models import Event, Attendee, RSVP, User
from .schemas import EventCreate, EventUpdate, AttendeeCreate, RSVPCreate, UserCreate

def create_event(db: Session, data: EventCreate) -> Event:
    obj = Event(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_events(
    db: Session, 
    q: Optional[str] = None, 
    location: Optional[str] = None, 
    start_after: Optional[datetime] = None, 
    start_before: Optional[datetime] = None,
    limit: int = 10,
    offset: int = 0,
    offset: int = 0,
    sort: Optional[str] = None,
    min_capacity: Optional[int] = None,
    status: Optional[str] = None
) -> dict:
    stmt = select(Event)
    if q:
        stmt = stmt.where(Event.title.ilike(f"%{q}%"))
    if location:
        stmt = stmt.where(Event.location.ilike(f"%{location}%"))
    if start_after:
        stmt = stmt.where(Event.start_time >= start_after)
    if start_before:
        stmt = stmt.where(Event.start_time <= start_before)
    if min_capacity:
        stmt = stmt.where(Event.capacity >= min_capacity)
    if status:
        now = datetime.utcnow()
        if status == "upcoming":
            stmt = stmt.where(Event.start_time > now)
        elif status == "past":
            stmt = stmt.where(Event.start_time < now)
    
    # Sorting
    if sort:
        desc = sort.startswith("-")
        field_name = sort[1:] if desc else sort
        # Allow sorting only by safe fields
        if field_name in ["start_time", "end_time", "created_at", "title", "capacity"]:
            field = getattr(Event, field_name)
            stmt = stmt.order_by(field.desc() if desc else field.asc())
    else:
        stmt = stmt.order_by(Event.start_time.asc())
        
    # Total count (efficient count)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0

    # Pagination
    stmt = stmt.limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())
    
    return {"items": items, "total": total, "limit": limit, "offset": offset}

def get_event(db: Session, event_id: int):
    return db.query(Event).options(joinedload(Event.rsvps)).filter(Event.id == event_id).first()

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
    # Ensure relationships are loaded if not present
    if 'rsvps' not in event.__dict__:
        db.refresh(event, ['rsvps'])
    
    total_rsvps = len(event.rsvps)
    
    counts = {"going": 0, "maybe": 0, "not_going": 0}
    for rsvp in event.rsvps:
        if rsvp.status in counts:
            counts[rsvp.status] += 1

    going = counts.get("going", 0)
    maybe = counts.get("maybe", 0)
    not_going = counts.get("not_going", 0)
    remaining = max(int(event.capacity) - going, 0)
    return {"event_id": event.id, "going": going, "maybe": maybe, "not_going": not_going, "remaining_capacity": remaining}

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.execute(select(User).where(User.username == username)).scalars().first()

def get_attendee_events(db: Session, attendee_id: int) -> List[Event]:
    stmt = select(Event).join(RSVP).where(RSVP.attendee_id == attendee_id)
    return list(db.execute(stmt).scalars().all())

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.execute(select(User).where(User.email == email)).scalars().first()

def create_user(db: Session, data: UserCreate, hashed_pw: str) -> User:
    obj = User(username=data.username, email=data.email, hashed_password=hashed_pw)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

