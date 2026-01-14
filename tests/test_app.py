from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "pytest-test@example.com"
    # preserve original participants to avoid side effects
    original = activities[activity]["participants"][:]

    # ensure test email not present initially
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    try:
        # signup
        res = client.post(f"/activities/{quote(activity)}/signup?email={email}")
        assert res.status_code == 200
        assert email in activities[activity]["participants"]

        # duplicate signup should fail with 400
        res_dup = client.post(f"/activities/{quote(activity)}/signup?email={email}")
        assert res_dup.status_code == 400

        # unregister
        res_un = client.post(f"/activities/{quote(activity)}/unregister?email={email}")
        assert res_un.status_code == 200
        assert email not in activities[activity]["participants"]

        # unregistering again should return 404
        res_un2 = client.post(f"/activities/{quote(activity)}/unregister?email={email}")
        assert res_un2.status_code == 404

    finally:
        # restore original participants list
        activities[activity]["participants"] = original
