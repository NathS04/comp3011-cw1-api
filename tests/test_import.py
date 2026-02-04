
import pytest
from app.models import Event, DataSource
from datetime import datetime

def test_data_model_constraints(db):
    # Test that we can create an event with provenance
    
    src = DataSource(name="Test Source")
    db.add(src)
    db.commit()
    
    ev = Event(
        title="Prov Event", location="Loc", 
        start_time=datetime.utcnow(), end_time=datetime.utcnow(), 
        capacity=10, 
        source_id=src.id, 
        source_record_id="REC_1",
        is_seeded=True
    )
    db.add(ev)
    db.commit()
    
    assert ev.source_id == src.id
    assert ev.is_seeded is True
