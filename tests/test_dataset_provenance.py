from datetime import datetime, timedelta
import pytest
from app.models import Event, DataSource, ImportRun
from scripts.import_dataset import import_dataset

def test_import_idempotency_and_provenance(db, tmp_path):
    # 1. Setup Mock CSV
    csv_file = tmp_path / "test_import.csv"
    csv_content = """EventId,EventTitle,Description,Venue,StartDate,EndDate,Capacity,Category
TEST_001,Test Event,Desc,Venue A,2026-01-01T10:00:00,2026-01-01T12:00:00,100,Test
TEST_002,Test Event 2,Desc 2,Venue B,2026-01-02T10:00:00,2026-01-02T12:00:00,50,Test
"""
    csv_file.write_text(csv_content, encoding="utf-8")
    
    # 2. Run Import 1 (Pass DB session! New Sig: type, url, db)
    # The URL for CSV is the file path
    import_dataset(source_type="csv", source_url=str(csv_file), db=db)
    
    # Verify Import 1
    events = db.query(Event).filter(Event.source_record_id.like("TEST%")).all()
    assert len(events) == 2
    
    # Check ImportRun
    run = db.query(ImportRun).order_by(ImportRun.id.desc()).first()
    assert run.rows_inserted == 2
    assert run.rows_updated == 0
    assert run.status == "success"
    # Ensure hash is populated for CSV too
    assert run.sha256_hash is not None
    
    # 3. Run Import 2 (Same Data)
    import_dataset(source_type="csv", source_url=str(csv_file), db=db)
    
    # Verify Idempotency
    events_after = db.query(Event).filter(Event.source_record_id.like("TEST%")).all()
    assert len(events_after) == 2 # Count should not increase
    
    run2 = db.query(ImportRun).order_by(ImportRun.id.desc()).first()
    assert run2.id > run.id
    assert run2.rows_inserted == 0
    assert run2.rows_updated == 2 # Should be updates now
    assert run2.status == "success"

def test_analytics_change_after_import(db, client, tmp_path):
    # Baseline: No events
    resp = client.get("/analytics/events/seasonality")
    assert resp.status_code == 200
    assert len(resp.json()['items']) == 0
    
    # Import Data
    csv_file = tmp_path / "analytics_test.csv"
    csv_content = """EventId,EventTitle,Description,Venue,StartDate,EndDate,Capacity,Category
ANA_001,Analytics Event,Desc,Venue X,2026-05-01T10:00:00,2026-05-01T12:00:00,100,Test
"""
    csv_file.write_text(csv_content, encoding="utf-8")
    import_dataset(source_type="csv", source_url=str(csv_file), db=db)
    
    # Verify Analytics Change
    resp_after = client.get("/analytics/events/seasonality")
    assert resp_after.status_code == 200
    items = resp_after.json()['items']
    assert len(items) == 1
    assert items[0]['month'] == '2026-05'
    assert items[0]['count'] == 1

def test_import_xml_logic(db, monkeypatch):
    # Mock requests.get to return XML
    class MockResponse:
        def __init__(self, content, status_code=200):
            self.content = content
            self.status_code = status_code
            
        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP Error")

    xml_content = b"""<?xml version="1.0" standalone="yes"?>
<LA_03_Temporary_Event_Notices>
  <Temporary_Event_Notice>
    <Reference_Number>XML_001</Reference_Number>
    <Premises_x0020_Name>XML Event</Premises_x0020_Name>
    <Activities>Music</Activities>
    <Premises_x0020_Address>Leeds XML Venue</Premises_x0020_Address>
    <Event_x0020_Start_x0020_Date>01/01/2026</Event_x0020_Start_x0020_Date>
    <Event_x0020_End_x0020_Date>01/01/2026</Event_x0020_End_x0020_Date>
    <Start_x0020_Times>10:00</Start_x0020_Times>
    <End_x0020_Times>12:00</End_x0020_Times>
  </Temporary_Event_Notice>
</LA_03_Temporary_Event_Notices>
"""
    def mock_get(*args, **kwargs):
        return MockResponse(xml_content)

    import requests
    monkeypatch.setattr(requests, "get", mock_get)

    # Run Import
    from scripts.import_dataset import import_dataset
    import_dataset(source_type="xml", source_url="http://mock-xml.com", db=db)

    # Verify
    events = db.query(Event).filter(Event.source_record_id == "XML_001").all()
    assert len(events) == 1
    assert events[0].title == "XML Event"
    assert events[0].location == "Leeds XML Venue"
    
    # Verify Provenance
    run = db.query(ImportRun).order_by(ImportRun.id.desc()).first()
    assert run.parser_version == "v2_xml_etree"
    assert run.sha256_hash is not None
    assert run.rows_inserted == 1
