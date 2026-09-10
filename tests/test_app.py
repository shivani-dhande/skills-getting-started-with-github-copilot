from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seeded_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["max_participants"] == 12
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_registers_participant_for_activity(client):
    email = "new.student+test@example.com"

    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Programming Class"
    }
    assert email in client.get("/activities").json()["Programming Class"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "michael@mergington.edu"

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email(client):
    response = client.post("/activities/Chess%20Club/signup")

    assert response.status_code == 422


def test_delete_removes_url_encoded_participant(client):
    email = "student+club@example.com"
    client.post("/activities/Art%20Club/signup", params={"email": email})

    response = client.delete(
        f"/activities/Art%20Club/participants/{quote(email, safe='')}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Art Club"}
    assert email not in client.get("/activities").json()["Art Club"]["participants"]


def test_delete_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/participants/student%40example.com"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_returns_not_found_for_missing_participant(client):
    response = client.delete(
        "/activities/Art%20Club/participants/missing%40example.com"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
