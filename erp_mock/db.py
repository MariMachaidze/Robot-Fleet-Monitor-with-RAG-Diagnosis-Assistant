"""SQLite storage for erp_mock: schema, seed data and a connection helper.

The spare-part seed is chosen to drive the demo and eval scenarios: the AMR-100 wheel
motor is out of stock with a 14-day lead time, while the AMR-200 one is in stock.
"""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS spare_parts (
    part_id          TEXT PRIMARY KEY,
    description      TEXT NOT NULL,
    compatible_model TEXT NOT NULL,
    stock            INTEGER NOT NULL CHECK (stock >= 0),
    location         TEXT NOT NULL,
    lead_time_days   INTEGER NOT NULL CHECK (lead_time_days >= 0)
);

CREATE TABLE IF NOT EXISTS maintenance_notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    robot_id    INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    priority    TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    status      TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'rejected')),
    created_at  TEXT NOT NULL
);
"""

# (part_id, description, compatible_model, stock, location, lead_time_days)
SEED_SPARE_PARTS = [
    ("SP-1001", "Wheel motor assembly", "AMR-100", 0, "Store A / Bin 12", 14),
    ("SP-1002", "Wheel motor assembly", "AMR-200", 3, "Store A / Bin 14", 7),
    ("SP-1003", "Wheel motor controller board", "AMR-200", 2, "Store A / Bin 15", 10),
    ("SP-1004", "Wheel encoder cable", "AMR-200", 6, "Store A / Bin 16", 5),
    ("SP-1005", "Lidar cable harness", "AMR-100", 5, "Store B / Bin 03", 5),
    ("SP-1006", "Lidar cable harness", "AMR-200", 4, "Store B / Bin 04", 5),
    ("SP-1007", "Lidar sensor unit", "AMR-100", 1, "Store B / Bin 01", 30),
    ("SP-1008", "Lidar sensor unit", "AMR-200", 1, "Store B / Bin 02", 30),
    ("SP-1009", "Battery pack 48V Li-ion", "AMR-100", 1, "Store C / Bin 01", 21),
    ("SP-1010", "Battery pack 48V Li-ion", "AMR-200", 2, "Store C / Bin 02", 21),
    ("SP-1011", "Drive wheel tyre, polyurethane", "AMR-100", 8, "Store A / Bin 20", 7),
    ("SP-1012", "Drive wheel tyre, polyurethane", "AMR-200", 8, "Store A / Bin 21", 7),
    ("SP-1013", "Charging contact plate", "AMR-100", 3, "Store C / Bin 05", 10),
    ("SP-1014", "Charging contact plate", "AMR-200", 3, "Store C / Bin 06", 10),
    ("SP-1015", "Wi-Fi antenna module", "AMR-100", 2, "Store D / Bin 02", 12),
    ("SP-1016", "Wi-Fi antenna module", "AMR-200", 2, "Store D / Bin 03", 12),
]


def connect(db_path: str) -> sqlite3.Connection:
    """Open a connection that returns rows as dict-like objects."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False: FastAPI may open and use the connection on different worker
    # threads. Each connection still serves only one request at a time.
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """Create the tables if needed and seed the spare-parts catalog on first start."""
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM spare_parts").fetchone()[0] == 0:
            conn.executemany("INSERT INTO spare_parts VALUES (?, ?, ?, ?, ?, ?)", SEED_SPARE_PARTS)
        conn.commit()
    finally:
        conn.close()
