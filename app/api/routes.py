from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.db import get_db
from .. import crud
from ..models import RSVP
from ..schemas import (
    EventCreate, EventUpdate, EventOut, EventStatsOut,
    AttendeeCreate, AttendeeOut,
    EventCreate, EventUpdate, EventOut, EventStatsOut, PaginatedResponse,
    AttendeeCreate, AttendeeOut,
    RSVPCreate, RSVPOut,
    UserCreate, UserOut, Token,
)
from ..models import User
from ..core import auth
from fastapi.security import OAuth2PasswordRequestForm

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
    hashed_pw = auth.get_password_hash(payload.password)
    return crud.create_user(db, payload, hashed_pw)

@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.
    """
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/health")
def health():
    """
    Health check endpoint.
    """
    return {"ok": True}

@router.post("/events", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Create a new event (Authenticated users only).
    """
    return crud.create_event(db, payload)

@router.get("/events", response_model=PaginatedResponse[EventOut])
def list_events(
    q: Optional[str] = None, 
    location: Optional[str] = None, 
    start_after: Optional[datetime] = None, 
    start_before: Optional[datetime] = None, 
    limit: int = 10,
    offset: int = 0,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List events with pagination, filtering, and sorting.
    """
    return crud.list_events(db, q=q, location=location, start_after=start_after, start_before=start_before, limit=limit, offset=offset, sort=sort)

@router.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Retrieve specific event details.
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return event

@router.patch("/events/{event_id}", response_model=EventOut)
def patch_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Update an existing event (Authenticated users only).
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return crud.update_event(db, event, payload)

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Delete an event (Authenticated users only).
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    crud.delete_event(db, event)
    return None

@router.post("/attendees", response_model=AttendeeOut, status_code=status.HTTP_201_CREATED)
def create_attendee(payload: AttendeeCreate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Register a new attendee (Authenticated users only).
    """
    try:
        return crud.create_attendee(db, payload)
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

@router.post("/events/{event_id}/rsvps", response_model=RSVPOut, status_code=status.HTTP_201_CREATED)
def create_rsvp(event_id: int, payload: RSVPCreate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    RSVP an attendee to an event (Authenticated users only).
    """
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if not crud.get_attendee(db, payload.attendee_id):
        raise HTTPException(status_code=404, detail="attendee not found")
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
