import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))
    yield


def test_get_activities_returns_activity_list():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["max_participants"] == 12
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert app_module.activities[activity_name]["participants"].count(email) == 1


def test_signup_unknown_activity_returns_not_found():
    # Arrange
    activity_name = "Unknown Activity"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/participants?email={quote(email, safe='')}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_not_found():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/participants?email={quote(email, safe='')}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
