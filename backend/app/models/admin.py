from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from psycopg.types.json import Json

from app.core.db import get_conn

DEFAULT_SERVICES = [
    {
        "key": "diagnostics",
        "title": "Диагностика и ТО",
        "description": "Дилерский регламент для Porsche, Bentley, Mercedes-Maybach, Rolls-Royce",
    },
    {
        "key": "detailing",
        "title": "Детейлинг и керамика",
        "description": "Полировка, покрытие кузова, уход за ЛКП без компромиссов",
    },
    {
        "key": "ppf",
        "title": "Антигравий PPF",
        "description": "Оклейка полиуретаном зон риска или всего кузова",
    },
    {
        "key": "body",
        "title": "Кузов и цвет",
        "description": "Локальный ремонт, подбор эмали, сохранение заводской фактуры",
    },
    {
        "key": "interior",
        "title": "Салон и кожа",
        "description": "Реставрация кожи, алькантары, дерева и хрома",
    },
    {
        "key": "concierge",
        "title": "Сезонное сопровождение",
        "description": "Хранение, выдача, выезд мастера и персональный слот",
    },
]


@dataclass
class AdminSettings:
    """
    CREATE TABLE IF NOT EXISTS admin_settings (
        id           SERIAL PRIMARY KEY,
        services     JSONB NOT NULL DEFAULT '[]'::jsonb,
        budget_min   TEXT NOT NULL DEFAULT '50000',
        budget_max   TEXT NOT NULL DEFAULT '5000000',
        budget_step  TEXT NOT NULL DEFAULT '50000',
        updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: int | None = None
    services: list | None = None
    budget_min: str = "200000"
    budget_max: str = "6000000"
    budget_step: str = "50000"
    updated_at: Any = None


class AdminCRUD:
    @staticmethod
    def _payload(data: dict[str, Any]) -> dict[str, Any]:
        return {
            "services": Json(data.get("services") or DEFAULT_SERVICES),
            "budget_min": str(data.get("budget_min") or "200000"),
            "budget_max": str(data.get("budget_max") or "6000000"),
            "budget_step": str(data.get("budget_step") or "50000"),
        }

    @staticmethod
    def ensure_default(conn: Any | None = None) -> dict[str, Any]:
        def _run(cur: Any) -> dict[str, Any]:
            cur.execute("SELECT * FROM admin_settings ORDER BY id ASC LIMIT 1")
            row = cur.fetchone()
            if row:
                return dict(row)
            payload = AdminCRUD._payload({})
            cur.execute(
                """
                INSERT INTO admin_settings (services, budget_min, budget_max, budget_step)
                VALUES (%(services)s, %(budget_min)s, %(budget_max)s, %(budget_step)s)
                RETURNING *
                """,
                payload,
            )
            return dict(cur.fetchone())

        if conn is not None:
            with conn.cursor() as cur:
                return _run(cur)
        with get_conn() as owned, owned.cursor() as cur:
            return _run(cur)

    @staticmethod
    def create(data: dict[str, Any]) -> dict[str, Any]:
        payload = AdminCRUD._payload(data)
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO admin_settings (services, budget_min, budget_max, budget_step)
                VALUES (%(services)s, %(budget_min)s, %(budget_max)s, %(budget_step)s)
                RETURNING *
                """,
                payload,
            )
            row = cur.fetchone()
        return dict(row)

    @staticmethod
    def get(settings_id: int) -> dict[str, Any] | None:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM admin_settings WHERE id = %s", (settings_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_current() -> dict[str, Any] | None:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM admin_settings ORDER BY id ASC LIMIT 1")
            row = cur.fetchone()
        return dict(row) if row else None

    @staticmethod
    def list(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM admin_settings ORDER BY id ASC LIMIT %s OFFSET %s",
                (limit, offset),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def update(settings_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        current = AdminCRUD.get(settings_id)
        if current is None:
            return None
        merged = {
            "services": data.get("services", current["services"]),
            "budget_min": data.get("budget_min", current["budget_min"]),
            "budget_max": data.get("budget_max", current["budget_max"]),
            "budget_step": data.get("budget_step", current["budget_step"]),
        }
        payload = AdminCRUD._payload(merged)
        payload["id"] = settings_id
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE admin_settings
                SET services = %(services)s,
                    budget_min = %(budget_min)s,
                    budget_max = %(budget_max)s,
                    budget_step = %(budget_step)s,
                    updated_at = NOW()
                WHERE id = %(id)s
                RETURNING *
                """,
                payload,
            )
            row = cur.fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete(settings_id: int) -> bool:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM admin_settings WHERE id = %s RETURNING id", (settings_id,))
            row = cur.fetchone()
        return row is not None
