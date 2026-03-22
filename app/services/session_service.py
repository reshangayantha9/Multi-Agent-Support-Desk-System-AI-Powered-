from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session as SessionModel

logger = logging.getLogger(__name__)


async def load_session(db: AsyncSession, session_id: str) -> dict[str, Any]:
    logger.debug(f"[SESSION][LOAD] session_id={session_id}")
    stmt = select(SessionModel).where(SessionModel.session_id == session_id)
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        return {"chat_history": [], "created_ticket_ids": []}
    return row.memory_json or {"chat_history": [], "created_ticket_ids": []}


async def save_session(
    db: AsyncSession,
    session_id: str,
    state: dict[str, Any],
    last_ticket_id: Optional[str] = None,
) -> None:
    logger.debug(
        f"[SESSION][SAVE] session_id={session_id} | "
        f"history_len={len(state.get('chat_history', []))} | "
        f"last_ticket={last_ticket_id}"
    )
    stmt = select(SessionModel).where(SessionModel.session_id == session_id)
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()

    if row is None:
        row = SessionModel(session_id=session_id)
        db.add(row)

    row.memory_json = state
    if last_ticket_id:
        row.last_ticket_id = last_ticket_id

    await db.commit()
