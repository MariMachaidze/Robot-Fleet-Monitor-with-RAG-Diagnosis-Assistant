"""Robot fleet simulator: runs the 3 robots and posts their telemetry to fleet_api.

Usage:
    python -m simulator.sim                                  # healthy fleet, runs forever
    python -m simulator.sim --inject wheel_stall --robot 2   # robot 2 stalls after 3 ticks
    python -m simulator.sim --ticks 20 --interval 0          # fast, finite run

The robots are loaded from fleet_api (GET /robots), so nothing about the fleet is
hard-coded here. The movement and fault rules live in simulator/behaviors.py.
"""

import argparse
import logging
import os
import random
import sys
import time

import httpx

from fleet_api.faults import FAULTS
from simulator.behaviors import RobotState, new_robot, start_fault, tick

log = logging.getLogger("simulator")


class SimulatorError(Exception):
    """A problem with the requested run, reported to the user without a traceback."""


# ---------- fleet_api calls ----------


def load_fleet(client: httpx.Client, attempts: int = 30) -> list[dict]:
    """GET /robots, retrying while fleet_api is still starting (e.g. in docker compose).

    Only connection problems are retried. An HTTP error such as 500 means the server is
    up but broken, and waiting will not fix it, so it is raised at once.
    """
    for attempt in range(1, attempts + 1):
        try:
            response = client.get("/robots")
        except httpx.TransportError as exc:
            if attempt == attempts:
                raise
            log.warning("fleet_api not reachable yet (%s), retrying", exc)
            time.sleep(1)
            continue
        response.raise_for_status()
        return response.json()
    return []  # unreachable; keeps type checkers happy


def last_reading(client: httpx.Client, robot_id: int) -> dict | None:
    readings = client.get(f"/robots/{robot_id}/telemetry", params={"limit": 1}).json()
    return readings[0] if readings else None


def post_reading(client: httpx.Client, reading: dict) -> None:
    """Post one reading. A failed post is logged and skipped, so the simulation keeps going."""
    try:
        client.post("/telemetry", json=reading).raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("could not post reading for robot %s: %s", reading["robot_id"], exc)


def inject(client: httpx.Client, robot: RobotState, fault: str) -> None:
    """Write the fault and its true cause to fault_log, then switch the robot's behavior."""
    client.post("/faults/inject", json={"robot_id": robot.id, "fault": fault}).raise_for_status()
    start_fault(robot, fault)


# ---------- Simulation loop ----------


def check_injection(fleet: list[dict], fault: str, robot_id: int) -> None:
    """Fail fast with a clear message instead of discovering a bad request mid-run."""
    robot = next((r for r in fleet if r["id"] == robot_id), None)
    if robot is None:
        known = ", ".join(str(r["id"]) for r in fleet)
        raise SimulatorError(f"robot {robot_id} does not exist (fleet: {known})")
    only = FAULTS[fault].firmware_only
    if only and robot["firmware"] != only:
        raise SimulatorError(
            f"{fault} only occurs on firmware {only}; robot {robot_id} runs {robot['firmware']}"
        )


def describe(r: RobotState) -> str:
    code = f" {r.error_code}" if r.error_code else ""
    signal = " [no signal]" if r.silent else ""
    return f"R{r.id} ({r.x},{r.y}) {r.battery:5.1f}% {r.status}{code}{signal}"


def run(
    client: httpx.Client,
    fault: str | None = None,
    robot_id: int | None = None,
    after: int = 3,
    ticks: int | None = None,
    interval: float = 2.0,
    seed: int | None = None,
) -> list[RobotState]:
    """Run the simulation. The fault (if any) starts after `after` healthy ticks.

    `client` is any client with httpx's get/post interface; tests pass FastAPI's TestClient.
    Returns the final robot states (useful in tests).
    """
    rng = random.Random(seed)
    fleet = load_fleet(client)
    if fault:
        check_injection(fleet, fault, robot_id)
    robots = [new_robot(r["id"], rng, last_reading(client, r["id"])) for r in fleet]

    n = 0
    while ticks is None or n < ticks:
        n += 1
        if fault and n == after + 1:
            inject(client, next(r for r in robots if r.id == robot_id), fault)
            log.warning("tick %d: injected %s on robot %d", n, fault, robot_id)
        for reading in tick(robots, rng):
            post_reading(client, reading)
        log.info("tick %d | %s", n, " | ".join(describe(r) for r in robots))
        if interval:
            time.sleep(interval)
    return robots


# ---------- Command line ----------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate the robot fleet and inject faults.")
    parser.add_argument("--inject", choices=sorted(FAULTS), help="fault to inject")
    parser.add_argument("--robot", type=int, help="id of the robot that gets the fault")
    parser.add_argument("--after", type=int, default=3, help="healthy ticks before the fault")
    parser.add_argument("--ticks", type=int, help="stop after N ticks (default: run forever)")
    parser.add_argument("--interval", type=float, default=2.0, help="seconds between ticks")
    parser.add_argument("--seed", type=int, help="random seed for a repeatable run")
    parser.add_argument("--fleet-url", default=os.getenv("FLEET_API_URL", "http://localhost:8001"))
    args = parser.parse_args(argv)
    if (args.inject is None) != (args.robot is None):
        parser.error("--inject and --robot must be used together")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # httpx logs every request at INFO
    try:
        with httpx.Client(base_url=args.fleet_url, timeout=5.0) as client:
            run(client, args.inject, args.robot, args.after, args.ticks, args.interval, args.seed)
    except SimulatorError as exc:
        log.error("error: %s", exc)
        return 2
    except httpx.HTTPError as exc:
        log.error("fleet_api request failed: %s", exc)
        return 1
    except KeyboardInterrupt:
        log.info("simulator stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
