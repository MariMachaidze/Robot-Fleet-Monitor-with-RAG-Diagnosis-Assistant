"""SQLite storage for fleet_api: schema, seed data and a connection helper.

Uses the standard-library sqlite3 module with plain SQL (no ORM), so every query is
visible and easy to explain. CHECK constraints repeat the API's validation inside the
database, so bad data cannot get in even if someone bypasses the API.
"""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS robots (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    model    TEXT NOT NULL,
    firmware TEXT NOT NULL,
    status   TEXT NOT NULL CHECK (status IN ('idle', 'moving', 'stopped', 'charging', 'error'))
);

CREATE TABLE IF NOT EXISTS telemetry (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    robot_id   INTEGER NOT NULL REFERENCES robots(id),
    ts         TEXT NOT NULL,  -- ISO-8601 UTC, one fixed format so text order = time order
    x          REAL NOT NULL,
    y          REAL NOT NULL,
    battery    REAL NOT NULL CHECK (battery BETWEEN 0 AND 100),
    status     TEXT NOT NULL CHECK (status IN ('idle', 'moving', 'stopped', 'charging', 'error')),
    error_code TEXT
);
CREATE INDEX IF NOT EXISTS idx_telemetry_robot_ts ON telemetry (robot_id, ts);

-- Ground truth for evaluation. No GET endpoint exposes this table, so the assistant
-- has to diagnose from telemetry and manuals instead of reading the answer.
CREATE TABLE IF NOT EXISTS fault_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    robot_id   INTEGER NOT NULL REFERENCES robots(id),
    ts         TEXT NOT NULL,
    fault      TEXT NOT NULL,
    true_cause TEXT NOT NULL
);
"""

# (id, name, model, firmware, status)
SEED_ROBOTS = [
    (1, "Atlas", "AMR-100", "1.4", "idle"),
    (2, "Bolt", "AMR-100", "1.4", "idle"),
    (3, "Comet", "AMR-200", "2.0", "idle"),
]


def connect(db_path: str) -> sqlite3.Connection:
    """Open a connection that returns rows as dict-like objects and enforces foreign keys."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False: FastAPI may open the connection (in a dependency) and use it
    # (in the endpoint) on different worker threads. Each connection still serves only one
    # request at a time, so this is safe.
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite leaves foreign keys off by default
    return conn


def init_db(db_path: str) -> None:
    """Create the tables if needed and seed the 3 robots on first start."""
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM robots").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO robots (id, name, model, firmware, status) VALUES (?, ?, ?, ?, ?)",
                SEED_ROBOTS,
            )
        conn.commit()
    finally:
        conn.close()
