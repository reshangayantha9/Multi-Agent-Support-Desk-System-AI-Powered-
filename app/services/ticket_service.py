from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Ticket, TicketNote
from app.db.schemas import TicketCreate, TicketPatch

logger = logging.getLogger(__name__)


async def create_ticket(db: AsyncSession, data: TicketCreate) -> Ticket:
    logger.info(
        f"[TICKET_SVC][CREATE] title='{data.title[:40]}...' | "
        f"severity={data.severity} | user_email={data.user_email}"
    )
    ticket = Ticket(
        title=data.title,
        description=data.description,
        severity=data.severity or "medium",
        user_email=data.user_email,
        metadata_=data.metadata,
        status="OPEN",
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket, ["notes"])
    logger.info(f"[TICKET_SVC][CREATED] ticket_id={ticket.id} | status={ticket.status}")
    return ticket


async def get_ticket(db: AsyncSession, ticket_id: str) -> Optional[Ticket]:
    logger.debug(f"[TICKET_SVC][GET] ticket_id={ticket_id}")
    stmt = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.notes))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_open_tickets(db: AsyncSession, limit: int = 5) -> list[Ticket]:
    stmt = (
        select(Ticket)
        .where(Ticket.status == "OPEN")
        .options(selectinload(Ticket.notes))
        .order_by(Ticket.created_at.asc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_tickets_by_status(db: AsyncSession, status: str, limit: int = 50) -> list[Ticket]:
    stmt = (
        select(Ticket)
        .where(Ticket.status == status.upper())
        .options(selectinload(Ticket.notes))
        .order_by(Ticket.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def patch_ticket(db: AsyncSession, ticket_id: str, patch: TicketPatch) -> Optional[Ticket]:
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        return None

    if patch.status is not None:
        ticket.status = patch.status.upper()
    if patch.owner is not None:
        ticket.owner = patch.owner
    if patch.severity is not None:
        ticket.severity = patch.severity
    if patch.category is not None:
        ticket.category = patch.category
    if patch.priority is not None:
        ticket.priority = patch.priority
    if patch.resolution is not None:
        ticket.resolution = patch.resolution

    if patch.notes:
        note = TicketNote(
            ticket_id=ticket_id,
            content=patch.notes,
            note_type="internal",
            created_by="triage-agent",
        )
        db.add(note)

    await db.commit()
    await db.refresh(ticket, ["notes"])
    return ticket

async def list_all_tickets(db: AsyncSession, limit: int = 50) -> list[Ticket]:
    logger.info(f"[TICKET_SVC][LIST_BY_STATUS] limit={limit}")
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.notes))
        .order_by(Ticket.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())