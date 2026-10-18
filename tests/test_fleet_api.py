"""Tests for fleet_api: robots, telemetry and fault injection."""

import sqlite3

READING = {"robot_id": 2, "x": 3, "y": 4, "battery": 87.5, "status": "moving"}


def test_health(fleet_client):
    assert fleet_client.get("/health").json() == {"status": "ok", "service": "fleet_api"}


def test_seeded_fleet_has_three_robots(fleet_client):
    robots = fleet_client.get("/robots").json()
    assert [(r["id"], r["model"], r["firmware"]) for r in robots] == [
        (1, "AMR-100", "1.4"),
        (2, "AMR-100", "1.4"),
        (3, "AMR-200", "2.0"),
    ]


def test_unknown_robot_returns_404(fleet_client):
    assert fleet_client.get("/robots/99").status_code == 404
    assert fleet_client.get("/robots/99/telemetry").status_code == 404
    assert fleet_client.post("/telemetry", json={**READING, "robot_id": 99}).status_code == 404
    inject = {"robot_id": 99, "fault": "wheel_stall"}
    assert fleet_client.post("/faults/inject", json=inject).status_code == 404


def test_posted_reading_appears_in_telemetry(fleet_client):
    assert fleet_client.post("/telemetry", json={**READING, "error_code": "E42"}).status_code == 201

    readings = fleet_client.get("/robots/2/telemetry").json()
    assert len(readings) == 1
    assert readings[0]["battery"] == 87.5
    assert readings[0]["error_code"] == "E42"
    # The robot's current status follows its latest reading.
    assert fleet_client.get("/robots/2").json()["status"] == "moving"
    # Readings are per robot.
    assert fleet_client.get("/robots/1/telemetry").json() == []


def test_telemetry_is_newest_first_and_respects_limit(fleet_client):
    for battery in (90, 80, 70):
        fleet_client.post("/telemetry", json={**READING, "battery": battery})

    readings = fleet_client.get("/robots/2/telemetry", params={"limit": 2}).json()
    assert [r["battery"] for r in readings] == [70, 80]


def test_invalid_reading_is_rejected(fleet_client):
    assert fleet_client.post("/telemetry", json={**READING, "battery": 150}).status_code == 422
    assert fleet_client.post("/telemetry", json={**READING, "status": "flying"}).status_code == 422


def test_fault_injection_writes_fault_log_row(fleet_client):
    response = fleet_client.post("/faults/inject", json={"robot_id": 2, "fault": "wheel_stall"})
    assert response.status_code == 201
    assert response.json()["true_cause"] == "wheel motor stalled"

    # fault_log has no read endpoint by design, so check the database directly.
    conn = sqlite3.connect(fleet_client.app.state.db_path)
    rows = conn.execute("SELECT robot_id, fault, true_cause FROM fault_log").fetchall()
    conn.close()
    assert rows == [(2, "wheel_stall", "wheel motor stalled")]


def test_unknown_fault_is_rejected(fleet_client):
    response = fleet_client.post("/faults/inject", json={"robot_id": 1, "fault": "gremlins"})
    assert response.status_code == 422


def test_localization_drift_only_on_firmware_2(fleet_client):
    drift = {"fault": "localization_drift"}
    assert fleet_client.post("/faults/inject", json={**drift, "robot_id": 1}).status_code == 422
    assert fleet_client.post("/faults/inject", json={**drift, "robot_id": 3}).status_code == 201
