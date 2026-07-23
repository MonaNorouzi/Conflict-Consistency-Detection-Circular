import json

from fastapi.testclient import TestClient

from backend.api.routes import db_clauses
from backend.main import app


client = TestClient(app)


def setup_function():
    db_clauses.clear()


def circular_payload(circular_id: str, issuer: str, issue_date: str, content: str):
    return {
        "circular_id": circular_id,
        "title": "تست بخشنامه",
        "doc_type": "داخلی",
        "issuer": issuer,
        "issue_date": issue_date,
        "clauses": [{"clause_number": 1, "content": content}],
    }


def test_health_endpoint_returns_running_message():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"].startswith("Circular Conflict")


def test_upload_json_detects_conflict_and_periodic_audit_counts_circulars():
    first = circular_payload("C-001", "اعتبارات", "1401/01/01", "سقف ۵۰ میلیون")
    second = circular_payload("C-002", "اعتبارات", "1402/01/01", "سقف ۸۰ میلیون")

    first_response = client.post(
        "/api/v1/circulars/upload-json",
        files={"file": ("first.json", json.dumps(first), "application/json")},
    )
    second_response = client.post(
        "/api/v1/circulars/upload-json",
        files={"file": ("second.json", json.dumps(second), "application/json")},
    )

    assert first_response.status_code == 200
    assert first_response.json() == []
    assert second_response.status_code == 200
    assert second_response.json()[0]["winning_clause"] == "C-002 (بند 1)"

    audit_response = client.get("/api/v1/circulars/periodic-audit")

    assert audit_response.status_code == 200
    assert audit_response.json()["total_circulars_checked"] == 2
    assert audit_response.json()["total_conflicts_found"] == 1


def test_upload_json_rejects_non_json_files():
    response = client.post(
        "/api/v1/circulars/upload-json",
        files={"file": ("circular.txt", "{}", "text/plain")},
    )

    assert response.status_code == 400