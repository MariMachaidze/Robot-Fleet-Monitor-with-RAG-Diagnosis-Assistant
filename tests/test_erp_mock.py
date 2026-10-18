"""Tests for erp_mock: spare-part search and the draft-only notification workflow."""

NOTIFICATION = {
    "robot_id": 2,
    "title": "Wheel stall on robot 2",
    "description": "E42 reported; wheel motor replacement likely.",
    "priority": "high",
}


def find(parts: list[dict], description: str, model: str) -> dict:
    """Return the one seeded part with this description for this robot model."""
    return next(
        p for p in parts if p["description"] == description and p["compatible_model"] == model
    )


def test_health(erp_client):
    assert erp_client.get("/health").json() == {"status": "ok", "service": "erp_mock"}


def test_seed_contains_parts_needed_by_the_scenarios(erp_client):
    parts = erp_client.get("/spare-parts").json()
    assert len(parts) >= 12

    amr100_motor = find(parts, "Wheel motor assembly", "AMR-100")
    assert (amr100_motor["stock"], amr100_motor["lead_time_days"]) == (0, 14)
    assert find(parts, "Wheel motor assembly", "AMR-200")["stock"] == 3
    assert find(parts, "Lidar cable harness", "AMR-100")["stock"] > 0
    assert find(parts, "Lidar cable harness", "AMR-200")["stock"] > 0
    assert find(parts, "Battery pack 48V Li-ion", "AMR-100")["stock"] == 1


def test_spare_part_search_filters_by_model(erp_client):
    parts = erp_client.get("/spare-parts", params={"compatible_model": "AMR-200"}).json()
    assert parts
    assert {p["compatible_model"] for p in parts} == {"AMR-200"}
    # The model filter ignores case, and an empty value means "no filter".
    lower = erp_client.get("/spare-parts", params={"compatible_model": "amr-200"}).json()
    assert lower == parts
    everything = erp_client.get("/spare-parts", params={"compatible_model": "", "q": ""}).json()
    assert len(everything) > len(parts)


def test_spare_part_text_search(erp_client):
    params = {"q": "WHEEL motor", "compatible_model": "AMR-100"}
    parts = erp_client.get("/spare-parts", params=params).json()
    assert [p["part_id"] for p in parts] == ["SP-1001"]


def test_notification_is_always_created_as_draft(erp_client):
    # A client trying to skip the human approval step still gets a draft.
    sneaky = {**NOTIFICATION, "status": "approved"}
    response = erp_client.post("/maintenance-notifications", json=sneaky)
    assert response.status_code == 201
    assert response.json()["status"] == "draft"
    assert erp_client.get("/maintenance-notifications").json()[0]["status"] == "draft"


def test_notification_cannot_be_approved_twice(erp_client):
    notification_id = erp_client.post("/maintenance-notifications", json=NOTIFICATION).json()["id"]

    first = erp_client.post(f"/maintenance-notifications/{notification_id}/approve")
    assert first.status_code == 200
    assert first.json()["status"] == "approved"

    second = erp_client.post(f"/maintenance-notifications/{notification_id}/approve")
    assert second.status_code == 409


def test_approving_unknown_notification_returns_404(erp_client):
    assert erp_client.post("/maintenance-notifications/999/approve").status_code == 404
