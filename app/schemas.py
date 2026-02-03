from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RSVPStatus = Literal["going", "maybe", "not_going"]

class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    location: str = Field(min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime
    capacity: int = Field(ge=0)

    @model_validator(mode="after")
    def _time_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self

class EventUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _time_order(self):
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time")
        return self

class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    location: str
    start_time: datetime
    end_time: datetime
    capacity: int
    created_at: datetime

class AttendeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=255)

class AttendeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str

class RSVPCreate(BaseModel):
    attendee_id: int
    status: RSVPStatus

class RSVPOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_id: int
    attendee_id: int
    status: str
    created_at: datetime

class EventStatsOut(BaseModel):
    event_id: int
    going: int
    maybe: int
    not_going: int
    remaining_capacity: int

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

