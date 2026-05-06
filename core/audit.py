import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core.config import AUDIT_DB, MODEL_VERSION

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    model_version TEXT,
    bidder_id TEXT,
    criterion_id TEXT,
    payload_json TEXT
);
"""


def _conn() -> sqlite3.Connection:
    Path(AUDIT_DB).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(AUDIT_DB)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


def log(action: str, actor: str = "system", **fields) -> int:
    ts = datetime.now(timezone.utc).isoformat()
    model_version = fields.pop("model_version", MODEL_VERSION)
    bidder_id = fields.pop("bidder_id", None)
    criterion_id = fields.pop("criterion_id", None)
    payload_json = json.dumps(fields) if fields else None

    conn = _conn()
    cur = conn.execute(
        "INSERT INTO audit_log (ts, action, actor, model_version, bidder_id, criterion_id, payload_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ts, action, actor, model_version, bidder_id, criterion_id, payload_json),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def clear() -> None:
    conn = _conn()
    conn.execute("DELETE FROM audit_log")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='audit_log'")
    conn.commit()
    conn.close()


def query(filters: dict | None = None) -> list[dict]:
    conn = _conn()
    sql = "SELECT * FROM audit_log"
    params: list = []
    if filters:
        clauses = []
        if "bidder_id" in filters:
            clauses.append("bidder_id = ?")
            params.append(filters["bidder_id"])
        if "action" in filters:
            clauses.append("action = ?")
            params.append(filters["action"])
        if "date_from" in filters:
            clauses.append("ts >= ?")
            params.append(filters["date_from"])
        if "date_to" in filters:
            clauses.append("ts <= ?")
            params.append(filters["date_to"])
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
