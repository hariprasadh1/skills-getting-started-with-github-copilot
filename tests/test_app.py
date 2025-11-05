import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code in [200, 307]  # Both are valid depending on how static files are served
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_for_activity_success():
    response = client.post("/activities/Basketball Team/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully signed up for Basketball Team"
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Basketball Team"]["participants"]

def test_signup_for_activity_already_registered():
    # First signup
    client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    
    # Try to signup again
    response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_signup_for_activity_full():
    # Fill up the Chess Club
    activity = "Chess Club"
    activities = client.get("/activities").json()
    max_participants = activities[activity]["max_participants"]
    current_participants = activities[activity]["participants"]
    
    # Add participants until full
    for i in range(len(current_participants), max_participants):
        email = f"test{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={email}")
    
    # Try to add one more participant
    response = client.post(f"/activities/{activity}/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()

def test_signup_for_nonexistent_activity():
    response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity_success():
    # First sign up
    activity = "Art Studio"
    email = "unregister@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Then unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]

def test_unregister_from_activity_not_registered():
    response = client.post("/activities/Drama Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_from_nonexistent_activity():
    response = client.post("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()