"""Tests for the simulator: the telemetry signature of each fault, and the full loop
running against fleet_api (through the TestClient, so no server is needed)."""

import random
import sqlite3

import pytest

from fleet_api.faults import FAULTS
from simulator.behaviors import FAULT_BEHAVIORS, RobotState, start_fault, tick
from simulator.sim import SimulatorError, parse_args, run


def robot(**overrides) -> RobotState:
    defaults = {"id": 1, "x": 2, "y": 2, "battery": 80.0, "goal": (6, 2)}
    return RobotState(**{**defaults, **overrides})


def run_ticks(r: RobotState, n: int, fault: str | None = None) -> list[list[dict]]:
    """Run n ticks for one robot; returns the readings posted on each tick."""
    rng = random.Random(0)
    if fault:
        start_fault(r, fault)
    return [tick([r], rng) for _ in range(n)]


def position(reading: dict) -> tuple[int, int]:
    return reading["x"], reading["y"]


def cells_apart(a: dict, b: dict) -> int:
    return max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))


# ---------- Behaviors (pure, no network) ----------


def test_every_cataloged_fault_has_a_behavior():
    assert set(FAULT_BEHAVIORS) == set(FAULTS)


def test_healthy_robot_moves_one_cell_and_drains_battery():
    [[reading]] = run_ticks(robot(), 1)
    assert position(reading) == (3, 2)
    assert reading["battery"] == 79.5
    assert (reading["status"], reading["error_code"]) == ("moving", None)


def test_healthy_robot_charges_when_battery_is_low():
    readings = [r for [r] in run_ticks(robot(battery=20.2), 2)]
    assert [r["status"] for r in readings] == ["charging", "charging"]
    assert [r["battery"] for r in readings] == [19.7, 24.7]


def test_wheel_stall_freezes_position_and_drains_battery_3x():
    readings = [r for [r] in run_ticks(robot(), 3, "wheel_stall")]
    assert {position(r) for r in readings} == {(2, 2)}
    assert [r["battery"] for r in readings] == [78.5, 77.0, 75.5]
    assert {(r["status"], r["error_code"]) for r in readings} == {("stopped", "E42")}


def test_blocked_path_reports_e21_after_5_unchanged_ticks():
    readings = [r for [r] in run_ticks(robot(), 6, "blocked_path")]
    assert {position(r) for r in readings} == {(2, 2)}
    assert [(r["status"], r["error_code"]) for r in readings] == [("moving", None)] * 4 + [
        ("stopped", "E21")
    ] * 2


def test_lidar_dropout_reports_error_and_jumping_position():
    start = {"x": 2, "y": 2}
    readings = [r for [r] in run_ticks(robot(), 3, "lidar_dropout")]
    assert {(r["status"], r["error_code"]) for r in readings} == {("error", "E33")}
    for before, after in zip([start, *readings], readings, strict=False):
        assert 2 <= cells_apart(before, after) <= 3


def test_localization_drift_jumps_more_than_3_cells():
    readings = [r for [r] in run_ticks(robot(), 3, "localization_drift")]
    assert cells_apart({"x": 2, "y": 2}, readings[0]) > 3
    assert {r["error_code"] for r in readings} == {"E57"}


def test_battery_drain_stops_robot_below_10_percent():
    readings = [r for [r] in run_ticks(robot(battery=50.0), 8, "battery_drain")]
    assert readings[0]["error_code"] is None  # still driving at first
    last = readings[-1]
    assert last["battery"] < 10
    assert (last["status"], last["error_code"]) == ("stopped", "E10")


def test_comms_loss_goes_silent_for_10_ticks_then_reports_e60():
    per_tick = run_ticks(robot(x=5), 13, "comms_loss")
    # 2 ticks driving into aisle 7, 10 silent ticks, then the robot reconnects.
    assert [len(readings) for readings in per_tick] == [1, 1] + [0] * 10 + [1]
    [last] = per_tick[-1]
    assert last["x"] == 7
    assert (last["status"], last["error_code"]) == ("stopped", "E60")


# ---------- Full loop against fleet_api ----------


def test_injected_fault_changes_status_and_writes_fault_log(fleet_client):
    run(fleet_client, fault="wheel_stall", robot_id=2, after=2, ticks=5, interval=0, seed=1)

    assert fleet_client.get("/robots/2").json()["status"] == "stopped"
    readings = fleet_client.get("/robots/2/telemetry").json()  # newest first
    assert [r["error_code"] for r in readings] == ["E42"] * 3 + [None] * 2
    # The other robots are unaffected.
    for other in (1, 3):
        codes = {r["error_code"] for r in fleet_client.get(f"/robots/{other}/telemetry").json()}
        assert codes == {None}

    conn = sqlite3.connect(fleet_client.app.state.db_path)
    rows = conn.execute("SELECT robot_id, fault, true_cause FROM fault_log").fetchall()
    conn.close()
    assert rows == [(2, "wheel_stall", "wheel motor stalled")]


def test_simulator_rejects_invalid_injection(fleet_client):
    with pytest.raises(SimulatorError, match="firmware 2.0"):
        run(fleet_client, fault="localization_drift", robot_id=1, ticks=1, interval=0)
    with pytest.raises(SimulatorError, match="does not exist"):
        run(fleet_client, fault="wheel_stall", robot_id=7, ticks=1, interval=0)


def test_restart_resumes_from_last_reading(fleet_client):
    before = run(fleet_client, ticks=3, interval=0, seed=1)
    after = run(fleet_client, ticks=0, interval=0, seed=2)  # ticks=0: only load the state
    assert [(r.x, r.y, r.battery) for r in after] == [(r.x, r.y, r.battery) for r in before]


def test_cli_requires_inject_and_robot_together():
    with pytest.raises(SystemExit):
        parse_args(["--inject", "wheel_stall"])
    with pytest.raises(SystemExit):
        parse_args(["--robot", "2"])
    args = parse_args(["--inject", "wheel_stall", "--robot", "2"])
    assert (args.inject, args.robot, args.after, args.interval) == ("wheel_stall", 2, 3, 2.0)
