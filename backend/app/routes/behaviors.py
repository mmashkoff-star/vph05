from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.behavior import BehaviorCRUD
from app.models.lead import LeadCRUD

router = APIRouter(prefix="/behaviors", tags=["behaviors"])


class BehaviorIn(BaseModel):
    id: int | None = None
    time_on_page_ms: int = 0
    return_count: int = 0
    buttons_clicked: list[Any] = Field(default_factory=list)
    cursor_hovers: list[Any] = Field(default_factory=list)
    user_agent: str = ""
    language: str = ""
    timezone: str = ""
    screen_width: int | None = None
    screen_height: int | None = None
    referrer: str = ""
    page_url: str = ""
    tech: dict[str, Any] = Field(default_factory=dict)


@router.post("")
def create_behavior(data: BehaviorIn) -> dict[str, Any]:
    lead_id = data.id
    if lead_id is None:
        raise HTTPException(status_code=400, detail="нужен id заявки")
    if LeadCRUD.get(lead_id) is None:
        raise HTTPException(status_code=404, detail="заявка не найдена")
    if BehaviorCRUD.get(lead_id) is not None:
        raise HTTPException(status_code=409, detail="метрики для этой заявки уже есть")
    return BehaviorCRUD.create(data.model_dump(), lead_id=lead_id)


@router.get("")
def list_behaviors(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    return BehaviorCRUD.list(limit=limit, offset=offset)


@router.get("/{lead_id}")
def get_behavior(lead_id: int) -> dict[str, Any]:
    row = BehaviorCRUD.get(lead_id)
    if row is None:
        raise HTTPException(status_code=404, detail="метрики не найдены")
    return row


@router.patch("/{lead_id}")
def update_behavior(lead_id: int, data: BehaviorIn) -> dict[str, Any]:
    row = BehaviorCRUD.update(lead_id, data.model_dump(exclude_unset=True))
    if row is None:
        raise HTTPException(status_code=404, detail="метрики не найдены")
    return row


@router.delete("/{lead_id}")
def delete_behavior(lead_id: int) -> dict[str, bool]:
    if not BehaviorCRUD.delete(lead_id):
        raise HTTPException(status_code=404, detail="метрики не найдены")
    return {"ok": True}
