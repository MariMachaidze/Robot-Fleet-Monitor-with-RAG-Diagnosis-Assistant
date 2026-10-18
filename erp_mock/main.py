"""erp_mock HTTP service (port 8002): spare parts and maintenance notifications.

A mock inspired by ERP systems, NOT a replica of any SAP API.

Run locally:  uvicorn erp_mock.main:app --port 8002
Interactive API docs: http://localhost:8002/docs
"""

import os
import sqlite3
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from erp_mock import db

Priority = Literal["low", "medium", "high"]
NotificationStatus = Literal["draft", "approved", "rejected"]


# ---------- Request and response models ----------


class SparePart(BaseModel):
    part_id: str
    description: str
    compatible_model: str
    stock: int
    location: str
    lead_time_days: int


class NotificationIn(BaseModel):
    """Request body for a new notification.

    There is deliberately no status field: a client cannot ask for anything but a draft.
    Unknown fields (such as "status": "approved") are ignored.
    """

    robot_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=4000)
    priority: Priority = "medium"


class Notification(BaseModel):
    id: int
    robot_id: int
    title: str
    description: str
    priority: Priority
    status: NotificationStatus
    created_at: str


# ---------- Helpers ----------


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: one short-lived connection per request, always closed."""
    conn = db.connect(request.app.state.db_path)
    try:
        yield conn
    finally:
        conn.close()


DB = Annotated[sqlite3.Connection, Depends(get_db)]


def fetch_notification(conn: sqlite3.Connection, notification_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM maintenance_notifications WHERE id = ?", (notification_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Notification {notification_id} not found")
    return row


# ---------- Endpoints ----------

router = APIRouter()


@router.get("/health")
def health(conn: DB) -> dict[str, str]:
    conn.execute("SELECT 1")  # proves the database is reachable, not just the process
    return {"status": "ok", "service": "erp_mock"}


@router.get("/spare-parts")
def search_spare_parts(
    conn: DB, compatible_model: str | None = None, q: str | None = None
) -> list[SparePart]:
    """Filter by exact model (case-insensitive) and/or free text.

    Every word of q must appear in the description or part id, so "wheel motor" matches
    "Wheel motor assembly". Empty parameters (?compatible_model=&q=) mean no filter.
    """
    clauses: list[str] = []
    params: list[str] = []
    if compatible_model and compatible_model.strip():
        clauses.append("compatible_model = ? COLLATE NOCASE")
        params.append(compatible_model.strip())
    for word in (q or "").split():
        clauses.append("(description LIKE ? OR part_id LIKE ?)")  # LIKE ignores ASCII case
        params += [f"%{word}%", f"%{word}%"]
    # Only fixed clause templates go into the SQL text; user input is always a bound parameter.
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = conn.execute(f"SELECT * FROM spare_parts {where} ORDER BY part_id", params)
    return [SparePart(**row) for row in rows]


@router.get("/maintenance-notifications")
def list_notifications(conn: DB) -> list[Notification]:
    """Newest first."""
    rows = conn.execute("SELECT * FROM maintenance_notifications ORDER BY id DESC")
    return [Notification(**row) for row in rows]


@router.post("/maintenance-notifications", status_code=201)
def create_notification(body: NotificationIn, conn: DB) -> Notification:
    """Always creates a DRAFT. Only the approve endpoint can change that."""
    created_at = datetime.now(UTC).isoformat(timespec="seconds")
    cur = conn.execute(
        "INSERT INTO maintenance_notifications"
        " (robot_id, title, description, priority, status, created_at)"
        " VALUES (?, ?, ?, ?, 'draft', ?)",
        (body.robot_id, body.title, body.description, body.priority, created_at),
    )
    conn.commit()
    return Notification(**fetch_notification(conn, cur.lastrowid))


@router.post("/maintenance-notifications/{notification_id}/approve")
def approve_notification(notification_id: int, conn: DB) -> Notification:
    """Move a notification from draft to approved. Anything else is refused with 409."""
    # One conditional UPDATE: the check and the change happen together, so two approvals
    # sent at the same moment cannot both succeed.
    cur = conn.execute(
        "UPDATE maintenance_notifications SET status = 'approved'"
        " WHERE id = ? AND status = 'draft'",
        (notification_id,),
    )
    conn.commit()
    row = fetch_notification(conn, notification_id)  # 404 if it does not exist
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=409,
            detail=f"Notification {notification_id} is '{row['status']}'; "
            "only drafts can be approved",
        )
    return Notification(**row)


# ---------- App factory ----------


def create_app(db_path: str | None = None) -> FastAPI:
    """Build the app. Tests pass a temporary db_path; the server reads ERP_DB_PATH."""
    db_path = db_path or os.getenv("ERP_DB_PATH", "data/erp.db")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        db.init_db(db_path)  # create tables and seed spare parts before the first request
        yield

    app = FastAPI(
        title="erp_mock",
        description="ERP-inspired mock for spare parts and maintenance notifications. "
        "Not a replica of any SAP API.",
        lifespan=lifespan,
    )
    app.state.db_path = db_path
    app.include_router(router)
    return app


app = create_app()
