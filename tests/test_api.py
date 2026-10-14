from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app import models  # noqa: F401
from main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def student_payload():
    return {
        "name": "Rahul Sharma",
        "date_of_birth": "2005-08-17",
        "email": "rahul@example.com",
        "phone": "+919876543210",
        "course": "B.Tech CSE",
        "address": "Ferozepur, Punjab",
        "enrollment_date": "2026-08-01",
    }


def create_one(client, student_payload):
    response = client.post("/students", json=student_payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_root_and_health(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json()["status"] == "ok"


def test_create_and_read_student(client, student_payload):
    student = create_one(client, student_payload)
    assert student["id"] == 1
    assert student["name"] == "Rahul Sharma"
    response = client.get(f"/students/{student['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "rahul@example.com"


def test_list_and_filter_students(client, student_payload):
    create_one(client, student_payload)
    response = client.get("/students?name=rahul&course=CSE&date_of_birth_after=2005-01-01")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert client.get("/students?name=unknown").json() == []


def test_patch_student(client, student_payload):
    student = create_one(client, student_payload)
    response = client.patch(f"/students/{student['id']}", json={"course": "AI and ML"})
    assert response.status_code == 200
    assert response.json()["course"] == "AI and ML"
    assert response.json()["email"] == "rahul@example.com"


def test_put_student(client, student_payload):
    student = create_one(client, student_payload)
    replacement = {**student_payload, "name": "Rahul S.", "email": "rahul.new@example.com"}
    response = client.put(f"/students/{student['id']}", json=replacement)
    assert response.status_code == 200
    assert response.json()["name"] == "Rahul S."


def test_delete_student_and_missing_record(client, student_payload):
    student = create_one(client, student_payload)
    assert client.delete(f"/students/{student['id']}").status_code == 204
    assert client.get(f"/students/{student['id']}").status_code == 404
    assert client.delete(f"/students/{student['id']}").status_code == 404


def test_validation_requires_contact_and_valid_email(client, student_payload):
    no_contact = {**student_payload, "email": None, "phone": None}
    assert client.post("/students", json=no_contact).status_code == 422
    invalid_email = {**student_payload, "email": "not-an-email"}
    assert client.post("/students", json=invalid_email).status_code == 422


def test_duplicate_email_conflict(client, student_payload):
    create_one(client, student_payload)
    duplicate = {**student_payload, "name": "Another Student", "phone": "+919000000000"}
    assert client.post("/students", json=duplicate).status_code == 409


def test_missing_update_and_empty_patch(client):
    assert client.patch("/students/999", json={"course": "CSE"}).status_code == 404
    assert client.patch("/students/999", json={}).status_code == 404


def test_patch_cannot_remove_last_contact(client, student_payload):
    student_payload["phone"] = None
    student = create_one(client, student_payload)
    response = client.patch(f"/students/{student['id']}", json={"email": None})
    assert response.status_code == 422


def test_ai_count_and_birth_filter(client, student_payload):
    client.post("/students", json=student_payload)
    result = client.post("/ai/ask", json={"question": "How many students are there?"})
    assert result.status_code == 200
    assert result.json()["facts"]["total_students"] == 1
    result = client.post("/ai/ask", json={"question": "List students born after 2005"})
    assert result.status_code == 200
    assert result.json()["facts"]["result_count"] == 0


def test_ai_unsupported_question_does_not_query_arbitrary_sql(client):
    result = client.post("/ai/ask", json={"question": "drop table students"})
    assert result.status_code == 200
    assert result.json()["intent"] == "unsupported"


def test_analytics_and_workflow_events(client, student_payload):
    created = client.post("/students", json=student_payload)
    assert created.status_code == 201
    summary = client.get("/analytics/summary")
    assert summary.status_code == 200
    assert summary.json()["total_students"] == 1
    events = client.get("/workflow/events")
    assert events.status_code == 200
    assert any(item["event_type"] == "student.created" for item in events.json())


def test_patch_creates_workflow_event(client, student_payload):
    student = client.post("/students", json=student_payload).json()
    response = client.patch(f"/students/{student['id']}", json={"course": "AI and ML"})
    assert response.status_code == 200
    events = client.get("/workflow/events").json()
    assert any(item["event_type"] == "student.updated" for item in events)
