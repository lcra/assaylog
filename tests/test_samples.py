from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from app.main import app

client = TestClient(app)


def mock_put_sample(site, depth_m, element, grade):
    return {
        "site": site,
        "id": "test-uuid-1234",
        "depth_m": float(depth_m),
        "element": element,
        "grade": float(grade),
    }

def mock_get_samples_empty(site):
    return []

def mock_get_samples_with_data(site):
    return [
        {
            "site": site,
            "id": "test-uuid-1234",
            "depth_m": 142.5,
            "element": "Cu",
            "grade": 2.3,
        }
    ]

def mock_get_samples_multiple(site):
    return [
        {"site": site, "id": "id-1", "depth_m": 100.0, "element": "Cu", "grade": 2.0},
        {"site": site, "id": "id-2", "depth_m": 200.0, "element": "Cu", "grade": 4.0},
        {"site": site, "id": "id-3", "depth_m": 300.0, "element": "Cu", "grade": 3.0},
    ]

# Health check
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# POST /samples — happy path
@patch("app.routes.samples.database.put_sample", side_effect=mock_put_sample)
def test_log_sample(mock_put):
    response = client.post("/samples", json={
        "site": "Olympic Dam",
        "depth_m": 142.5,
        "element": "Cu",
        "grade": 2.3
    })
    assert response.status_code == 201
    assert response.json()["message"] == "Sample logged"
    assert response.json()["sample"]["site"] == "Olympic Dam"

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
    response = client.post("/samples", json={
        "site": "Olympic Dam", "depth_m": -10, "element": "Cu", "grade": 2.3
    })
    assert response.status_code == 422

# POST /samples — negative grade
def test_log_sample_negative_grade():
    response = client.post("/samples", json={
        "site": "Olympic Dam", "depth_m": 100, "element": "Cu", "grade": -1.5
    })
    assert response.status_code == 422

# POST /samples — empty site
def test_log_sample_empty_site():
    response = client.post("/samples", json={
        "site": "", "depth_m": 100, "element": "Cu", "grade": 2.3
    })
    assert response.status_code == 422

# POST /samples — empty element
def test_log_sample_empty_element():
    response = client.post("/samples", json={
        "site": "Olympic Dam", "depth_m": 100, "element": "", "grade": 2.3
    })
    assert response.status_code == 422

# POST /samples — database error
@patch("app.routes.samples.database.put_sample",
       side_effect=ClientError({"Error": {"Code": "500", "Message": "fail"}}, "PutItem"))
def test_log_sample_db_error(mock_put):
    response = client.post("/samples", json={
        "site": "Olympic Dam", "depth_m": 142.5, "element": "Cu", "grade": 2.3
    })
    assert response.status_code == 503

# GET /samples/{site} — happy path
@patch("app.routes.samples.database.get_samples_by_site", side_effect=mock_get_samples_with_data)
def test_get_samples(mock_get):
    response = client.get("/samples/Olympic%20Dam")
    assert response.status_code == 200
    assert response.json()["site"] == "Olympic Dam"
    assert len(response.json()["samples"]) == 1

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
