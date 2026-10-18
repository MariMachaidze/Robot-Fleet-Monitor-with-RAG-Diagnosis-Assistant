"""Pure simulation rules: robot state, healthy movement, and one behavior per fault.

There is no network code here, so every rule can be unit-tested by calling tick().
Positions are cells on a 10x10 grid, and aisle N is grid column x = N. Each robot's x and
y are what the robot believes and reports, which is why a sensor fault can make them jump.
"""

import random
from collections.abc import Callable
from dataclasses import dataclass

from fleet_api.faults import FAULTS

GRID_SIZE = 10
BATTERY_DRAIN = 0.5  # percent lost per tick in normal operation
CHARGE_RATE = 5.0  # percent gained per tick while charging
LOW_BATTERY = 20.0  # a healthy robot starts charging below this level
DEAD_ZONE_AISLE = 7  # comms_loss: the Wi-Fi dead zone is in aisle 7
SILENT_TICKS = 10  # comms_loss: ticks without telemetry before the robot reconnects

Cell = tuple[int, int]


@dataclass
class RobotState:
    id: int
    x: int
    y: int
    battery: float
    goal: Cell
    status: str = "idle"
    error_code: str | None = None
    fault: str | None = None
    fault_ticks: int = 0  # ticks since the fault started
    silent_ticks: int = 0  # comms_loss: ticks without telemetry so far
    silent: bool = False  # True when this tick's reading never reaches fleet_api


# ---------- Small helpers ----------


def random_cell(rng: random.Random) -> Cell:
    return rng.randrange(GRID_SIZE), rng.randrange(GRID_SIZE)


def drain(r: RobotState, factor: float = 1.0) -> None:
    r.battery = max(0.0, r.battery - BATTERY_DRAIN * factor)


def step_toward(r: RobotState, target: Cell) -> None:
    """Move one cell toward target: along x first, then along y."""
    if r.x != target[0]:
        r.x += 1 if target[0] > r.x else -1
    elif r.y != target[1]:
        r.y += 1 if target[1] > r.y else -1


def wander(r: RobotState, rng: random.Random) -> None:
    """Drive one cell toward the goal. On arrival, idle for a tick and pick a new goal."""
    if (r.x, r.y) == r.goal:
        r.status = "idle"
        r.goal = random_cell(rng)
    else:
        step_toward(r, r.goal)
        r.status = "moving"


def jump(r: RobotState, rng: random.Random, min_cells: int, max_cells: int) -> None:
    """Teleport the reported position to a random cell min_cells..max_cells away."""
    candidates = [
        (x, y)
        for x in range(GRID_SIZE)
        for y in range(GRID_SIZE)
        if min_cells <= max(abs(x - r.x), abs(y - r.y)) <= max_cells
    ]
    r.x, r.y = rng.choice(candidates)


def fault_code(r: RobotState) -> str:
    """The error code of the robot's active fault, taken from the shared fault catalog."""
    return FAULTS[r.fault].error_code


def new_robot(robot_id: int, rng: random.Random, last_reading: dict | None = None) -> RobotState:
    """Create a robot, resuming from its last reading so a restart does not teleport it
    or refill its battery. Without history it starts on a random cell."""
    if last_reading:
        x = min(max(round(last_reading["x"]), 0), GRID_SIZE - 1)
        y = min(max(round(last_reading["y"]), 0), GRID_SIZE - 1)
        battery = last_reading["battery"]
    else:
        (x, y), battery = random_cell(rng), round(rng.uniform(60, 100), 1)
    return RobotState(id=robot_id, x=x, y=y, battery=battery, goal=random_cell(rng))


# ---------- Normal behavior ----------


def healthy_tick(r: RobotState, rng: random.Random) -> None:
    """Normal operation: drive toward a goal, and charge when the battery runs low."""
    if r.status == "charging":
        r.battery = min(100.0, r.battery + CHARGE_RATE)
        if r.battery >= 100.0:
            r.status = "idle"
        return
    drain(r)
    if r.battery < LOW_BATTERY:
        r.status = "charging"  # simplification: robots charge where they stand
        return
    wander(r, rng)


