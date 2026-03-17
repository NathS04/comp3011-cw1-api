import argparse
import csv
import hashlib
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import defusedxml.ElementTree as ET
import requests
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models import DataSource, Event, ImportRun

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_xml_date(date_str: str, time_str: str) -> Optional[datetime]:
    """Parse Leeds XML date (DD/MM/YYYY) and time (HH:MM)."""
    try:
        if not date_str or not time_str:
            return None
        dt_str = f"{date_str.strip()} {time_str.strip()}"
        return datetime.strptime(dt_str, "%d/%m/%Y %H:%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def compute_sha256(content: bytes) -> str:
    """Compute SHA256 hash of raw content."""
    return hashlib.sha256(content).hexdigest()


def import_dataset(
    source_type: str, source_url: str, db: Optional[Session] = None
) -> Dict[str, Any]:
    """Import events from an external dataset (XML or CSV).

    Returns a dict with 'status' ('success' or 'failed') and summary fields.
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    start_time = time.time()
    source_name = "Leeds Temporary Events" if source_type == "xml" else "Manual Import"

    try:
        # 1. Get or create DataSource
        source = db.query(DataSource).filter(DataSource.name == source_name).first()
        if not source:
            source = DataSource(
                name=source_name,
                url=source_url,
                license="Open Government Licence (OGL) v3.0",
            )
            db.add(source)
            db.commit()
            db.refresh(source)
            logger.info("Created/Found DataSource: %s (ID: %s)", source.name, source.id)

        # 2. Create ImportRun (running)
        run = ImportRun(
            data_source_id=source.id,
            status="running",
            parser_version="v2_xml_defused" if source_type == "xml" else "v1_csv",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        logger.info("Started Import Run ID: %s", run.id)

        rows_read = 0
        rows_inserted = 0
        rows_updated = 0
        errors: list[dict] = []

        # 3. Fetch Data
        if source_type == "xml":
            logger.info("Fetching XML from %s...", source_url)
            resp = requests.get(source_url, timeout=30)
            resp.raise_for_status()
            raw_content = resp.content
            run.sha256_hash = compute_sha256(raw_content)

            root = ET.fromstring(raw_content)
            items = root.findall("Temporary_Event_Notice")
            if not items:
                items = root.findall(".//Temporary_Event_Notice")

            logger.info("Docs found: %d", len(items))

            for item in items:
                rows_read += 1
                try:
                    record_id = item.findtext("Reference_Number")
                    title = item.findtext("Premises_x0020_Name")
                    desc = item.findtext("Activities")
                    location = item.findtext("Premises_x0020_Address") or title

                    start_d = item.findtext("Event_x0020_Start_x0020_Date")
                    end_d = item.findtext("Event_x0020_End_x0020_Date")
                    start_t = item.findtext("Start_x0020_Times")
                    end_t = item.findtext("End_x0020_Times")

                    if not record_id or not title:
                        continue

                    start_dt = parse_xml_date(start_d, start_t) or datetime.now(timezone.utc)
                    end_dt = parse_xml_date(end_d, end_t) or (start_dt + timedelta(hours=4))

                    existing = (
                        db.query(Event)
                        .filter(Event.source_id == source.id, Event.source_record_id == record_id)
                        .first()
                    )

                    event_data = {
                        "title": title[:200],
                        "description": (desc or "")[:1000],
                        "location": (location or "Leeds")[:200],
                        "start_time": start_dt,
                        "end_time": end_dt,
                        "capacity": 100,
                        "source_id": source.id,
                        "source_record_id": record_id,
                        "is_seeded": False,
                    }

                    if existing:
                        for k, v in event_data.items():
                            setattr(existing, k, v)
                        rows_updated += 1
                    else:
                        db.add(Event(**event_data))
                        rows_inserted += 1

                except Exception as row_err:
                    errors.append({"row": rows_read, "error": str(row_err)})

        elif source_type == "csv":
            with open(source_url, encoding="utf-8") as f:
                f.seek(0)
                run.sha256_hash = compute_sha256(f.read().encode("utf-8"))
                f.seek(0)

                reader = csv.DictReader(f)
                for row in reader:
                    rows_read += 1
                    try:
                        record_id = row.get("EventId")
                        if not record_id:
                            continue

                        title = row.get("EventTitle", "")
                        desc = row.get("Description")
                        location = row.get("Venue")

                        start_raw = row.get("StartDate", "")
                        end_raw = row.get("EndDate", "")
                        if not start_raw or not end_raw:
                            continue
                        try:
                            start_dt = datetime.fromisoformat(start_raw).replace(
                                tzinfo=timezone.utc
                            )
                            end_dt = datetime.fromisoformat(end_raw).replace(
                                tzinfo=timezone.utc
                            )
                        except ValueError:
                            continue

                        existing = (
                            db.query(Event)
                            .filter(
                                Event.source_id == source.id,
                                Event.source_record_id == record_id,
                            )
                            .first()
                        )

                        event_data = {
                            "title": (title or "")[:200],
                            "description": (desc or "")[:1000],
                            "location": (location or "Leeds")[:200],
                            "start_time": start_dt,
                            "end_time": end_dt,
                            "capacity": int(row.get("Capacity", 100)),
                            "source_id": source.id,
                            "source_record_id": record_id,
                            "is_seeded": False,
                        }

                        if existing:
                            for k, v in event_data.items():
                                setattr(existing, k, v)
                            rows_updated += 1
                        else:
                            db.add(Event(**event_data))
                            rows_inserted += 1

                    except Exception as row_err:
                        errors.append({"row": rows_read, "error": str(row_err)})

        # 4. Finalize
        run.status = "success"
        run.finished_at = datetime.now(timezone.utc)
        run.rows_read = rows_read
        run.rows_inserted = rows_inserted
        run.rows_updated = rows_updated
        run.duration_ms = int((time.time() - start_time) * 1000)
        if errors:
            run.errors_json = {"errors": errors[:50]}

        db.commit()
        logger.info(
            "Import Finished. Duration: %dms. Read: %d, Inserted: %d, Updated: %d",
            run.duration_ms, rows_read, rows_inserted, rows_updated,
        )
        return {
            "status": "success",
            "rows_read": rows_read,
            "rows_inserted": rows_inserted,
            "rows_updated": rows_updated,
            "duration_ms": run.duration_ms,
        }

    except Exception as e:
        logger.error("Fatal Import Error: %s", str(e))
        if "run" in locals():
            run.status = "failed"
            run.finished_at = datetime.now(timezone.utc)
            run.errors_json = {"fatal": str(e)}
            db.commit()
        return {"status": "failed", "error": str(e)}
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["csv", "xml"], default="xml")
    parser.add_argument(
        "--url",
        default="https://opendata.leeds.gov.uk/downloads/Licences/temp-event-notice/temp-event-notice.xml",
    )
    args = parser.parse_args()
    import_dataset(args.type, args.url)
