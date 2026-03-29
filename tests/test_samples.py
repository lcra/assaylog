from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from app.main import app

client = TestClient(app)

VALID_SAMPLE = {
    "site": "Olympic Dam",
    "hole_id": "OD-DDH-042",
    "depth_m": 142.5,
    "sample_from_m": 140.0,
    "sample_to_m": 142.5,
    "element": "Cu",
    "grade": 2.3,
    "assay_method": "fire_assay",
    "unit": "ppm",
}


def mock_put_sample(site, hole_id, depth_m, sample_from_m, sample_to_m,
                    element, grade, assay_method, unit, batch_id=None,
                    collected_at=None, lab_received_at=None,
                    status="submitted", source_system=None):
    item = {
        "site": site,
        "id": "test-uuid-1234",
        "hole_id": hole_id,
        "depth_m": float(depth_m),
        "sample_from_m": float(sample_from_m),
        "sample_to_m": float(sample_to_m),
        "element": element,
        "grade": float(grade),
        "assay_method": assay_method,
        "unit": unit,
        "status": status,
    }
    if batch_id is not None:
        item["batch_id"] = batch_id
    if collected_at is not None:
        item["collected_at"] = collected_at.isoformat()
    if lab_received_at is not None:
        item["lab_received_at"] = lab_received_at.isoformat()
    if source_system is not None:
        item["source_system"] = source_system
    return item

def mock_get_samples_empty(site):
    return []

def mock_get_samples_with_data(site):
    return [
        {
            "site": site,
            "id": "test-uuid-1234",
            "hole_id": "OD-DDH-042",
            "depth_m": 142.5,
            "sample_from_m": 140.0,
            "sample_to_m": 142.5,
            "element": "Cu",
            "grade": 2.3,
            "assay_method": "fire_assay",
            "unit": "ppm",
            "status": "submitted",
        }
    ]

def mock_get_samples_multiple(site):
    return [
        {"site": site, "id": "id-1", "hole_id": "OD-DDH-042", "depth_m": 100.0,
         "sample_from_m": 98.0, "sample_to_m": 100.0, "element": "Cu", "grade": 2.0,
         "assay_method": "fire_assay", "unit": "ppm", "status": "submitted"},
        {"site": site, "id": "id-2", "hole_id": "OD-DDH-042", "depth_m": 200.0,
         "sample_from_m": 198.0, "sample_to_m": 200.0, "element": "Cu", "grade": 4.0,
         "assay_method": "fire_assay", "unit": "ppm", "status": "submitted"},
        {"site": site, "id": "id-3", "hole_id": "OD-DDH-042", "depth_m": 300.0,
         "sample_from_m": 298.0, "sample_to_m": 300.0, "element": "Cu", "grade": 3.0,
         "assay_method": "fire_assay", "unit": "ppm", "status": "submitted"},
    ]

# Health check
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# POST /samples — happy path
@patch("app.routes.samples.database.put_sample", side_effect=mock_put_sample)
def test_log_sample(mock_put):
    response = client.post("/samples", json=VALID_SAMPLE)
    assert response.status_code == 201
    assert response.json()["message"] == "Sample logged"
    assert response.json()["sample"]["site"] == "Olympic Dam"
    assert response.json()["sample"]["hole_id"] == "OD-DDH-042"
    assert response.json()["sample"]["assay_method"] == "fire_assay"
    assert response.json()["sample"]["status"] == "submitted"

# POST /samples — with optional fields
@patch("app.routes.samples.database.put_sample", side_effect=mock_put_sample)
def test_log_sample_with_optional_fields(mock_put):
    payload = {
        **VALID_SAMPLE,
        "batch_id": "BATCH-001",
        "collected_at": "2025-06-15T10:30:00",
        "lab_received_at": "2025-06-16T08:00:00",
        "status": "completed",
        "source_system": "GeoLog v3",
    }
    response = client.post("/samples", json=payload)
    assert response.status_code == 201
    assert response.json()["sample"]["batch_id"] == "BATCH-001"
    assert response.json()["sample"]["status"] == "completed"
    assert response.json()["sample"]["source_system"] == "GeoLog v3"

# POST /samples — missing field
def test_log_sample_missing_field():
    response = client.post("/samples", json={
        "site": "Olympic Dam",
        "depth_m": 142.5,
        "element": "Cu"
    })
    assert response.status_code == 422

# POST /samples — negative depth
def test_log_sample_negative_depth():
    payload = {**VALID_SAMPLE, "depth_m": -10}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — negative grade
def test_log_sample_negative_grade():
    payload = {**VALID_SAMPLE, "grade": -1.5}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — empty site
def test_log_sample_empty_site():
    payload = {**VALID_SAMPLE, "site": ""}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — empty element
def test_log_sample_empty_element():
    payload = {**VALID_SAMPLE, "element": ""}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — sample_to_m <= sample_from_m
def test_log_sample_invalid_interval():
    payload = {**VALID_SAMPLE, "sample_from_m": 150.0, "sample_to_m": 140.0}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — sample_to_m equals sample_from_m
def test_log_sample_zero_length_interval():
    payload = {**VALID_SAMPLE, "sample_from_m": 140.0, "sample_to_m": 140.0}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — missing hole_id
