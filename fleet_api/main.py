"""fleet_api HTTP service (port 8001): robots, telemetry and fault injection.

Run locally:  uvicorn fleet_api.main:app --port 8001
Interactive API docs: http://localhost:8001/docs
"""

import os
import sqlite3
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from fleet_api import db
from fleet_api.faults import FAULTS

RobotStatus = Literal["idle", "moving", "stopped", "charging", "error"]


# ---------- Request and response models ----------


class Robot(BaseModel):
    id: int
    name: str
    model: str
    firmware: str
    status: RobotStatus


class TelemetryIn(BaseModel):
    robot_id: int
    x: float
    y: float
    battery: float = Field(ge=0, le=100, description="Battery level in percent")
    status: RobotStatus
    error_code: str | None = Field(default=None, max_length=10, examples=["E42"])
    ts: datetime | None = Field(
        default=None, description="Reading time; defaults to server time. Naive values = UTC."
    )


class Telemetry(BaseModel):
    id: int
    robot_id: int
    ts: str
    x: float
    y: float
    battery: float
    status: RobotStatus
    error_code: str | None


class FaultInjectIn(BaseModel):
    robot_id: int
    fault: str = Field(examples=["wheel_stall"], description=f"One of: {', '.join(FAULTS)}")


class FaultLogEntry(BaseModel):
    id: int
    robot_id: int
    ts: str
    fault: str
    true_cause: str


# ---------- Helpers ----------


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: one short-lived connection per request, always closed."""
    conn = db.connect(request.app.state.db_path)
    try:
        yield conn
    finally:
        conn.close()


DB = Annotated[sqlite3.Connection, Depends(get_db)]


def utc_iso(ts: datetime | None = None) -> str:
    """Format a timestamp as ISO-8601 UTC in one fixed format, so stored text sorts by time."""
    ts = ts or datetime.now(UTC)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)  # treat naive timestamps as UTC, not server-local time
    return ts.astimezone(UTC).isoformat(timespec="seconds")


def fetch_robot(conn: sqlite3.Connection, robot_id: int) -> sqlite3.Row:
    """Return the robot row or raise 404, so every endpoint handles unknown ids the same way."""
    row = conn.execute("SELECT * FROM robots WHERE id = ?", (robot_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Robot {robot_id} not found")
    return row


# ---------- Endpoints ----------

router = APIRouter()


@router.get("/health")
def health(conn: DB) -> dict[str, str]:
    conn.execute("SELECT 1")  # proves the database is reachable, not just the process
    return {"status": "ok", "service": "fleet_api"}


@router.get("/robots")
def list_robots(conn: DB) -> list[Robot]:
    return [Robot(**row) for row in conn.execute("SELECT * FROM robots ORDER BY id")]


@router.get("/robots/{robot_id}")
def get_robot(robot_id: int, conn: DB) -> Robot:
    return Robot(**fetch_robot(conn, robot_id))


@router.get("/robots/{robot_id}/telemetry")
def get_telemetry(
    robot_id: int, conn: DB, limit: Annotated[int, Query(ge=1, le=500)] = 20
) -> list[Telemetry]:
    """Most recent readings first."""
    fetch_robot(conn, robot_id)
    rows = conn.execute(
        "SELECT * FROM telemetry WHERE robot_id = ? ORDER BY ts DESC, id DESC LIMIT ?",
        (robot_id, limit),
    )
    return [Telemetry(**row) for row in rows]


@router.post("/telemetry", status_code=201)
def post_telemetry(reading: TelemetryIn, conn: DB) -> Telemetry:
    fetch_robot(conn, reading.robot_id)
    ts = utc_iso(reading.ts)
    cur = conn.execute(
        "INSERT INTO telemetry (robot_id, ts, x, y, battery, status, error_code)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            reading.robot_id,
            ts,
            reading.x,
            reading.y,
            reading.battery,
            reading.status,
            reading.error_code,
        ),
    )
    # Keep robots.status equal to the latest reading, so GET /robots shows the live state.
    conn.execute("UPDATE robots SET status = ? WHERE id = ?", (reading.status, reading.robot_id))
    conn.commit()
    return Telemetry(id=cur.lastrowid, ts=ts, **reading.model_dump(exclude={"ts"}))


@router.post("/faults/inject", status_code=201)
def inject_fault(body: FaultInjectIn, conn: DB) -> FaultLogEntry:
    """Record that a fault was injected, with its true cause (ground truth for evals).

    This endpoint only writes the fault_log row. The simulator produces the matching
    telemetry (status, error code, position) for the faulty robot.
    """
    robot = fetch_robot(conn, body.robot_id)
    spec = FAULTS.get(body.fault)
    if spec is None:
        raise HTTPException(
            status_code=422, detail=f"Unknown fault '{body.fault}'. Known: {', '.join(FAULTS)}"
        )
    if spec.firmware_only and robot["firmware"] != spec.firmware_only:
        raise HTTPException(
            status_code=422,
            detail=f"'{body.fault}' only occurs on firmware {spec.firmware_only}; "
            f"robot {robot['id']} runs {robot['firmware']}",
        )
    ts = utc_iso()
    cur = conn.execute(
        "INSERT INTO fault_log (robot_id, ts, fault, true_cause) VALUES (?, ?, ?, ?)",
        (body.robot_id, ts, body.fault, spec.true_cause),
    )
    conn.commit()
    return FaultLogEntry(
        id=cur.lastrowid,
        robot_id=body.robot_id,
        ts=ts,
        fault=body.fault,
        true_cause=spec.true_cause,
    )


# ---------- App factory ----------


def create_app(db_path: str | None = None) -> FastAPI:
    """Build the app. Tests pass a temporary db_path; the server reads FLEET_DB_PATH."""
    db_path = db_path or os.getenv("FLEET_DB_PATH", "data/fleet.db")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        db.init_db(db_path)  # create tables and seed robots before the first request
        yield

    app = FastAPI(title="fleet_api", description="Robot platform stand-in", lifespan=lifespan)
    app.state.db_path = db_path
    app.include_router(router)
    return app


app = create_app()
