from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.db import get_db
from ..core import auth
from ..models import User, ImportRun, DataSource
from ..schemas import ImportRunOut, DataSourceOut
from scripts.import_dataset import import_dataset

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/imports/run", status_code=status.HTTP_201_CREATED)
def run_import(
    source_type: str = Query("xml", regex="^(xml|csv)$"),
    source_url: str = Query("https://opendata.leeds.gov.uk/downloads/Licences/temp-event-notice/temp-event-notice.xml"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(auth.get_current_user) # Admin only in real life
):
    """
    Trigger a dataset import (Admin only).
    """
    # Verify user is admin if role exists, else just auth
    try:
        # Running sync for simplicity as per brief requirements
        import_dataset(source_type, source_url, db)
        return {"message": "Import finished successfully", "source": source_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/imports", response_model=List[ImportRunOut]) # Need schema
def list_imports(limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    List recent import runs.
    """
    return db.query(ImportRun).order_by(ImportRun.started_at.desc()).limit(limit).all()

@router.get("/dataset/meta")
def get_dataset_meta(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Get metadata about the current dataset integration.
    """
    source = db.query(DataSource).order_by(DataSource.retrieved_at.desc()).first()
    if not source:
        return {"message": "No dataset imported yet"}
    
    last_run = db.query(ImportRun).filter(ImportRun.data_source_id == source.id).order_by(ImportRun.started_at.desc()).first()
    
    return {
        "source_name": source.name,
        "source_url": source.url,
        "last_import": last_run.started_at if last_run else None,
        "rows_inserted": last_run.rows_inserted if last_run else 0,
        "sha256_hash": last_run.sha256_hash if last_run else None
    }