# ---------- Fault behaviors: each one replaces the robot's normal tick ----------


def battery_drain(r: RobotState, rng: random.Random) -> None:
    """Degraded cell: the battery drains 16x faster while driving; below 10% the robot stops."""
    if r.battery >= 10:
        drain(r, factor=16)
        wander(r, rng)
    else:
        drain(r)
    if r.battery < 10:
        r.status, r.error_code = "stopped", fault_code(r)


def blocked_path(r: RobotState, rng: random.Random) -> None:
    """Obstacle in the aisle: the robot cannot move. It waits, then gives up after 5 ticks."""
    drain(r)
    if r.fault_ticks >= 5:
        r.status, r.error_code = "stopped", fault_code(r)
    else:
        r.status = "moving"  # still trying to drive, but the position does not change


def lidar_dropout(r: RobotState, rng: random.Random) -> None:
    """Loose lidar cable: without lidar the robot loses its position fix, halts with an
    error, and the position it reports jumps around by 2 to 3 cells."""
    drain(r)
    jump(r, rng, 2, 3)
    r.status, r.error_code = "error", fault_code(r)


def wheel_stall(r: RobotState, rng: random.Random) -> None:
    """Stalled wheel motor: the robot cannot move, but the stalled motor still draws
    current, so the battery falls 3x faster."""
    drain(r, factor=3)
    r.status, r.error_code = "stopped", fault_code(r)


def localization_drift(r: RobotState, rng: random.Random) -> None:
    """Map mismatch (firmware 2.0): the position estimate jumps more than 3 cells once,
    then the robot keeps driving on the wrong map and reports E57 on every reading."""
    drain(r)
    if r.fault_ticks == 1:
        jump(r, rng, 4, GRID_SIZE)
        r.status = "moving"
    else:
        wander(r, rng)
    r.error_code = fault_code(r)


def comms_loss(r: RobotState, rng: random.Random) -> None:
    """Wi-Fi dead zone: the robot drives into aisle 7 and halts there. Its readings are
    lost for 10 ticks, then it reconnects and reports E60."""
    drain(r)
    if r.x != DEAD_ZONE_AISLE:
        step_toward(r, (DEAD_ZONE_AISLE, r.y))
        r.status = "moving"
        return
    r.status = "stopped"  # robots halt when they lose the link to the fleet manager
    r.silent = r.silent_ticks < SILENT_TICKS
    if r.silent:
        r.silent_ticks += 1
    else:
        r.error_code = fault_code(r)


FaultBehavior = Callable[[RobotState, random.Random], None]

FAULT_BEHAVIORS: dict[str, FaultBehavior] = {
    "battery_drain": battery_drain,
    "blocked_path": blocked_path,
    "lidar_dropout": lidar_dropout,
    "wheel_stall": wheel_stall,
    "localization_drift": localization_drift,
    "comms_loss": comms_loss,
}


# ---------- One simulation step ----------


def start_fault(r: RobotState, fault: str) -> None:
    r.fault, r.fault_ticks = fault, 0


def to_reading(r: RobotState) -> dict:
    """The JSON body for POST /telemetry."""
    return {
        "robot_id": r.id,
        "x": r.x,
        "y": r.y,
        "battery": round(r.battery, 1),
        "status": r.status,
        "error_code": r.error_code,
    }


def tick(robots: list[RobotState], rng: random.Random) -> list[dict]:
    """Advance every robot by one tick and return the readings that reach fleet_api."""
    readings = []
    for r in robots:
        if r.fault:
            r.fault_ticks += 1
            FAULT_BEHAVIORS[r.fault](r, rng)
        else:
            healthy_tick(r, rng)
        if not r.silent:
            readings.append(to_reading(r))
    return readings