def test_log_sample_missing_hole_id():
    payload = {k: v for k, v in VALID_SAMPLE.items() if k != "hole_id"}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — missing assay_method
def test_log_sample_missing_assay_method():
    payload = {k: v for k, v in VALID_SAMPLE.items() if k != "assay_method"}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — missing unit
def test_log_sample_missing_unit():
    payload = {k: v for k, v in VALID_SAMPLE.items() if k != "unit"}
    response = client.post("/samples", json=payload)
    assert response.status_code == 422

# POST /samples — database error
@patch("app.routes.samples.database.put_sample",
       side_effect=ClientError({"Error": {"Code": "500", "Message": "fail"}}, "PutItem"))
def test_log_sample_db_error(mock_put):
    response = client.post("/samples", json=VALID_SAMPLE)
    assert response.status_code == 503

# GET /samples/{site} — happy path
@patch("app.routes.samples.database.get_samples_by_site", side_effect=mock_get_samples_with_data)
def test_get_samples(mock_get):
    response = client.get("/samples/Olympic%20Dam")
    assert response.status_code == 200
    assert response.json()["site"] == "Olympic Dam"
    assert len(response.json()["samples"]) == 1
    assert response.json()["samples"][0]["hole_id"] == "OD-DDH-042"

# GET /samples/{site} — site not found
@patch("app.routes.samples.database.get_samples_by_site", side_effect=mock_get_samples_empty)
def test_get_samples_not_found(mock_get):
    response = client.get("/samples/Unknown%20Site")
    assert response.status_code == 404

# GET /samples/{site}/summary — happy path
@patch("app.routes.samples.database.get_samples_by_site", side_effect=mock_get_samples_with_data)
def test_get_summary(mock_get):
    response = client.get("/samples/Olympic%20Dam/summary")
    assert response.status_code == 200
    assert response.json()["sample_count"] == 1
    assert response.json()["average_grade"] == 2.3

# GET /samples/{site}/summary — multiple samples
@patch("app.routes.samples.database.get_samples_by_site", side_effect=mock_get_samples_multiple)
def test_get_summary_multiple_samples(mock_get):
    response = client.get("/samples/Olympic%20Dam/summary")
    assert response.status_code == 200
    assert response.json()["sample_count"] == 3
    assert response.json()["average_grade"] == 3.0

# GET /samples/{site}/summary — site not found
@patch("app.routes.samples.database.get_samples_by_site", side_effect=mock_get_samples_empty)
def test_get_summary_not_found(mock_get):
    response = client.get("/samples/Unknown%20Site/summary")
    assert response.status_code == 404

# --- Idempotency tests ---

IDEMPOTENCY_HEADER = {"Idempotency-Key": "unique-key-abc"}

# POST with idempotency key — first call writes sample
@patch("app.routes.samples.database.store_idempotency_key")
@patch("app.routes.samples.database.check_idempotency_key", return_value=None)
@patch("app.routes.samples.database.put_sample", side_effect=mock_put_sample)
def test_idempotent_first_call(mock_put, mock_check, mock_store):
    response = client.post("/samples", json=VALID_SAMPLE, headers=IDEMPOTENCY_HEADER)
    assert response.status_code == 201
    assert response.json()["message"] == "Sample logged"
    mock_check.assert_called_once_with("unique-key-abc")
    mock_put.assert_called_once()
    mock_store.assert_called_once()

# POST with same idempotency key — returns cached response, no write
@patch("app.routes.samples.database.put_sample", side_effect=mock_put_sample)
@patch("app.routes.samples.database.check_idempotency_key", return_value={
    "message": "Sample logged",
    "sample": {"site": "Olympic Dam", "id": "test-uuid-1234", "hole_id": "OD-DDH-042",
               "depth_m": 142.5, "sample_from_m": 140.0, "sample_to_m": 142.5,
               "element": "Cu", "grade": 2.3, "assay_method": "fire_assay",
               "unit": "ppm", "status": "submitted"},
})
def test_idempotent_duplicate_key(mock_check, mock_put):
    response = client.post("/samples", json=VALID_SAMPLE, headers=IDEMPOTENCY_HEADER)
    assert response.status_code == 201
    assert response.json()["message"] == "Sample logged"
    mock_check.assert_called_once_with("unique-key-abc")
    mock_put.assert_not_called()

# POST without idempotency key — no idempotency check
@patch("app.routes.samples.database.check_idempotency_key")
@patch("app.routes.samples.database.put_sample", side_effect=mock_put_sample)
def test_no_idempotency_header(mock_put, mock_check):
    response = client.post("/samples", json=VALID_SAMPLE)
    assert response.status_code == 201
    mock_check.assert_not_called()
    mock_put.assert_called_once()

# POST with idempotency key — idempotency DB fails on check
@patch("app.routes.samples.database.check_idempotency_key",
       side_effect=ClientError({"Error": {"Code": "500", "Message": "fail"}}, "GetItem"))
def test_idempotent_check_db_error(mock_check):
    response = client.post("/samples", json=VALID_SAMPLE, headers=IDEMPOTENCY_HEADER)
    assert response.status_code == 503
