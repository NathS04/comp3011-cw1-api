import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from scripts.import_dataset import import_dataset

from ..core import auth
from ..core.db import get_db
from ..models import DataSource, ImportRun, User
from ..schemas import ImportQualityItem, ImportQualityResponse, ImportRunOut

router = APIRouter(prefix="/admin", tags=["admin"])

logger = logging.getLogger(__name__)


@router.post("/imports/run", status_code=status.HTTP_201_CREATED)
def run_import(
    source_type: str = Query("xml", pattern="^(xml|csv)$"),
    source_url: str = Query(
        "https://opendata.leeds.gov.uk/downloads/Licences/temp-event-notice/temp-event-notice.xml"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin_user),
):
    result = import_dataset(source_type, source_url, db)

    if result.get("status") == "failed":
        logger.error("Import failed: %s", result.get("error", "unknown"))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Import failed — upstream data source error",
        )

    return {
        "message": "Import finished successfully",
        "source": source_url,
        "rows_inserted": result.get("rows_inserted", 0),
        "rows_updated": result.get("rows_updated", 0),
    }


@router.get("/imports", response_model=List[ImportRunOut])
def list_imports(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin_user),
):
    return db.query(ImportRun).order_by(ImportRun.started_at.desc()).limit(limit).all()


@router.get("/dataset/meta")
def get_dataset_meta(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin_user),
):
    source = db.query(DataSource).order_by(DataSource.retrieved_at.desc()).first()
    if not source:
        return {"message": "No dataset imported yet"}

    last_run = (
        db.query(ImportRun)
        .filter(ImportRun.data_source_id == source.id)
        .order_by(ImportRun.started_at.desc())
        .first()
    )

    return {
        "source_name": source.name,
        "source_url": source.url,
        "last_import": last_run.started_at if last_run else None,
        "rows_inserted": last_run.rows_inserted if last_run else 0,
        "sha256_hash": last_run.sha256_hash if last_run else None,
    }


@router.get("/imports/quality", response_model=ImportQualityResponse)
def get_import_quality(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin_user),
):
    """Import quality analytics: success/failure breakdown with per-run detail."""
    runs = db.query(ImportRun).order_by(ImportRun.started_at.desc()).limit(limit).all()

    successful = sum(1 for r in runs if r.status == "success")
    failed = sum(1 for r in runs if r.status == "failed")
    durations = [r.duration_ms for r in runs if r.duration_ms is not None]

    last_ok = (
        db.query(ImportRun)
        .filter(ImportRun.status == "success")
        .order_by(ImportRun.started_at.desc())
        .first()
    )

    items = [
        ImportQualityItem(
            id=r.id,
            data_source_id=r.data_source_id,
            status=r.status,
            started_at=r.started_at,
            finished_at=r.finished_at,
            rows_read=r.rows_read,
            rows_inserted=r.rows_inserted,
            rows_updated=r.rows_updated,
            duration_ms=r.duration_ms,
            error_count=len((r.errors_json or {}).get("errors", [])),
            sha256_hash=r.sha256_hash,
            parser_version=r.parser_version,
        )
        for r in runs
    ]

    return ImportQualityResponse(
        total_runs=len(runs),
        successful_runs=successful,
        failed_runs=failed,
        success_rate=(successful / len(runs)) if runs else 0.0,
        last_successful_import=last_ok.started_at if last_ok else None,
        avg_duration_ms=(sum(durations) / len(durations)) if durations else None,
        total_rows_read=sum(r.rows_read for r in runs),
        total_rows_inserted=sum(r.rows_inserted for r in runs),
        total_rows_updated=sum(r.rows_updated for r in runs),
        recent_failures_count=failed,
        runs=items,
    )
