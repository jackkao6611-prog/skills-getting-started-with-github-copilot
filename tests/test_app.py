from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def get_activity_details(activity_name):
    activities = client.get("/activities").json()
    return activities.get(activity_name, {})


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)
    assert "participants" in data["Chess Club"]


def test_signup_adds_new_participant():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activity = get_activity_details(activity_name)
    assert email in activity["participants"]


def test_duplicate_signup_returns_400():
    email = "emma@mergington.edu"
    activity_name = "Programming Class"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_delete_participant_removes_from_activity():
    email = "daniel@mergington.edu"
    activity_name = "Chess Club"

    response = client.delete(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    activity = get_activity_details(activity_name)
    assert email not in activity["participants"]


def test_delete_nonexistent_participant_returns_404():
    email = "missing@mergington.edu"
    activity_name = "Chess Club"

    response = client.delete(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
