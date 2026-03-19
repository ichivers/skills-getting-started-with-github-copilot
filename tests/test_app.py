from src.app import activities


def test_root_redirects_to_static_index(client):
    expected_location = "/static/index.html"

    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data(client):
    expected_activity = "Chess Club"

    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert expected_activity in payload
    assert "participants" in payload[expected_activity]


def test_signup_adds_new_participant(client):
    activity_name = "Chess Club"
    new_email = "new.student@mergington.edu"
    participants_before = len(activities[activity_name]["participants"])

    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == participants_before + 1


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]

    response = client.post(f"/activities/{activity_name}/signup", params={"email": duplicate_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity(client):
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    activity_name = "Programming Class"
    existing_email = activities[activity_name]["participants"][0]
    participants_before = len(activities[activity_name]["participants"])

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": existing_email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {existing_email} from {activity_name}"
    assert existing_email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == participants_before - 1


def test_unregister_returns_404_when_participant_missing(client):
    activity_name = "Programming Class"
    missing_email = "not.enrolled@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unregister_returns_404_for_unknown_activity(client):
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"