from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal, Generic, TypeVar, List

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator, SecretStr

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int

RSVPStatus = Literal["going", "maybe", "not_going"]

class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    location: str = Field(min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime
    capacity: int = Field(ge=1)

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Capacity must be at least 1")
        return v

    @field_validator("title", "location")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def _time_order(self):
        # Ensure event ends after it starts
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "End of Year Tech Gala",
                "description": "A networking event for tech enthusiasts.",
                "location": "Convention Center, Hall A",
                "start_time": "2026-12-15T18:00:00",
                "end_time": "2026-12-15T22:00:00",
                "capacity": 200
            }
        }
    }

class EventUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = Field(default=None, ge=0)

    @field_validator("title", "location")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip()
        return v

    @model_validator(mode="after")
    def _time_order(self):
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "End of Year Tech Gala (Updated)",
                "capacity": 250
            }
        }
    }

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

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Alex Smith",
                "email": "alex.smith@example.com"
            }
        }
    }

class AttendeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str

class RSVPCreate(BaseModel):
    attendee_id: int
    status: RSVPStatus

    model_config = {
        "json_schema_extra": {
            "example": {
                "attendee_id": 1,
                "status": "going"
            }
        }
    }

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
    password: SecretStr = Field(min_length=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "janedoe",
                "email": "jane@example.com",
                "password": "strongpassword123"
            }
        }
    }

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

