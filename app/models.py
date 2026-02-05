from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, DateTime, Integer, ForeignKey, UniqueConstraint, Boolean, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

class Base(DeclarativeBase):
    pass

class DataSource(Base):
    """
    SQLAlchemy model representing an external data source (e.g., CSV file, public API).
    """
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    import_runs: Mapped[List["ImportRun"]] = relationship("ImportRun", back_populates="data_source")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="data_source")

    def __repr__(self):
        return f"<DataSource(name={self.name})>"

class ImportRun(Base):
    """
    SQLAlchemy model tracking execution of data import jobs.
    """
    __tablename__ = "import_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_source_id: Mapped[int] = mapped_column(ForeignKey("data_sources.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20))  # 'running', 'success', 'failed'
    rows_read: Mapped[int] = mapped_column(Integer, default=0)
    rows_inserted: Mapped[int] = mapped_column(Integer, default=0)
    rows_updated: Mapped[int] = mapped_column(Integer, default=0)
    rows_updated: Mapped[int] = mapped_column(Integer, default=0)
    errors_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # 95+ Band Provenance Fields
    sha256_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    parser_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    data_source: Mapped["DataSource"] = relationship("DataSource", back_populates="import_runs")

    def __repr__(self):
        return f"<ImportRun(id={self.id}, status={self.status})>"

class Event(Base):
    """
    SQLAlchemy model representing an event.
    """
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    location: Mapped[str] = mapped_column(String(200))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    capacity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Provenance fields
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("data_sources.id"), nullable=True)
    source_record_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # ID in the external system
    is_seeded: Mapped[bool] = mapped_column(Boolean, default=False)

    rsvps: Mapped[List["RSVP"]] = relationship("RSVP", back_populates="event", cascade="all, delete-orphan")
    data_source: Mapped[Optional["DataSource"]] = relationship("DataSource", back_populates="events")

    def __repr__(self):
        return f"<Event(title={self.title}, location={self.location})>"

class Attendee(Base):
    """
    SQLAlchemy model representing an event attendee.
    """
    __tablename__ = "attendees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    rsvps: Mapped[List["RSVP"]] = relationship("RSVP", back_populates="attendee", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Attendee(name={self.name}, email={self.email})>"

class RSVP(Base):
    """
    SQLAlchemy model representing an RSVP (link between Event and Attendee).
    """
    __tablename__ = "rsvps"
    __table_args__ = (UniqueConstraint("event_id", "attendee_id", name="uq_rsvp_event_attendee"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    attendee_id: Mapped[int] = mapped_column(ForeignKey("attendees.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    event: Mapped["Event"] = relationship("Event", back_populates="rsvps")
    attendee: Mapped["Attendee"] = relationship("Attendee", back_populates="rsvps")

    def __repr__(self):
        return f"<RSVP(event_id={self.event_id}, attendee_id={self.attendee_id}, status={self.status})>"

class User(Base):
    """
    SQLAlchemy model representing a registered system user.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
