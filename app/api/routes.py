from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud
from ..core import auth
from ..core.config import settings
from ..core.db import get_db
from ..models import RSVP, ImportRun, User
from ..schemas import (
    AttendeeCreate,
    AttendeeOut,
    EventCreate,
    EventOut,
    EventProvenanceOut,
    EventStatsOut,
    EventUpdate,
    PaginatedResponse,
    RSVPCreate,
    RSVPOut,
    Token,
    UserCreate,
    UserOut,
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    if crud.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.get_password_hash(payload.password.get_secret_value())
    user = crud.create_user(db, payload, hashed_pw)
    logger.info(f"New user registered: {user.username}")
    return user

@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.
    """
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"User logged in: {user.username}")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}  # nosec B105

@router.get("/health", tags=["system"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check with deployment metadata.
    """
    try:
        # Check DB connection
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "online",
        "database": db_status,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "commit": settings.GIT_SHA,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/events", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    return crud.create_event(db, payload, user_id=current_user.id)

@router.get("/events", response_model=PaginatedResponse[EventOut])
def list_events(
    q: Optional[str] = None,
    location: Optional[str] = None,
    start_after: Optional[datetime] = None,
    start_before: Optional[datetime] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: Optional[str] = None,
    min_capacity: Optional[int] = Query(None, ge=1),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List events with pagination, filtering, and sorting.
    """
    return crud.list_events(db, q=q, location=location, start_after=start_after, start_before=start_before, limit=limit, offset=offset, sort=sort, min_capacity=min_capacity, status=status)

@router.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Retrieve specific event details.
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return event


@router.get("/events/{event_id}/provenance", response_model=EventProvenanceOut)
def get_event_provenance(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")

    if event.source_id is None:
        return EventProvenanceOut(event_id=event.id, is_user_created=True)

    ds = event.data_source
    latest_run = (
        db.query(ImportRun)
        .filter(ImportRun.data_source_id == event.source_id)
        .order_by(ImportRun.started_at.desc())
        .first()
    )
    return EventProvenanceOut(
        event_id=event.id,
        source_name=ds.name if ds else None,
        source_url=ds.url if ds else None,
        source_record_id=event.source_record_id,
        import_run_id=latest_run.id if latest_run else None,
        imported_at=latest_run.started_at if latest_run else None,
        latest_import_at=latest_run.started_at if latest_run else None,
        parser_version=latest_run.parser_version if latest_run else None,
        sha256_hash=latest_run.sha256_hash if latest_run else None,
        is_seeded=event.is_seeded,
        is_user_created=False,
    )


@router.patch("/events/{event_id}", response_model=EventOut)
def patch_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if event.created_by_user_id is not None and event.created_by_user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorised to modify this event")
    return crud.update_event(db, event, payload)

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if event.created_by_user_id is not None and event.created_by_user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorised to delete this event")
    crud.delete_event(db, event)
    return None

@router.post("/attendees", response_model=AttendeeOut, status_code=status.HTTP_201_CREATED)
def create_attendee(payload: AttendeeCreate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Register a new attendee (Authenticated users only).
    """
    try:
        return crud.create_attendee(db, payload, owner_user_id=current_user.id)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="email already exists")

@router.get("/attendees/{attendee_id}", response_model=AttendeeOut)
def get_attendee(attendee_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific attendee.
    """
    attendee = crud.get_attendee(db, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="attendee not found")
    return attendee

@router.get("/attendees/{attendee_id}/events", response_model=List[EventOut])
def get_attendee_events(attendee_id: int, db: Session = Depends(get_db)):
    """
    Get all events for a specific attendee.
    """
    attendee = crud.get_attendee(db, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="attendee not found")
    return crud.get_attendee_events(db, attendee_id)

@router.post("/events/{event_id}/rsvps", response_model=RSVPOut, status_code=status.HTTP_201_CREATED)
def create_rsvp(event_id: int, payload: RSVPCreate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    RSVP an attendee to an event (Authenticated users only).
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    attendee = crud.get_attendee(db, payload.attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="attendee not found")
    if attendee.owner_user_id is not None and attendee.owner_user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorised to RSVP for this attendee")
    try:
        return crud.create_rsvp(db, event_id, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="duplicate RSVP for this attendee/event")

@router.get("/events/{event_id}/rsvps", response_model=List[RSVPOut])
def list_event_rsvps(event_id: int, db: Session = Depends(get_db)):
    """
    List all RSVPs for a specific event.
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return crud.list_rsvps_for_event(db, event_id)

@router.delete("/events/{event_id}/rsvps/{rsvp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_rsvp(event_id: int, rsvp_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Remove an RSVP (Authenticated users only).
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    rsvp = db.get(RSVP, rsvp_id)
    if not rsvp or rsvp.event_id != event_id:
        raise HTTPException(status_code=404, detail="rsvp not found")
    attendee = rsvp.attendee
    attendee_owner = attendee.owner_user_id if attendee else None
    can_delete = current_user.is_admin or attendee_owner == current_user.id or event.created_by_user_id == current_user.id
    if not can_delete:
        raise HTTPException(status_code=403, detail="Not authorised to delete this RSVP")
    crud.delete_rsvp(db, rsvp)
    return None

@router.get("/events/{event_id}/stats", response_model=EventStatsOut)
def event_stats(event_id: int, db: Session = Depends(get_db)):
    """
    Get detailed statistics for an event (e.g., total attendees).
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return crud.get_event_stats(db, event)
