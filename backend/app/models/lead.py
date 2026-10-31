from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any

from app.core.db import get_conn

COLUMNS = (
    "last_name",
    "first_name",
    "patronymic",
    "phone",
    "email",
    "make",
    "model",
    "year",
    "vehicle_details",
    "service",
    "work_type",
    "work_area",
    "visit_format",
    "booked_by",
    "needed_by",
    "budget",
    "preferred_contact",
    "convenient_time",
    "comments",
)


@dataclass
class Lead:
    """
    CREATE TABLE IF NOT EXISTS leads (
        id                 SERIAL PRIMARY KEY,
        last_name          TEXT NOT NULL DEFAULT '',
        first_name         TEXT NOT NULL DEFAULT '',
        patronymic         TEXT NOT NULL DEFAULT '',
        phone              TEXT NOT NULL DEFAULT '',
        email              TEXT NOT NULL DEFAULT '',
        make               TEXT NOT NULL DEFAULT '',
        model              TEXT NOT NULL DEFAULT '',
        year               TEXT NOT NULL DEFAULT '',
        vehicle_details    TEXT NOT NULL DEFAULT '',
        service            TEXT NOT NULL DEFAULT '',
        work_type          TEXT NOT NULL DEFAULT '',
        work_area          TEXT NOT NULL DEFAULT '',
        visit_format       TEXT NOT NULL DEFAULT '',
        booked_by          TEXT NOT NULL DEFAULT '',
        needed_by          TEXT NOT NULL DEFAULT '',
        budget             TEXT NOT NULL DEFAULT '',
        preferred_contact  TEXT NOT NULL DEFAULT '',
        convenient_time    TEXT NOT NULL DEFAULT '',
        comments           TEXT NOT NULL DEFAULT '',
        created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: int | None = None
    last_name: str = ""
    first_name: str = ""
    patronymic: str = ""
    phone: str = ""
    email: str = ""
    make: str = ""
    model: str = ""
    year: str = ""
    vehicle_details: str = ""
    service: str = ""
    work_type: str = ""
    work_area: str = ""
    visit_format: str = ""
    booked_by: str = ""
    needed_by: str = ""
    budget: str = ""
    preferred_contact: str = ""
    convenient_time: str = ""
    comments: str = ""
    created_at: Any = None


class LeadCRUD:
    @staticmethod
    def _payload(data: dict[str, Any]) -> dict[str, Any]:
        allowed = {item.name for item in fields(Lead)} - {"id", "created_at"}
        return {key: data.get(key, "") for key in COLUMNS if key in allowed}

    @staticmethod
    def create(data: dict[str, Any]) -> dict[str, Any]:
        payload = LeadCRUD._payload(data)
        placeholders = ", ".join(f"%({key})s" for key in COLUMNS)
        names = ", ".join(COLUMNS)
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO leads ({names}) VALUES ({placeholders}) RETURNING *",
                payload,
            )
            row = cur.fetchone()
        return dict(row)

    @staticmethod
    def get(lead_id: int) -> dict[str, Any] | None:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM leads WHERE id = %s", (lead_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    @staticmethod
    def list(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM leads ORDER BY id DESC LIMIT %s OFFSET %s",
                (limit, offset),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def update(lead_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        payload = {key: value for key, value in LeadCRUD._payload(data).items() if key in data}
        if not payload:
            return LeadCRUD.get(lead_id)
        assignments = ", ".join(f"{key} = %({key})s" for key in payload)
        payload["id"] = lead_id
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE leads SET {assignments} WHERE id = %(id)s RETURNING *",
                payload,
            )
            row = cur.fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete(lead_id: int) -> bool:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM leads WHERE id = %s RETURNING id", (lead_id,))
            row = cur.fetchone()
        return row is not None

    @staticmethod
    def as_dict(lead: Lead) -> dict[str, Any]:
        return asdict(lead)
