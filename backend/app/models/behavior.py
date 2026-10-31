from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from psycopg.types.json import Json

from app.core.db import get_conn

COLUMNS = (
    "id",
    "time_on_page_ms",
    "return_count",
    "buttons_clicked",
    "cursor_hovers",
    "user_agent",
    "language",
    "timezone",
    "screen_width",
    "screen_height",
    "referrer",
    "page_url",
    "tech",
)


@dataclass
class Behavior:
    """
    CREATE TABLE IF NOT EXISTS behaviors (
        id               INTEGER PRIMARY KEY REFERENCES leads(id) ON DELETE CASCADE,
        time_on_page_ms  INTEGER NOT NULL DEFAULT 0,
        return_count     INTEGER NOT NULL DEFAULT 0,
        buttons_clicked  JSONB NOT NULL DEFAULT '[]'::jsonb,
        cursor_hovers    JSONB NOT NULL DEFAULT '[]'::jsonb,
        user_agent       TEXT NOT NULL DEFAULT '',
        language         TEXT NOT NULL DEFAULT '',
        timezone         TEXT NOT NULL DEFAULT '',
        screen_width     INTEGER,
        screen_height    INTEGER,
        referrer         TEXT NOT NULL DEFAULT '',
        page_url         TEXT NOT NULL DEFAULT '',
        tech             JSONB NOT NULL DEFAULT '{}'::jsonb,
        created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: int | None = None
    time_on_page_ms: int = 0
    return_count: int = 0
    buttons_clicked: list | dict | None = None
    cursor_hovers: list | dict | None = None
    user_agent: str = ""
    language: str = ""
    timezone: str = ""
    screen_width: int | None = None
    screen_height: int | None = None
    referrer: str = ""
    page_url: str = ""
    tech: dict | None = None
    created_at: Any = None


class BehaviorCRUD:
    @staticmethod
    def _payload(data: dict[str, Any], lead_id: int | None = None) -> dict[str, Any]:
        payload = {
            "time_on_page_ms": int(data.get("time_on_page_ms") or 0),
            "return_count": int(data.get("return_count") or 0),
            "buttons_clicked": Json(data.get("buttons_clicked") or []),
            "cursor_hovers": Json(data.get("cursor_hovers") or []),
            "user_agent": data.get("user_agent") or "",
            "language": data.get("language") or "",
            "timezone": data.get("timezone") or "",
            "screen_width": data.get("screen_width"),
            "screen_height": data.get("screen_height"),
            "referrer": data.get("referrer") or "",
            "page_url": data.get("page_url") or "",
            "tech": Json(data.get("tech") or {}),
        }
        if lead_id is not None:
            payload["id"] = lead_id
        elif data.get("id") is not None:
            payload["id"] = data["id"]
        return payload

    @staticmethod
    def create(data: dict[str, Any], lead_id: int | None = None) -> dict[str, Any]:
        payload = BehaviorCRUD._payload(data, lead_id)
        if "id" not in payload:
            raise ValueError("нужен id заявки для связи 1:1")
        names = ", ".join(COLUMNS)
        placeholders = ", ".join(f"%({key})s" for key in COLUMNS)
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO behaviors ({names}) VALUES ({placeholders}) RETURNING *",
                payload,
            )
            row = cur.fetchone()
        return dict(row)

    @staticmethod
    def get(lead_id: int) -> dict[str, Any] | None:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM behaviors WHERE id = %s", (lead_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    @staticmethod
    def list(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM behaviors ORDER BY id DESC LIMIT %s OFFSET %s",
                (limit, offset),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def update(lead_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        payload = BehaviorCRUD._payload(data, lead_id)
        payload.pop("id", None)
        assignments = ", ".join(f"{key} = %({key})s" for key in payload)
        payload["id"] = lead_id
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE behaviors SET {assignments} WHERE id = %(id)s RETURNING *",
                payload,
            )
            row = cur.fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete(lead_id: int) -> bool:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM behaviors WHERE id = %s RETURNING id", (lead_id,))
            row = cur.fetchone()
        return row is not None
