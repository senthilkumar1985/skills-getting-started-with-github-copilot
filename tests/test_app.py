import pytest
from fastapi.testclient import TestClient
from src import app

@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    # Arrange: Reset the activities state before each test
    from src.app import activities as real_activities
    original = {k: v.copy() for k, v in real_activities.items()}
    for k, v in real_activities.items():
        v["participants"] = original[k]["participants"][:]
    yield
    # No teardown needed for in-memory

def test_get_activities():
    # Arrange
    client = TestClient(app)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()

def test_signup_success():
    # Arrange
    client = TestClient(app)
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    # Confirm participant added
    get_resp = client.get("/activities")
    assert email in get_resp.json()[activity]["participants"]

def test_signup_duplicate():
    # Arrange
    client = TestClient(app)
    email = "michael@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_success():
    # Arrange
    client = TestClient(app)
    email = "daniel@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    # Confirm participant removed
    get_resp = client.get("/activities")
    assert email not in get_resp.json()[activity]["participants"]

def test_unregister_not_registered():
    # Arrange
    client = TestClient(app)
    email = "notregistered@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]
