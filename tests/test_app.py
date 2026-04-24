from urllib.parse import quote

import src.app as app_module


def activity_url(activity_name: str, suffix: str = "") -> str:
    return f"/activities/{quote(activity_name, safe='')}{suffix}"


def test_get_activities_returns_all_activities_with_no_store_header(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert expected_activity in response.json()
    assert response.json()[expected_activity]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_a_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "new.student@mergington.edu"

    # Act
    response = client.post(
        activity_url(activity_name, "/signup"),
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {new_email} for {activity_name}"
    }
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        activity_url(activity_name, "/signup"),
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert app_module.activities[activity_name]["participants"].count(existing_email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    missing_activity = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        activity_url(missing_activity, "/signup"),
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_existing_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"

    # Act
    response = client.delete(
        activity_url(activity_name, "/participants"),
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}"
    }
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    missing_activity = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        activity_url(missing_activity, "/participants"),
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_missing_participant(client):
    # Arrange
    activity_name = "Art Studio"
    missing_email = "student@mergington.edu"

    # Act
    response = client.delete(
        activity_url(activity_name, "/participants"),
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Participant not found for this activity"
    }