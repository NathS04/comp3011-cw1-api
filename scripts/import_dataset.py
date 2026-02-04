
import csv
import sys
import os
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.models import Event, DataSource, ImportRun

# Sample dataset path (place a CSV here)
DATASET_PATH = "scripts/sample_events_dataset.csv"

def get_or_create_data_source(db: Session, name: str, url: str) -> DataSource:
    source = db.scalar(select(DataSource).where(DataSource.name == name))
    if not source:
        source = DataSource(name=name, url=url, license="CC-BY-4.0")
        db.add(source)
        db.commit()
        db.refresh(source)
        print(f"Created new data source: {name}")
    return source

def import_events(csv_path: str):
    db: Session = SessionLocal()
    try:
        # 1. Get/Create DataSource
        source = get_or_create_data_source(db, "Leeds Public Events API", "https://example.com/api/events")
        
        # 2. Create Start ImportRun
        run = ImportRun(data_source_id=source.id, status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        print(f"Started Import Run ID: {run.id}")

        rows_read = 0
        rows_inserted = 0
        rows_updated = 0
        errors = []

        # 3. Read CSV
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows_read += 1
                try:
                    record_id = row["id"]
                    title = row["title"]
                    # Idempotency check
                    existing_event = db.scalar(
                        select(Event).where(Event.source_id == source.id, Event.source_record_id == record_id)
                    )

                    start_dt = datetime.fromisoformat(row["start_time"])
                    end_dt = datetime.fromisoformat(row["end_time"])

                    if existing_event:
                        # Update logic (if changed)
                        existing_event.title = title
                        existing_event.location = row["location"]
                        existing_event.start_time = start_dt
                        existing_event.end_time = end_dt
                        rows_updated += 1
                    else:
                        # Create new
                        new_event = Event(
                            title=title,
                            description=row.get("description", ""),
                            location=row["location"],
                            start_time=start_dt,
                            end_time=end_dt,
                            capacity=int(row["capacity"]),
                            source_id=source.id,
                            source_record_id=record_id,
                            is_seeded=True
                        )
                        db.add(new_event)
                        rows_inserted += 1
                except Exception as e:
                    errors.append({"row": rows_read, "error": str(e), "data": row})

        # 4. Finish ImportRun
        run.finished_at = datetime.now(timezone.utc)
        run.status = "success" if not errors else "partial_success"
        run.rows_read = rows_read
        run.rows_inserted = rows_inserted
        run.rows_updated = rows_updated
        run.errors_json = errors
        db.commit()

        print(f"Import Finished. Status: {run.status}")
        print(f"Read: {rows_read}, Inserted: {rows_inserted}, Updated: {rows_updated}, Errors: {len(errors)}")

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        if 'run' in locals():
            run.status = "failed"
            run.errors_json = {"fatal": str(e)}
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    # Create a dummy CSV if not exists for testing
    if not os.path.exists(DATASET_PATH):
        print("Creating sample dataset...")
        with open(DATASET_PATH, "w") as f:
            f.write("id,title,description,location,start_time,end_time,capacity\n")
            f.write("EXT_001,Advanced AI Workshop,Deep dive into LLMs,Leeds Tech Hub,2026-05-10T10:00:00,2026-05-10T16:00:00,50\n")
            f.write("EXT_002,Community Coding,Social coding event,University Union,2026-05-12T18:00:00,2026-05-12T21:00:00,100\n")
            f.write("EXT_003,Data Science Seminar,Guest speaker on Big Data,Roger Stevens LT,2026-05-15T14:00:00,2026-05-15T15:30:00,200\n")
    
    import_events(DATASET_PATH)
