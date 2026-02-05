# Dataset Source Documentation: Leeds City Council

**Dataset Name:** Temporary Event Notices  
**Source URL:** [https://opendata.leeds.gov.uk/downloads/Licences/temp-event-notice/temp-event-notice.xml](https://opendata.leeds.gov.uk/downloads/Licences/temp-event-notice/temp-event-notice.xml)  
**Publisher:** Leeds City Council (via Data Mill North / data.gov.uk)  
**License:** Open Government Licence (OGL) v3.0  
**Retrieval Date:** 4th February 2026  

---

## 1. Description
This dataset lists Temporary Event Notices (TENs) granted by Leeds City Council. It provides real-world data about event permissions, including locations, dates, and times, which is perfect for an "Event Management" API simulation.

**Why this dataset?**
- **Real & Verifiable:** It is a live dataset updated by the council.
- **XML Format:** Demonstrates parsing capability beyond simple CSVs (Novel Data Integration).
- **Domain Relevant:** Directly maps to "Events", "Locations", and "Start/End Times".

## 2. Parsing & Ingestion Strategy

The ingestion pipeline (`scripts/import_dataset.py`) supports both legacy CSV and the new XML format.

**XML Provenance Logging:**
Each import run logs:
- `source_url`: The remote URL.
- `sha256_hash`: Hash of the raw XML content (for integrity verification).
- `parser_version`: `v2_xml_etree` (tracks logic versioning).
- `duration_ms`: Time taken to fetch and parse.

**Field Mapping:**

| XML Tag | API Model Field | Logic |
|---------|-----------------|-------|
| `Reference_Number` | `source_record_id` | Unique ID (e.g., TEN/03010/24/01) |
| `Premises_Name` | `title` | Truncated to 200 chars |
| `Activities` | `description` | Truncated to 1000 chars |
| `Event_Start_Date` + `Start_Times` | `start_time` | Parsed into UTC datetime |
| `Event_End_Date` + `End_Times` | `end_time` | Parsed into UTC datetime |

## 3. Data Integrity
- **Idempotency:** Uses `Reference_Number` to prevent duplicates. Re-running the import updates existing records if changed.
- **Validation:** Skips records with missing IDs or titles.

---
*Documentation required for Novel Data Integration component*
